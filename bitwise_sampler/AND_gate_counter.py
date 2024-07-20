from Compiler.GC.types import *
from Compiler.circuit import *
from Compiler.util import *
from Compiler.library import *
from Compiler.types import *
from decimal import *
from mpmath import *
from bitwise_sampler.ostack import *
from bitwise_sampler.basic_sampler import basic_sampler
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

    def optimal_g(self, n, r, t, l=None):
        min_push_time, min_random_bit, opt_g, opt_q, opt_u, opt_v = 0, 0, 0, 0, 0, 0
        max_level = math.floor(math.log2(n / 3 + 1))
        for i in range(1, max_level + 1):
            g = 3 * (2**i - 1)
            rem = n % g
            u = self.push_times(n - rem, g, r)
            q = 0
            for j in range(1, i + 1):
                tmp = 3 * (2**j - 1)
                if tmp >= rem:
                    q = tmp
                    break
            v = self.push_times(rem, q, r, l)
            total_push_time = self.get_and_gate(u, g, t, l) * math.floor(
                n / g
            ) + self.get_and_gate(v, q, t, l)
            trial = self.k if l is None else (self.k + l)
            total_random_bit = trial * (u * math.floor(n / g) + v)
            # print('g', g)
            # print('complexity', total_push_time)
            # print('total_push_time', total_push_time2)
            # print(f'g:{g}  complexity:{total_push_time}  total_push_time:{total_push_time}')

            if i == 1 or total_push_time < min_push_time:
                min_random_bit = total_random_bit
                min_push_time = total_push_time
                opt_g = g
                opt_q = q
                opt_u = u
                opt_v = v

        # print('opt g', opt_g)
        # print('opt q', opt_q)
        # print('opt u', opt_u)
        # print('opt v', opt_v)

        self.compare_ostack_and_direct(min_push_time, opt_u, opt_v, opt_g, opt_q)
        return opt_g, opt_q, opt_u, opt_v, min_push_time, min_random_bit

    def compare_ostack_and_direct(self, com_ostack, u, v, g, q):
        com_direct = self.n * self.k * self.acc
        bit_direct = self.n * self.k * self.acc
        bit_ostack = (u * math.floor(self.n / g) + v) * self.k
        print(
            f"direct ** communication: {com_direct}, random bit: {bit_direct}, totol: {com_direct+bit_direct}"
        )
        print(
            f"ostack ** communication: {com_ostack}, random bit: {bit_ostack}, total: {com_ostack+bit_ostack}"
        )
        if com_direct + bit_direct < com_ostack + bit_ostack:
            print("use direct")
        else:
            print("use ostack")
        return com_direct > com_ostack
    
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
