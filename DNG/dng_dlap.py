import numpy as np
from mpmath import *
from math import exp, log2, log, ceil, sqrt
from scipy.stats import nbinom
from scipy import stats
from Compiler.GC.types import *
from Compiler.circuit import *
from Compiler.util import *
from Compiler.library import *
# from Compiler.types import *

class dlap_generator(object):
    def __init__(self, args) -> None:
        sfix.set_precision(16, 32)
        self.n, self.m, self.lambd = args.n, args.num_party, args.lambd
        self.t = args.sensitivity / args.epsilon
        p = exp(1 / self.t)

        self.k = int(ceil(log2(self.t * ((self.lambd + 1 + log2(self.n)) - log2(1 + p)) * log(2))))
        self.sbg = sbitint.get_type(self.k)
        self.sbl = sbitint.get_type(self.k+1)
        self.N = 2 ** self.k + 1
        print(f't: {self.t}')
        print(f'k derived from allocating lambda to truncation: {self.k}')
        print(f'mod clip N: {self.N}')

    def module_clip(self, noise):
        return (noise + self.N % (2 * self.N)) - self.N

    def output_pn_to_clients(self, noise):
        signs = noise > 0
        for i in range(self.m):
            with open(f'Player-Data/Input-P{i}-0', 'w') as f:
                for j in range(self.n):
                    f.write(str(int(signs[i][j])) + ' ')
                    f.write(str(abs(noise[i][j])) + ' ')
            f.close()

    def sample_from_polya(self):
        r = exp(-1 / self.t)
        polya1 = nbinom.rvs(n=1/self.m, p=(1-r), size=(self.m, self.n))
        polya2 = nbinom.rvs(n=1/self.m, p=(1-r), size=(self.m, self.n))
        return self.module_clip(polya1 - polya2)
    
    def generate_partial_noise(self):
        noise = self.sample_from_polya()
        self.output_pn_to_clients(noise)

    def aggregate_discrete(self):
        dlaps = Array(self.n, self.sbl)
        @for_range(self.n)
        def _(i):
            dlaps[i] = self.sbl(0)
        
        for i in range(self.m):
            @for_range(self.n)
            def _(j):
                sign = sbit.get_input_from(i)
                partial_noise = self.sbl.get_input_from(i)
                partial_noise = sign.if_else(partial_noise, -partial_noise)
                dlaps[j] = dlaps[j] + partial_noise
        @for_range(self.n)
        def _(i):
            print_ln("%s", dlaps[i].reveal())
        return dlaps 
    
    def KS_test_discrete(self, D, binary=1):
        print_ln("begin KS test")
        k, N = self.k, self.N
        n = self.n
        D_cit = 1.36 * sqrt(2/n)
        c = sint(0) if binary == 0 else self.sbl(0)
        bound = sint(999) if binary == 0 else self.sbl(999)
        @for_range(self.n)
        def _(i):
            legal = (D[i] < bound) & (D[i] > (-bound)) 
            c.update(c+legal)
            
        sfix_num = sfix if binary == 0 else sbitfix
        f_table = Array(2*N+1, sfix_num)
        obs_table = Array(self.n, sfix_num)
        @for_range(self.n)
        def _(i):
            obs_table[i] = sfix_num(0)
        if binary == 0:
            idx_table = Array(2*N+1, sint)
        else:
            idx_table = Array(2*N+1, self.sbl)
        dlap_cdf = stats.laplace.cdf(np.linspace(-N, N+1, 2*N+1), scale=self.t)

        for i in range(2*N+1):
            f_table[i] = sfix_num(dlap_cdf[i] * self.n)
            idx_table[i] = sint(i-N) if binary == 0 else self.sbl(i-N)

        # num_and = self.n * (2*N+1) * (self.k + 1 + 32)
        # print("num of AND gates", num_and)  


        @for_range(n)
        def _(i):
            f_dis = sfix_num(0)
            @for_range(2*N+1)
            def _(j):
                equal = (D[i] == idx_table[j])
                f_dis.update(equal.if_else(f_table[j], f_dis))
                
            obs_table[i] = f_dis

        obs_table.sort()

        f_max = sfix_num(0)

        @for_range_opt(self.n)
        def _(i):
            f_dis = abs(i - obs_table[i])
            f_new = (f_max > f_dis).if_else(f_max, f_dis)
            f_max.update(f_new)
        print_ln("res: %s", f_max.reveal())
        return f_max < D_cit
# import sys
# config.lambd = int(sys.argv[4])
# config.n = int(sys.argv[5])
# config.epsilon = float(sys.argv[6])


# generator = dlap_generator(config)
# generator.generate_partial_noise()
# noise = generator.aggregate_discrete()
# generator.KS_test_discrete(noise)