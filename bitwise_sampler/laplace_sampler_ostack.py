from Compiler.GC.types import *
from Compiler.circuit import *
from Compiler.util import *
from Compiler.library import *
from Compiler.types import *
from decimal import *
from mpmath import *
from bitwise_sampler.ostack import *
from bitwise_sampler.basic_sampler import basic_sampler
import re


class laplace_sampler_ostack(basic_sampler):
    def __init__(self, args, queries=None) -> None:
        basic_sampler.__init__(self, args, queries)
        self.num_real = args.num_real
        self.periodic = args.periodic
        p = exp(1 / self.t)

        M = self.r1 + self.r2 + self.r3
        self.r1 = self.r1 / M
        self.r2 = self.r2 / M
        self.r3 = self.r3 / M

        # recompute k and acc
        self.k = int(
            ceil(
                math.log2(
                    self.t
                    * (
                        (self.lambd + 1 - math.log2(self.r1) + math.log2(self.n))
                        - math.log2(1 + p)
                    )
                    * ln(2)
                )
            )
        )
        self.acc = int(
            ceil(
                self.lambd
                + math.log2((self.k + 1) + math.log2(self.n) - math.log2(self.r2))
            )
        )
        self.sbk = sbitint.get_type(self.k + 1)


    def push_times(self, n, g, r, l=None):
        if n == 0:
            return 0
        k1 = 2 * g
        if l is not None:
            k2 = (
                (
                    self.lambd
                    + math.log2(n)
                    + math.log2(self.k + l)
                    - math.log2(g)
                    - math.log2(r)
                )
                * math.log(2)
                * 2
            )
        else:
            k2 = (
                (
                    self.lambd
                    + math.log2(n)
                    + math.log2(self.k)
                    - math.log2(g)
                    - math.log2(r)
                )
                * math.log(2)
                * 2
            )
        m = int(ceil(k1 + k2 / 2 + sqrt(k2**2 / 4 + k1 * k2)))
        return m

    def get_and_gate(self, u, g, t=None, l=None):
        height1 = log2(g / 3 + 1)
        height2 = log2(self.acc / 3 + 1)
        counter1 = [0] * height1
        counter2 = [0] * height2
        depths1 = [0] * u
        depths2 = [0] * u
        for j in range(u):
            i = 0
            while counter1[i] != 0 and i != height1 - 1:
                counter1[i] = 0
                i += 1
            counter1[i] = 1
            depths1[j] = i + 1

        for j in range(u):
            i = 0
            while counter2[i] != 0 and i != height2 - 1:
                counter2[i] = 0
                i += 1
            counter2[i] = 1
            depths2[j] = i + 1

        AND_push = 0
        AND_pop = 0
        AND_reset = 0
        for d in depths1:
            for i in range(d):
                AND_push += 3 * (2**i) + 9
                if i != d - 1:
                    AND_push += 2**i + 1

        for d in depths2:
            pop0 = 0
            for i in range(d):
                if i == 0:
                    AND_pop += 3 * (2**i) + 2
                    pop0 += 3 * (2**i) + 2
                else:
                    AND_pop += 6 * (2**i) + 3
                    pop0 += 6 * (2**i) + 3
                if i != d - 1:
                    AND_pop += 3 * (2**i) + 2
                    pop0 += 3 * (2**i) + 2

            AND_reset += height2

        # print(f'{u} rstack: {AND_pop + AND_reset}, cstack: {AND_push}, reset: {AND_reset}')
        if l is None:
            if t == "push_only":
                return self.k * AND_push
            elif t == "periodic":
                return self.num_real * (AND_pop + AND_push + AND_reset) + sum(
                    [2 * i + AND_push for i in range(0, self.k - self.num_real)]
                )
            elif t == "non_periodic":
                return self.k * (AND_pop + AND_push + AND_reset)
        else:
            if t == "push_only":
                return (self.k + l) * AND_push
            elif t == "periodic":
                return (
                    self.num_real * (AND_pop + AND_push + AND_reset)
                    + sum([2 * i + AND_push for i in range(0, self.k - self.num_real)])
                    + l * (AND_pop + AND_push + AND_reset)
                )
            elif t == "non_periodic":
                return (self.k + l) * (AND_pop + AND_push + AND_reset)

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

    def discrete_laplace_geo_ostack(
        self, n=None, t=None, g=None, q=None, u=None, v=None, num_AND=None, num_bit=None, rejection=False
    ):
        """
        Sample n discrete laplace variables with the security parameter λ
        d: number of laplace
        t: the scaler of laplace
        lambd: security parameter λ
        g: batch size
        u: number of push in ostack bernoulli
        acc: the length of binary expansion of p
        k = O(log(λ+logd))
        g = lambd + log(k) + log(d) (must be 3*(2^i-1), i = 1, 2, 3, ...)
        acc = lambd + log(k) + log(d)
        """
        if t is None:
            t = self.t
        if n is None:
            n = self.n
            
        if g is None:
            if self.periodic:
                g, q, u, v, num_AND, num_bit = self.optimal_g(n, self.r3, t="periodic")
            else:
                g, q, u, v, num_AND, num_bit = self.optimal_g(
                    n, self.r3, t="non_periodic"
                )

        num_real = self.num_real if self.periodic else self.k
        num_variable = (n // g) * g + q
        p = exp(-1 / t)

        print("Discrete Laplace geo ostack")
        print("lambda", self.lambd)
        print("n", n)
        print("num_variable", num_variable)
        print("t", t)
        print("k", self.k)
        print("acc:", self.acc)
        print("num of AND gates:", num_AND)
        print("num of random bits:", num_bit)
        print("num of AND + random bits:", num_AND + num_bit)
        print("p", p)
        print("g", g)
        print("u", u)
        print("q", q)
        print("v", v)

        sbit_acc = sbitint.get_type(self.acc)
        geo_bias = sbit_acc.Array(self.k)
        for i in range(self.k):
            geo_bias[i] = sbitint.get_type(self.acc).bit_compose(
                self.decfrac2bin(p ** (2**i) / (1 + p ** (2**i)))
            )
        coins = Array(self.k * num_variable, sbit)

        @for_range(self.k)
        def _(j):
            bias = geo_bias[j]

            @for_range(n // g)
            def _(l):
                geos = self.ostack_bernoulli(u, g, bias, self.acc, j - num_real)

                @for_range(g)
                def _(c):
                    coins[l * g * self.k + c * self.k + j] = geos[c]

            geos = self.ostack_bernoulli(v, q, bias, self.acc, j - num_real)

            @for_range(q)
            def _(c):
                coins[n // g * g * self.k + c * self.k + j] = geos[c]

        sbk = sbitint.get_type(self.k + 1)
        laps = Array(n, sbk)
        signs = Array(n, sbit)
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

        if not rejection:
            @for_range(n)
            def _(j):
                laps[j] = signs[j].if_else(-laps[j], laps[j])
                print_ln("%s", laps[j].reveal())
            return laps
        else:
            return signs, laps
