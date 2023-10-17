from Compiler.GC.types import *
from Compiler.circuit import *
from Compiler.util import *
from Compiler.library import *
from Compiler.types import *
from decimal import *
from mpmath import *
from bitwise_sampler.ostack import *
from bitwise_sampler.noise_sampler import sampler

class laplace_sampler_direct(sampler):
    def __init__(self, args, queries=None) -> None:
        sampler.__init__(self, args, queries)
        p = exp(1 / self.t)
        M = self.r1 + self.r2
        self.r1 = self.r1 / M
        self.r2 = self.r2 / M
        self.k = int(ceil(math.log2(self.t * ((self.lambd + 1 - math.log2(self.r1) + math.log2(self.n)) - math.log2(1 + p)) * ln(2))))
        self.acc = int(ceil(self.lambd + math.log2((self.k+1) + math.log2(self.n) - math.log2(self.r2))))
        self.sbk = sbitint.get_type(self.k+1)

    def geometric(self, p):
        geo_bias = [self.decfrac2bin(p ** (2 ** i) / (1 + p ** (2 ** i))) for i in range(self.k)]
        sbit_acc = sbitint.get_type(self.acc)
        geo_bias = sbit_acc.Array(self.k)
        geo = Array(self.k, sbit)
        
        for i in range(self.k):
            geo_bias[i] = sbitint.get_type(self.acc).bit_compose(self.decfrac2bin(p ** (2 ** i) / (1 + p ** (2 ** i)))) 

        @for_range(self.k)
        def _(i):
            geo[i] = self.basic_bernoulli(geo_bias[i])

        return sbitint.get_type(self.k).bit_compose(geo)
    

    def discrete_laplace_direct(self, t):
        p = exp(-1 / t)
        geo = self.geometric(p).force_bit_decompose()
        geo.append(0)
        # increase the length of geo
        geo = self.sbk.bit_compose(geo)
        
        dlap_bias = sbitint.get_type(self.acc).bit_compose(self.decfrac2bin((1 - p) / (1 + p - 2 * exp(-(2 ** self.k + 1) / t))))
        ber = self.basic_bernoulli(dlap_bias)

        dlap = ber.if_else(0, geo + 1)
        sign = self.get_random()
        return sign, dlap

    def discrete_laplace_geo_direct(self, n=None, t=None):

        if t is None:
            t = self.t
        if n is None:
            n = self.n
        print('Discrete Laplace geo direct')
        print('n', n)
        print('t', t)
        print('lambda', self.lambd)
        print('k', self.k)
        print('acc:', self.acc)
        laps = Array(n, self.sbk)
        @for_range(n)
        def _(i):
            sign, dlap = self.discrete_laplace_direct(t)
            dlap = sign.if_else(dlap, -dlap)
            # print_ln("get dlap: %s", dlap.reveal())
            if self.plain_queries is not None:
                laps[i] = dlap + self.plain_queries[i]
            else:
                laps[i] = dlap
        return laps