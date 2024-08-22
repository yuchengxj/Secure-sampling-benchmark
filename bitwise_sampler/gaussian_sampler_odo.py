from Compiler.GC.types import *
from Compiler.circuit import *
from Compiler.util import *
from Compiler.library import *
from Compiler.types import *
from Compiler.types import _bitint
from decimal import *
from mpmath import *
from bitwise_sampler.ostack import *
from bitwise_sampler.laplace_sampler_odo import laplace_sampler_odo

class gauss_sampler(laplace_sampler_odo):
    def __init__(self, args, queries=None) -> None:
        laplace_sampler_odo.__init__(self, args, queries)
        self.delta = args.delta
        self.sigma = args.sensitivity * math.sqrt(2 * ln(1.25 / self.delta)) / args.epsilon
        self.k = max(
            int(
                ceil(
                    math.log2(
                        sqrt(2 * ln(2) * (self.lambd + 2 + math.log2(self.n)))
                        * self.sigma
                        - 1
                    )
                )
            ),
            1,
        )
        self.sbk = sbitint.get_type(self.k+1)

    def trial_times(self, n, p, delta):
        print(p)
        k1 = n / p
        k2 = (-log2(delta)) * log(2) / (2 * p**2)
        print('k2', k2)
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

    def full_multiple(self, a, b):
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

    def exponential_bernoulli(self, u, f):
        if type(u) == sbit:
            du = [u]
        else:
            du = u.force_bit_decompose()

        exp_bias = [self.decfrac2bin(exp(-(2**i) / f)) for i in range(len(du))]

        expber = 1
        for du_bit, bias in zip(du, exp_bias):
            expber &= ~(du_bit & ~self.basic_bernoulli(bias))
        return expber

    def discrete_gaussian_dlap_rejection(self):
        N = (1 << self.k) + 1
        if self.sigma >= 1:
            z = nint(self.sigma)
        else:
            z = 1 / ceil(1 / self.sigma)

        if z >= 1:
            self.t = self.sigma**2 / z
            f = 2 * self.sigma**2
        else:
            self.t = self.sigma**2 * (1 / z)
            f = 2 * self.sigma**2 * (1 / z) ** 2

        s1 = nsum(lambda x: exp(-(x**2) / (2 * self.sigma**2)), [-(N - 1), (N - 1)])
        s2 = nsum(lambda x: exp(-abs(x) / self.t), [-(N - 1), (N - 1)])
        s3 = exp(-(self.sigma**2) / (2 * self.t**2))

        p = s1 / s2 * s3
        print("p:", p)

        p_ = p - (2 ** (-self.lambd))

        m = self.trial_times(self.n, p_, 2 ** (-self.lambd - 2))
        print("m:", m)

        if z >= 1:
            l = 2 * self.k
        else:
            l = 2 * (self.k + 1) + 2 * int(ceil(math.log2(1 / z)))

        c = self.k + 1 + l
        print("c:", c)

        d = 2 * (self.k + 1) + l

        self.acc = int(ceil(self.lambd + 2 + math.log2(d * self.n / p_)))
        print("acc:", self.acc)
        print("k:", self.k)
        


        samples = sbitint.get_type(self.k + 1).Array(m)
        accepts = sbit.Array(m)
        @for_range(m)
        def f(i):
            sign, dlap = self.discrete_laplace_direct(self.t)
            if z >= 1:
                v = abs(dlap - int(z))
                v = v.cast(v.n_bits - 1)
            else:
                v = abs(self.full_multiple(dlap, int(1 / z)) - 1)

            u = self.full_square(v)
            accepts[i] = self.exponential_bernoulli(u, f)
            samples[i] = sign.if_else(dlap, -dlap)
            self.bit_count = m * ((self.k + 1) * self.acc + 1) + m * len(u.force_bit_decompose()) * self.acc

        out_list = sbitint.get_type(self.k + 1).Array(self.n)
        @for_range(self.n)
        def _(i):
            out_list[i] = self.sbk(0)
        for i in range(m):
            @if_((accepts[i].reveal()))
            def _():
                out_list[i%self.n] = samples[i]
        for i in range(m):
            out_list[i%self.n] = samples[i]
            print_ln("%s, %s", accepts[i].reveal(), samples[i].reveal())
        return out_list