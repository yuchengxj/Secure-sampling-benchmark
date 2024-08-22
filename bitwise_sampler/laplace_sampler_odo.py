from Compiler.GC.types import *
from Compiler.circuit import *
from Compiler.util import *
from Compiler.library import *
from Compiler.types import *
from decimal import *
from mpmath import *
from bitwise_sampler.ostack import *
from bitwise_sampler.basic_sampler import basic_sampler



class laplace_sampler_odo(basic_sampler):
    def __init__(self, args, queries=None) -> None:
        basic_sampler.__init__(self, args, queries)
        p = exp(1 / self.t)
        self.odo = args.odo
        M = self.r1 + self.r2
        self.r1 = self.r1 / M
        self.r2 = self.r2 / M
        self.k = int(ceil(math.log2(self.t * ((self.lambd + 1 - math.log2(self.r1) + math.log2(self.n)) - math.log2(1 + p)) * ln(2))))
        self.sbk = sbitint.get_type(self.k+1)
        self.acc = int(ceil(self.lambd + math.log2((self.k+1) + math.log2(self.n) - math.log2(self.r2))))
        
        

    def geometric(self, p, odo=2, input_random=None, d=0):
        geo_bias = [self.decfrac2bin(p ** (2 ** i) / (1 + p ** (2 ** i))) for i in range(self.k)]
        sbit_acc = sbitint.get_type(self.acc)
        geo_bias = sbit_acc.Array(self.k)
        geo = Array(self.k, sbit)
        
        for i in range(self.k):
            geo_bias[i] = sbitint.get_type(self.acc).bit_compose(self.decfrac2bin(p ** (2 ** i) / (1 + p ** (2 ** i)))) 

        if odo == 3:
            @for_range(self.k)
            def _(i):
                geo[i] = self.probabilistic_bernoulli(geo_bias[i], input_random, d)

        else:
            @for_range(self.k)
            def _(i):
                geo[i] = self.basic_bernoulli(geo_bias[i])

        return sbitint.get_type(self.k).bit_compose(geo)
    
    def discrete_laplace(self, n=None, t=None):
        dlap = None
        if self.odo == 1:
            # recursive bernoulli
            dlap = self.discrete_laplace_odo1(n, t)

        elif self.odo == 2:
            # brute force bernoulli
            dlap = self.discrete_laplace_odo2(n, t)

        elif self.odo == 3:
            # probabilistic bernoulli
            dlap = self.discrete_laplace_odo3(n, t)
        
        @for_range(self.n)
        def _(i):
            print_ln("%s", dlap[i].reveal())
        return dlap


    def discrete_laplace_odo1(self, n=None, t=None):
        if t is None:
            t = self.t
        if n is None:
            n = self.n
            
        r_acc = self.r2 / 2
        self.acc = int(ceil(self.lambd + math.log2((self.k+1) + math.log2(self.n) - math.log2(r_acc))))
        
        r_compare = self.r2 / 2
        k1 = 2 * self.n
        k2 = (
            (
                self.lambd
                + math.log2(self.n)
                + math.log2(self.k)
                - math.log2(r_compare)
            )
            * math.log(2)
            * 2
        )
        u = int(ceil(k1 + k2 / 2 + sqrt(k2**2 / 4 + k1 * k2)))

        p = exp(-1 / t)

        print("Discrete Laplace odo1")
        print("lambda", self.lambd)
        print("n", n)
        print("t", t)
        print("k", self.k)
        print("acc:", self.acc)
        print("p:", p)
        print("u:", u)


        sbit_acc = sbitint.get_type(self.acc)
        geo_bias = sbit_acc.Array(self.k)
        for i in range(self.k):
            geo_bias[i] = sbitint.get_type(self.acc).bit_compose(
                self.decfrac2bin(p ** (2**i) / (1 + p ** (2**i)))
            )
        coins = Array(self.k * n, sbit)
        @for_range(self.k)
        def _(j):
            bias = geo_bias[j]

            geos = self.recursive_bernoulli(u, n, bias, self.acc)

            @for_range(n)
            def _(c):
                coins[c * self.k + j] = geos[c]

        sbk = sbitint.get_type(self.k + 1)
        laps = Array(n, sbk)
        signs = Array(n, sbit)
        self.radnom_bit += n
        @for_range(n)
        def _(j):
            geo = coins.get_part(j * self.k, self.k)
            geo = sbitint.get_type(self.k).bit_compose(geo)

            if self.k != 1:
                geo = geo.force_bit_decompose()
            geo.append(0)
            geo = sbk.bit_compose(geo)
            dlap_bias = sbitint.get_type(self.acc).bit_compose(
                self.decfrac2bin((1 - p) / (1 + p - 2 * exp(-(2**self.k + 1) / t)))
            )
            ber = self.basic_bernoulli(dlap_bias)
            dlap = ber.if_else(0, geo + 1)
            signs[j] = self.get_random()
            laps[j] = dlap

        # if not rejection:
        #     @for_range(n)
        #     def _(j):
        #         laps[j] = signs[j].if_else(-laps[j], laps[j])
        #         # print_ln("%s get dlap: %s", j.reveal(), laps[j].reveal())
        #     return laps
        # else:
        #     return signs, laps
        @for_range(n)
        def _(j):
            laps[j] = signs[j].if_else(-laps[j], laps[j])
        return laps


    def discrete_laplace_odo2(self, n=None, t=None):
        if t is None:
            t = self.t
        if n is None:
            n = self.n
        print('Discrete Laplace odo2')
        print('n', n)
        print('t', t)
        print('lambda', self.lambd)
        print('k', self.k)
        print('acc:', self.acc)
        laps = Array(n, self.sbk)
        self.bit_count = self.n * ((self.k + 1) * self.acc + 1)
        @for_range(n)
        def _(i):
            

            p = exp(-1 / t)
            geo = self.geometric(p).force_bit_decompose()
            geo.append(0)
            # increase the length of geo
            geo = self.sbk.bit_compose(geo)
            
            dlap_bias = sbitint.get_type(self.acc).bit_compose(self.decfrac2bin((1 - p) / (1 + p - 2 * exp(-(2 ** self.k + 1) / t))))
            ber = self.basic_bernoulli(dlap_bias)

            dlap = ber.if_else(0, geo + 1)
            sign = self.get_random()
            
            dlap = sign.if_else(dlap, -dlap)
            # print_ln("%s", dlap.reveal())
            if self.plain_queries is not None:
                laps[i] = dlap + self.plain_queries[i]
            else:
                laps[i] = dlap
        return laps

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
    

    def discrete_laplace_odo3(self, n=None, t=None):
        if t is None:
            t = self.t
        if n is None:
            n = self.n

        r_acc = self.r2 / 2
        self.acc = int(ceil(self.lambd + math.log2((self.k+1) + math.log2(self.n) - math.log2(r_acc))))

        r_prod = self.r2 / 2
        d = int(16 * self.n  + self.lambd + math.log2(self.n) - math.log2(r_prod))


        print('Discrete Laplace odo3')
        print('n', n)
        print('t', t)
        print('lambda', self.lambd)
        print('k', self.k)
        print('acc:', self.acc)
        print('d: ', d)
        input_random = Array(d, sbit)
        self.bit_counter += d
        @for_range(d)
        def _(i):
            input_random[i] = self.get_random()

        laps = Array(n, self.sbk)
        self.bit_counter += n
        @for_range(n)
        def _(i):

            p = exp(-1 / t)
            geo = self.geometric(p, odo=3, input_random=input_random, d=d).force_bit_decompose()
            geo.append(0)
            # increase the length of geo
            geo = self.sbk.bit_compose(geo)
            
            dlap_bias = sbitint.get_type(self.acc).bit_compose(self.decfrac2bin((1 - p) / (1 + p - 2 * exp(-(2 ** self.k + 1) / t))))
            ber = self.probabilistic_bernoulli(dlap_bias, input_random, d)


            dlap = ber.if_else(0, geo + 1)
            sign = self.get_random()

            dlap = sign.if_else(dlap, -dlap)
            # print_ln("%s", dlap.reveal())
            if self.plain_queries is not None:
                laps[i] = dlap + self.plain_queries[i]
            else:
                laps[i] = dlap
        return laps
    

