from Compiler.GC.types import *
from Compiler.circuit import *
from Compiler.util import *
from Compiler.library import *
from Compiler.types import *
from decimal import *
from mpmath import *
from bitwise_sampler.ostack import *
from bitwise_sampler.noise_sampler import sampler
from bitwise_sampler.laplace_sampler_ostack import laplace_sampler_ostack

        
def trial_times(n, p, delta):
    start = int(ceil(n / p))
    end = 3 * start
    k1 = n / p
    k2 = (-log2(delta)) * log(2) / (2 * p ** 2)
    m = int(ceil(k1 + k2 / 2 + sqrt(k2 ** 2 / 4 + k1 * k2)))
    return m

class counter(laplace_sampler_ostack):
    def __init__(self, args, queries=None) -> None:
        laplace_sampler_ostack.__init__(self, args, queries)
        self.l = None
    
    def pre_and_gate(self, n, mechanism):
        p_ = 0
        if mechanism == 'dgauss':
            M = self.r1 + self.r2 + self.r3 + self.r4
            self.r1, self.r2, self.r3, self.r4 = self.r1/M, self.r2/M, self.r3/M, self.r4/M
            self.sigma = self.t
            # Truncation error
            self.k = max(int(ceil(math.log2(sqrt(2 * ln(2) * (self.lambd - math.log2(self.r1) + math.log2(self.n))) * self.sigma - 1))), 1)
            self.N = (1 << self.k) + 1
            self.sigma = self.t
            self.k = max(int(ceil(math.log2(sqrt(2 * ln(2) * (self.lambd - math.log2(self.r1) + math.log2(self.n))) * self.sigma - 1))), 1)
            if self.sigma >= 1:
                z = nint(self.sigma)
            else:
                z = 1 / ceil(1 / self.sigma)

            if z >= 1:
                t = self.sigma ** 2 / z
            else:
                t = self.sigma ** 2 * (1/z) 
                
            if z >= 1:
                self.l = 2 * self.k
            else:
                self.l = 2 * (self.k + 1) + 2 * int(ceil(math.log2(1 / z)))
            s1 = nsum(lambda x: exp(-(x ** 2) / (2 * self.sigma ** 2)), [-(self.N - 1), (self.N - 1)])
            s2 = nsum(lambda x: exp(-abs(x) / t), [-(self.N - 1), (self.N - 1)])
            s3 = exp(-(self.sigma ** 2) / (2 * t ** 2))

            p = s1 / s2 * s3
            p_ = p - (2 ** (-self.lambd))
            n = trial_times(self.n, p_, 2 ** (-self.lambd + math.log2(self.r4)))
            
        _, _, _, _, num_and_gate_ostack_periodic, num_bit_ostack_periodic = self.optimal_g(n, self.r3, t='periodic', l=self.l)
        _, _, _, _, num_and_gate_ostack, num_bit_ostack = self.optimal_g(n, self.r3, t='non_periodic', l=self.l)
        _, _, _, _, num_and_gate_push, num_bit_ostack_push = self.optimal_g(n, self.r3, t='push_only', l=self.l)

        if mechanism == 'dlap':
            M = self.r1 + self.r2
            self.r1 = self.r1 / M
            self.r2 = self.r2 / M
            p = exp(1 / self.t)
            self.k = int(ceil(math.log2(self.t * ((self.lambd + 1 - math.log2(self.r1) + math.log2(self.n)) - math.log2(1 + p)) * ln(2))))
            self.acc = int(ceil(self.lambd + math.log2((self.k+1) + math.log2(self.n) - math.log2(self.r2))))
            num_and_gate_direct = n * self.k * self.acc
            num_random_bit_direct = n * self.k * self.acc
        elif mechanism == 'dgauss':
            M = self.r1 + self.r2 + self.r3
            self.r1 = self.r1 / M
            self.r2 = self.r2 / M
            self.r3 = self.r3 / M
            self.k = max(int(ceil(math.log2(sqrt(2 * ln(2) * (self.lambd - math.log2(self.r1) + math.log2(self.n))) * self.sigma - 1))), 1)
            d = self.k + self.l + 1
            self.acc = int(ceil(self.lambd + 2 + math.log2(d * self.n / p_)))
            num_and_gate_direct = n * (self.k + self.l) * self.acc
            num_random_bit_direct = n * (self.k + self.l) * self.acc
        num_and_gate_dng = n * (2 ** self.k + 1) 


        return num_and_gate_ostack_periodic, num_and_gate_ostack, num_and_gate_direct, num_and_gate_push, num_and_gate_dng, num_bit_ostack_periodic, num_bit_ostack, num_random_bit_direct, num_bit_ostack_push
