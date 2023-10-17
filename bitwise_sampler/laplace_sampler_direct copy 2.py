from Compiler.GC.types import *
from Compiler.circuit import *
from Compiler.util import *
from Compiler.library import *
from Compiler.types import *
from decimal import *
from mpmath import *
from bitwise_sampler.ostack import *
from bitwise_sampler.noise_sampler import sampler

class laplace_sampler(sampler):
    def __init__(self, args, queries=None) -> None:
        sampler.__init__(self, args, queries)
        self.num_real = args.num_real
        self.periodic = args.periodic
        self.monotonic = args.monotonic
        p = exp(1 / self.t)
        if self.ostack:
            M = self.r1 + self.r2 + self.r3
            self.r1 = self.r1 / M
            self.r2 = self.r2 / M
            self.r3 = self.r3 / M
            # print(self.r1, self.r2, self.r3)
        else:
            M = self.r1 + self.r2
            self.r1 = self.r1 / M
            self.r2 = self.r2 / M
            # print(self.r1, self.r2)

        self.k = int(ceil(math.log2(self.t * ((self.lambd + 1 - math.log2(self.r1) + math.log2(self.n)) - math.log2(1 + p)) * ln(2))))
        self.acc = int(ceil(self.lambd + math.log2((self.k+1) + math.log2(self.n) - math.log2(self.r2))))
        self.sbk = sbitint.get_type(self.k+1)

    def generate_dlap(self):
        if self.test:
            g = self.g
            q = self.n % self.g
            rem = self.n % g 
            u = self.push_times(self.n-rem, g, self.r3)
            q = 0
            for i in range(15):
                if 3 * (2**i - 1) > rem:
                    q = 3 * (2**i - 1)
                    break
            v = self.push_times(rem, q, self.r3)
            self.compare_ostack_direct(g, u, q, v)
            return 0
        else:
            return self.discrete_laplace_geo_ostack(self.n, self.t) if self.ostack else self.discrete_laplace_geo_direct(self.n, self.t)
    
    def push_times(self, n, g, r):
        k1 = 2 * g 
        k2 = (self.lambd  + math.log2(n) + math.log2(self.k) - math.log2(g) - math.log2(r)) * math.log(2) * 2
        m = int(ceil(k1 + k2 / 2 + sqrt(k2 ** 2 / 4 + k1 * k2)))
        return m
    

    def get_and_gate(self, u, g):
        height1 = (log2(g/3+1))
        height2 = (log2(self.acc/3+1))
        counter1 = [0] * height1
        counter2 = [0] * height2
        depths1 = [0] * u
        depths2 = [0] * u
        for j in range(u):
            i = 0
            while(counter1[i]!=0 and i != height1-1):
                counter1[i] = 0
                i +=1 
            counter1[i] = 1
            depths1[j] = i + 1

        for j in range(u):
            i = 0
            while(counter2[i]!=0 and i != height2-1):
                counter2[i] = 0
                i +=1 
            counter2[i] = 1
            depths2[j] = i + 1

        AND_push = 0
        AND_pop = 0
        AND_reset = 0   
        for d in depths1:
            for i in range(d):
                AND_push += 3 * (2 ** i) + 9
                if i != d-1:
                    AND_push += 2 ** i + 1   

        for d in depths2:
            pop0 = 0
            for i in range(d):

                if i == 0:
                    AND_pop += 3 * (2 ** i) + 2
                    pop0 += 3 * (2 ** i) + 2
                else:
                    AND_pop += 6 * (2 ** i) + 3
                    pop0 += 6 * (2 ** i) + 3
                if i != d-1:
                    AND_pop += 3 * (2 ** i) + 2      
                    pop0 += 3 * (2 ** i) + 2
                
            AND_reset += height2   
        # print(f'{u} rstack: {AND_pop + AND_reset}, cstack: {AND_push}, reset: {AND_reset}')
        if self.recusion:
            return self.k * AND_push
        elif not self.periodic:
            return self.k * (AND_pop + AND_push + AND_reset)
        else:
            return self.num_real * (AND_pop + AND_push + AND_reset) + sum([2*i + AND_push for i in range(0, self.k - self.num_real)])

    def compare_ostack_and_direct(self, com_ostack):
        com_direct = self.n * self.k * self.acc
        print('direct', com_direct)
        print('ostack', com_ostack)
        if com_direct < com_ostack:
            print("use direct")
        else:
            print("use ostack")
        return com_direct > com_ostack
    
    def optimal_g(self, n, r):
        min_push_time, opt_g, opt_q, opt_u, opt_v = 0, 0, 0, 0, 0
        max_level = math.floor(math.log2(n/3+1))
        for i in range(1, max_level+1):                
            g = 3 * (2**i - 1)
            rem = n % g
            u = self.push_times(n - rem, g, r)
            q = 0
            for j in range(1, i+1):
                tmp = 3 * (2**j - 1)
                if tmp >= rem:
                    q = tmp
                    break
            v = self.push_times(rem, q, r)
            total_push_time = self.get_and_gate(u, g) * math.floor(n / g) + self.get_and_gate(v, q)
            total_push_time2 = u * math.floor(n / g) + v
            # print('g', g)
            # print('complexity', total_push_time)
            # print('total_push_time', total_push_time2)
            # print(f'g:{g}  complexity:{total_push_time}  total_push_time:{total_push_time}')

            if i == 1 or total_push_time < min_push_time:
                min_push_time = total_push_time
                opt_g = g
                opt_q = q
                opt_u = u
                opt_v = v

        # print('opt g', opt_g)
        # print('opt q', opt_q)
        # print('opt u', opt_u)
        # print('opt v', opt_v)

        self.compare_ostack_and_direct(min_push_time)
        return opt_g, opt_q, opt_u, opt_v
    
    def pre_and_gate(self, n):
        g, q, u, v = self.optimal_g(n, self.r3)
        self.periodic = True
        num_and_gate_ostack_periodic = self.get_and_gate(u, g) * math.floor(n / g) + self.get_and_gate(v, q)
        self.periodic = False
        num_and_gate_ostack = self.get_and_gate(u, g) * math.floor(n / g) + self.get_and_gate(v, q)
        num_and_gate_direct = n * self.k * self.acc
        self.recusion = 1
        num_and_gate_push = self.get_and_gate(u, g) * math.floor(n / g) + self.get_and_gate(v, q)
        dng = n * (2 ** self.k + 1) 

        return num_and_gate_ostack_periodic, num_and_gate_ostack, num_and_gate_direct, num_and_gate_push, dng


    def discrete_laplace_geo_ostack(self, n, t):
        """
        Sample n discrete laplace variables with the security parameter λ
        d: number of laplace 
        t: the scaler of laplace
        lambd: security parameter λ
        g: batch size 
        u: number of push in make batch
        acc: the length of binary expansion of p
        k = O(log(λ+logd))
        g = lambd + log(k) + log(d) (must be 3*(2^i-1), i = 1, 2, 3, ...)
        acc = lambd + log(k) + log(d)
        """

        g, q, u, v = self.optimal_g(n, self.r3)

        num_real = self.num_real if self.periodic else self.k
        num_variable = (n//g)*g+q
        print('Discrete Laplace geo ostack')
        print("lambda", self.lambd)
        print('n', n)
        print('num_variable', num_variable)
        print('t', t)
        print('lambda', self.lambd)
        print('k', self.k)
        print('acc:', self.acc)

        p = exp(-1 / t)
        print("p", p)
        sbit_acc = sbitint.get_type(self.acc)
        geo_bias = sbit_acc.Array(self.k)
        for i in range(self.k):
            geo_bias[i] = sbitint.get_type(self.acc).bit_compose(self.decfrac2bin(p ** (2 ** i) / (1 + p ** (2 ** i)))) 
        coins = Array(self.k*num_variable, sbit)
        @for_range(self.k)
        def _(j):
            bias = geo_bias[j]
            @for_range(n//g)
            def _(l):
                output_bits = self.make_batch(u, g, bias, self.acc, j-num_real)
                geos = output_bits.PURGE()
                @for_range(g)
                def _(c):
                    coins[l*g*self.k+c*self.k+j] = geos[c]

            output_bits = self.make_batch(v, q, bias, self.acc, j-num_real)
            geos = output_bits.PURGE()
            @for_range(q)
            def _(c):
                coins[n//g*g*self.k+c*self.k+j] = geos[c]

        sbk = sbitint.get_type(self.k+1)
        laps = Array(n, sbk)
        @for_range(n)
        def _(j):
            geo = coins.get_part(j*self.k, self.k)
            geo = sbitint.get_type(self.k).bit_compose(geo)
            
            if self.k != 1:
                geo = geo.force_bit_decompose()
            geo.append(0)
            geo = sbk.bit_compose(geo)
            dlap_bias = sbitint.get_type(self.acc).bit_compose(self.decfrac2bin((1 - p) / (1 + p - 2 * exp(-(2 ** self.k + 1) / t))))
            ber = self.basic_bernoulli(dlap_bias)
            dlap = ber.if_else(0, geo + 1)
            sign = self.get_random()
            dlap = sign.if_else(dlap, -dlap)
            print_ln("get dlap: %s", dlap.reveal())
            if self.plain_queries is not None:
                laps[j] = dlap + self.plain_queries[j]
            else:
                laps[j] = dlap
        return laps.get_part(0, n)


    def geometric(self, p):
        print("p", p)
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
        geo = self.sbk.bit_compose(geo)
        
        dlap_bias = sbitint.get_type(self.acc).bit_compose(self.decfrac2bin((1 - p) / (1 + p - 2 * exp(-(2 ** self.k + 1) / t))))
        ber = self.basic_bernoulli(dlap_bias)

        dlap = ber.if_else(0, geo + 1)
        sign = self.get_random()
        print_ln("and_gate: %s", self.and_counter.reveal())
        return sign, dlap

    def discrete_laplace_geo_direct(self, n, t):
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
            print_ln("get dlap: %s", dlap.reveal())
            if self.plain_queries is not None:
                laps[i] = dlap + self.plain_queries[i]
            else:
                laps[i] = dlap
        return laps
    
    def report_noisy_max_dlap(self, num_query):
        if self.monotonic:
            self.t /= 2
        if self.ostack:
            dlaps_queries = self.discrete_laplace_geo_ostack(num_query, self.t)
        else:
            dlaps_queries = self.discrete_laplace_geo_direct(num_query, self.t)
        argmax = self.sbk.Array(1)
        argmax[0] = self.sbk(0)   
        max_score = self.sbk.Array(1)
        max_score[0] = dlaps_queries[0]
        @for_range(num_query)
        def _(i):
            idx = self.sbk(i)
            larger = dlaps_queries[i] > max_score[0]
            print_ln("%s", larger.reveal())
            print_ln("max: %s", max_score[0].reveal())
            argmax[0] = larger.if_else(idx, argmax[0])
            max_score[0] = larger.if_else(dlaps_queries[i], max_score[0])
        print_ln("noisy max: %s", argmax[0].reveal())
        return argmax[0]

    def SVT_ostack(self, num_query, eps1=0.3, eps2=0.3, eps3=0.4, c=10, plain_thr=None):
        print("SVT Ostack")
        if plain_thr is not None:
            p = self.discrete_laplace_geo_direct(1, t/eps1, plain_queries=plain_thr)
        else:
            p = self.discrete_laplace_geo_direct(1, t/eps1)      
        noised_queries = self.discrete_laplace_geo_ostack(num_query, t/eps2)
        addtional_noise = self.discrete_laplace_geo_ostack(num_query, t/eps3)
        output = Array(num_query, self.sbk)
        count = Array(1, self.sbk)
        count[0] = self.sbk(0)
        c_sint = self.sbk(c)
        @for_range(num_query)
        def _(i):
            @if_(eps3==0)
            def _():
                addtional_noise[i] = self.sbk(1)
            accept = (noised_queries[i] > p[0])
            finish = (count[0] > c_sint)
            accept_output = accept.if_else(addtional_noise[i], self.sbk(0))
            output[i] = finish.if_else(self.sbk(-1), accept_output)
            count[0] = (accept & (~finish)).if_else(count[0]+1, count[0])
        return output
    
    def compare_ostack_direct(self, g, u, q, v):
        t = self.t
        p = exp(1 / t)
        sbit_acc = sbitint.get_type(self.acc) 
        print('n', self.n)
        print('k', self.k)
        print("acc", self.acc)
        print('g', g)
        print('u', u)
        print('q', q)
        print('v', v)
        @if_e(self.ostack)
        def _():
            geo_bias = sbit_acc.Array(self.k)
            for i in range(self.k):
                geo_bias[i] = sbitint.get_type(self.acc).bit_compose(self.decfrac2bin(p ** (2 ** i) / (1 + p ** (2 ** i))))
            @for_range(self.k*(self.n//g))
            def _(i):
                output_bits = self.make_batch(u, g, geo_bias[0], self.acc, -1)
                geos = output_bits.PURGE()                
        @else_
        def _():
            geo_bias = [self.decfrac2bin(p ** (2 ** i) / (1 + p ** (2 ** i))) for i in range(self.k)]
            length = self.k*self.n
            print("length", length)
            print(len(geo_bias[0]))
            @for_range(length)
            def _(i):
                print(i)
                self.basic_bernoulli(geo_bias[0])

