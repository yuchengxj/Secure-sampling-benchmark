from Compiler.GC.types import *
from Compiler.circuit import *
from Compiler.util import *
from Compiler.library import *
from Compiler.types import *
from Compiler.types import _bitint
from decimal import *
from mpmath import *
from bitwise_sampler.ostack import *
from bitwise_sampler.laplace_sampler_ostack import laplace_sampler_ostack

class gauss_sampler_ostack(laplace_sampler_ostack):
    def __init__(self, args, queries=None) -> None:
        laplace_sampler_ostack.__init__(self, args, queries)

        # Calculate the allocation of security parameters
        M = self.r1 + self.r2 + self.r3 + self.r4
        self.r1, self.r2, self.r3, self.r4 = (
            self.r1 / M,
            self.r2 / M,
            self.r3 / M,
            self.r4 / M,
        )
        self.delta = args.delta
        self.sigma = args.sensitivity * math.sqrt(2 * ln(1.25 / self.delta)) / args.epsilon

        # Truncation error
        self.k = max(
            int(
                ceil(
                    math.log2(
                        sqrt(
                            2
                            * ln(2)
                            * (self.lambd - math.log2(self.r1) + math.log2(self.n))
                        )
                        * self.sigma
                        - 1
                    )
                )
            ),
            1,
        )
        self.N = (1 << self.k) + 1
        self.sbk = sbitint.get_type(self.k+1)

        
    def trial_times(self, n, p, delta):
        k1 = n / p
        k2 = (-log2(delta)) * log(2) / (2 * p**2)
        m = int(ceil(k1 + k2 / 2 + sqrt(k2**2 / 4 + k1 * k2)))
        return m

    def full_square(self, a):
        da = util.bit_decompose(a)
        bit_matrix = [[0 for i in range(len(da))] for j in range(len(da))]

        for i in range(len(da)):
            bit_matrix[i][i] = da[i]

        for i in range(len(da)):
            for j in range(i + 1, len(da)):
                bit_matrix[i][j] = bit_matrix[j][i] = da[i] & da[j]

        res = []
        res[0 : len(da)] = bit_matrix[0]
        for i in range(1, len(da)):
            res[i : i + len(da) + 1] = _bitint.bit_adder(
                res[i : i + len(da)], bit_matrix[i], 0, True
            )

        return sbitint.get_type(len(res)).bit_compose(res)

    def full_multiple(a, b):
        da = util.bit_decompose(a)
        db = util.bit_decompose(b)
        res = []
        if isinstance(b, int):
            idx = db.index(1)
            res[0:idx] = [sbit(0) for i in range(idx)]
            res[idx : idx + len(da)] = da
            for i in range(idx + 1, len(db)):
                if db[i] == 1:
                    res[i : i + len(da) + 1] = _bitint.bit_adder(
                        res[i : i + len(da)], da, 0, True
                    )
        else:
            res[0 : len(da)] = [da_bit & db[0] for da_bit in da]
            for i in range(1, len(db)):
                tmp = [da_bit & db[i] for da_bit in da]
                res[i : i + len(da) + 1] = _bitint.bit_adder(
                    res[i : i + len(da)], tmp, 0, True
                )
        return sbitint.get_type(len(res)).bit_compose(res)

    def exponential_bernoulli(self, du, coins, i):
        expber = 1
        length = len(du)
        for j in range(length):
            du_bit = du[j]
            ber = coins[i * length + j]
            expber &= ~(du_bit & ~ber)
        return expber

    def sample_exponential_coins(
        self, f, length, num_variable, m, g=None, q=None, u=None, v=None
    ):
        coins = Array(length * num_variable, sbit)
        sbit_acc = sbitint.get_type(self.acc)
        exp_bias = sbit_acc.Array(length)
        for i in range(length):
            exp_bias[i] = sbitint.get_type(self.acc).bit_compose(
                self.decfrac2bin(exp(-(2**i) / f))
            )
        @for_range(length)
        def _(j):
            bias = exp_bias[j]

            @for_range(m // g)
            def _(l):
                exps = self.ostack_bernoulli(u, g, bias, self.acc, -1)

                @for_range(g)
                def _(c):
                    coins[l * g * length + c * length + j] = exps[c]

            exps = self.ostack_bernoulli(v, q, bias, self.acc, -1)

            @for_range(q)
            def _(c):
                coins[m // g * g * length + c * length + j] = exps[c]

        return coins

    def discrete_gaussian_dlap_rejection_ostack(self):
        # Calculate t
        print("Discrete Gaussian Rejection ostack")

        if self.sigma >= 1:
            z = nint(self.sigma)
        else:
            z = 1 / ceil(1 / self.sigma)

        if z >= 1:
            t = self.sigma**2 / z
            f = 2 * self.sigma**2
        else:
            t = self.sigma**2 * (1 / z)
            f = 2 * self.sigma**2 * (1 / z) ** 2
        print("t: ", t)

        # Calculate m
        s1 = nsum(
            lambda x: exp(-(x**2) / (2 * self.sigma**2)),
            [-(self.N - 1), (self.N - 1)],
        )
        s2 = nsum(lambda x: exp(-abs(x) / t), [-(self.N - 1), (self.N - 1)])
        s3 = exp(-(self.sigma**2) / (2 * t**2))

        p = s1 / s2 * s3
        print("p:", p)

        p_ = p - (2 ** (-self.lambd))
        print('self.r4', self.r4)
        m = self.trial_times(self.n, p_, 2 ** (-self.lambd + math.log2(self.r4)))
        print("m:", m)

        if z >= 1:
            self.l = 2 * self.k
        else:
            self.l = 2 * (self.k + 1) + 2 * int(ceil(math.log2(1 / z)))

        c = self.k + 1 + self.l
        print("c:", c)

        d = 2 * (self.k + 1) + self.l

        # Calculate acc
        self.acc = int(
            ceil(self.lambd - math.log2(self.r2) + math.log2(d * self.n / p_))
        )

        # Calculate ostack g, u, q, v
        if self.periodic:
            g, q, u, v, num_AND, num_bit = self.optimal_g(
                m, self.r3, t="periodic", l=self.l
            )
        else:
            g, q, u, v, num_AND, num_bit = self.optimal_g(
                m, self.r3, t="non_periodic", l=self.l
            )

        self.acc = int(ceil(self.lambd + 2 + math.log2(d * self.n / p_)))
        signs, dlaps = self.discrete_laplace_geo_ostack(m, t, g, q, u, v, num_AND, num_bit, rejection=True)

        samples = sbitint.get_type(self.k + 1).Array(m)
        accepts = sbit.Array(m)

        dlap = dlaps[0]
        if z >= 1:
            x = abs(dlap - int(z))
            x = x.cast(x.n_bits - 1)
        else:    
            x = abs(self.full_multiple(dlap, int(1 / z)) - 1)
        r = self.full_square(x)

        if type(r) == sbit:
            du = [r]
        else:
            du = r.force_bit_decompose()
        coins = self.sample_exponential_coins(
            f, len(du), (m // g) * g + q, m, g, q, u, v
        )

        @for_range(m)
        def _f(i):
            dlap = dlaps[i]
            if z >= 1:
                x = abs(dlap - int(z))
                x = x.cast(x.n_bits - 1)
            else:
                x = abs(self.full_multiple(dlap, int(1 / z)) - 1)

            r = self.full_square(x)
            if type(r) == sbit:
                du = [r]
            else:
                du = r.force_bit_decompose()

            b = self.exponential_bernoulli(du, coins, i)

            samples[i] = signs[i].if_else(-dlap, dlap)
            accepts[i] = b

        out_list = Array(self.n, self.sbk)
        @for_range(self.n)
        def _(i):
            out_list[i] = self.sbk(0)
        for i in range(m):
            @if_((accepts[i].reveal()))
            def _():
                out_list[i%self.n] = samples[i]
        for i in range(self.n):
            print_ln(
                    "%s", out_list[i].reveal()
                )
        return out_list
        
                