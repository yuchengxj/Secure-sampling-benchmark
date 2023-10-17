from Compiler.GC.types import *
from Compiler.circuit import *
from Compiler.util import *
from Compiler.library import *
from Compiler.types import *
from decimal import *
from mpmath import *
from bitwise_sampler.ostack import *
from bitwise_sampler.laplace_sampler import laplace_sampler


class gauss_sampler(laplace_sampler):
    def __init__(self, args, queries=None) -> None:
        laplace_sampler.__init__(self, args, queries)
        self.sigma = args.sensitivity / args.epsilon
        self.k = max(int(ceil(math.log2(sqrt(2 * ln(2) * (self.lambd + 2 + math.log2(n))) * self.sigma - 1))), 1)
        
    def trial_times(n, p, delta):
        start = int(ceil(n / p))
        end = 3 * start
        k1 = n / p
        k2 = (-log2(delta)) * log(2) / (2 * p ** 2)
        m = int(ceil(k1 + k2 / 2 + sqrt(k2 ** 2 / 4 + k1 * k2)))
        return m
    
    def full_square(a):
        da = util.bit_decompose(a)
        bit_matrix = [[0 for i in range(len(da))] for j in range(len(da))]

        for i in range(len(da)):
            bit_matrix[i][i] = da[i]

        for i in range(len(da)):
            for j in range(i + 1, len(da)):
                bit_matrix[i][j] = bit_matrix[j][i] = da[i] & da[j]

        res = []
        res[0: len(da)] = bit_matrix[0]
        for i in range(1, len(da)):
            res[i: i + len(da) + 1] = _bitint.bit_adder(res[i: i + len(da)], bit_matrix[i], 0, True)

        return sbitint.get_type(len(res)).bit_compose(res)
    
    def full_multiple(a, b):
        da = util.bit_decompose(a)
        db = util.bit_decompose(b)
        res = []
        if isinstance(b, int):
            idx = db.index(1)
            res[0 : idx] = [ sbit(0) for i in range(idx) ]
            res[idx: idx + len(da)] = da
            for i in range(idx + 1, len(db)):
                if db[i] == 1:
                    res[i: i + len(da) + 1] = _bitint.bit_adder(res[i: i + len(da)], da, 0, True)
        else:
            res[0: len(da)] = [da_bit & db[0] for da_bit in da]
            for i in range(1, len(db)):
                tmp = [da_bit & db[i] for da_bit in da]
                res[i: i + len(da) + 1] = _bitint.bit_adder(res[i: i + len(da)], tmp, 0, True)
        return sbitint.get_type(len(res)).bit_compose(res)
    
    def exponential_bernoulli(self, u, f):
        if type(u) == sbit:
            du = [u]
        else:
            du = u.force_bit_decompose()
        
        exp_bias = [self.decfrac2bin(exp(-(2 ** i) / f)) for i in range(len(du))]

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
            self.t = self.sigma ** 2 / z
            f = 2 * self.sigma ** 2
        else:
            self.t = self.sigma ** 2 * (1/z) 
            f = 2 * self.sigma ** 2 * (1/z) ** 2
        print("t: ", t)

        s1 = nsum(lambda x: exp(-(x ** 2) / (2 * self.sigma ** 2)), [-(N - 1), (N - 1)])
        s2 = nsum(lambda x: exp(-abs(x) / t), [-(N - 1), (N - 1)])
        s3 = exp(-(self.sigma ** 2) / (2 * t ** 2))

        p = s1 / s2 * s3
        print('p:', p)

        p_ = p - (2 ** (-self.lambd))

        m = self.trial_times(self.n, p_, 2 ** (-self.lambd - 2))
        print('m:', m)

        if z >= 1:
            l = 2 * self.k
        else:
            l = 2 * (self.k + 1) + 2 * int(ceil(math.log2(1 / z)))

        c = self.k + 1 + l
        print('c:', c)

        d = 2 * (self.k + 1) + l

        self.acc = int(ceil(self.lambd + 2 + math.log2(d * self.n / p_)))
        print('acc:', self.acc)
        print('k:', self.k)
        bitnum = 1 + self.acc * c
        print('bitnum:', bitnum)
        if self.ostack:
            dlaps = self.discrete_laplace_geo_ostack(m, t)

        b_list = Array(m, cbit)

        @for_range(m)
        def f(i):
            if self.ostack:
                dlap = dlaps[i]
            else:
                sign, dlap = self.discrete_laplace_direct(t)
            if z >= 1:
                v = abs(dlap - int(z))
                v = v.cast(v.n_bits - 1)
            else:
                v = abs(self.full_multiple(dlap, int(1 / z)) - 1)

            u = self.full_square(v)
            b = self.exponential_bernoulli(u, f)
            b_list[i] = b.reveal()