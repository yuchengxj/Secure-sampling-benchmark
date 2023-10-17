from Compiler.GC.types import *
from Compiler.circuit import *
from Compiler.util import *
from Compiler.library import *
from Compiler.types import *
from decimal import *
from mpmath import *
from bitwise_sampler.ostack import *

class sampler(object):
    def __init__(self, args, queries=None) -> None:
        self.epsilon = args.epsilon
        self.t = args.sensitivity / args.epsilon
        self.lambd = args.lambd
        self.n = args.n
        self.num_party = args.num_party
        self.ostack = args.ostack
        self.recusion = args.recusion
        self.plain_queries = queries
        p = exp(1 / self.t)
        self.k = int(ceil(math.log2(self.t * ((self.lambd + 2 + math.log2(self.n)) - ln(1 + p)) * ln(2))))
        self.acc = int(ceil(self.lambd + 2 + math.log2((self.k+1) * self.n)))
        self.sbk = sbitint.get_type(self.k+1)
        self.r1 = args.r1
        self.r2 = args.r2
        self.r3 = args.r3
        self.r4 = args.r4
        self.and_counter = regint(0)

    def decfrac2bin(self, dec):
        bin = []
        for i in range(self.acc):
            dec *= 2
            bit = int(dec)
            dec -= bit
            bin.append(sbit(bit))
        return list(reversed(bin))


    def expand_noise(self, noise, precision):
        for i in range(self.n):
            x = util.bit_decompose(noise[i])
            bin.append()
            sign = x[i]
            bin = []


    
    def get_random(self):
        uniform_bit = Array(1, sbit)
        uniform_bit[0] = sbit.get_input_from(0)
        for i in range(1, self.num_party):
            uniform_bit[0] = uniform_bit[0] ^ sbit.get_input_from(i)

        return uniform_bit[0]
    
    def debug(self, stk, n):
        for i in range(n):
            print_ln("level: %s s: %s count: %s %s", i, stk.s[i], stk.counts[2*i+1].reveal(), stk.counts[2*i].reveal())
            for j in range(3):
                begin = 2**i - 1
                end = 2**(i+1) - 1
                for k in range(begin, end):
                    print_ln("%s", stk.slots[j][k].reveal())
    
    def basic_bernoulli(self, p):
        if not isinstance(p, list):
            bias = util.bit_decompose(p)
        else:
            bias = p 
        ber = 0
        for b in bias: 
            r = self.get_random()
            ber = (r ^ b).if_else(~r, ber)
            self.and_counter.update(self.and_counter+1)
        return ber
                    

    def make_batch(self, u, g, p, acc, j=0):
        """
        Make a batch of coins of size g
        g: size of stack (number of coins it can make)
        u: number of push to fill the batch of size g
        p: bias
        acc: length of stack to save the binary expansion of p
        g = acc = O(λ+logd), g must be 3*(2^i-1), i = 1, 2, 3, ... 
        """
        cstack = obliv_stack(g)
        cstack.get_depth(u)

        @if_e(j>=0)
        def _():
            counter = Array(self.k, sbit)
            @for_range(j)
            def _(l):
                counter[l] = sbit(0)
            @for_range(u)
            def _(i):
                b = self.get_random()
                t = counter[j]
                f = b ^ t
                if self.recusion:
                    input = Array(1, sbit)
                    input[0] = b
                    s = cstack.CPUSH(~f, input, 0)
                else:
                    cstack.CPUSH_iteration(~f, b, cstack.depths[i])
                next = sbit(1)
                @for_range(self.k)
                def _(l):
                    temp = counter[l]
                    new_bit = next ^ counter[l]
                    next.update(temp & next)
                    counter[l] = MUX_sbit(~f, sbit(0), new_bit)
        
        @else_
        def _():
            rstack = obliv_stack(acc)
            rstack.get_depth(u)
            s = rstack.initialize_slots(p)
            @for_range(u)
            def _(i):

                # recusion
                if self.recusion:
                    b = self.get_random()
                    s, t = rstack.RPOP(sbit(1), 0)
                    f = b ^ t
                    input = Array(1, sbit)
                    input[0] = b
                    s = cstack.CPUSH(~f, input, 0)
                    rstack.CRESET(~f, 0)

                else:
                    b = self.get_random()
                    t = rstack.RPOP_iteration(rstack.depths[i])                
                    f = b ^ t
                    cstack.CPUSH_iteration(~f, b, cstack.depths[i])

                    # print_ln("%s,%s", rstack.depths[i].reveal(), rstack.num_and_gate.reveal())
                    # print_ln("%s,%s", cstack.depths[i].reveal(), cstack.num_and_gate.reveal())

                    # print_ln("pop: depth: %s, number of and gates: %s", rstack.depths[i].reveal(), rstack.num_and_gate.reveal())
                    # print_ln("push: depth: %s, number of and gates: %s\n", cstack.depths[i].reveal(), cstack.num_and_gate.reveal())
                    rstack.CRESET(~f, 0)
                    cstack.num_and_gate.update(0)
                    rstack.num_and_gate.update(0)


            # print_ln("rstack.num_and_gate: %s", (rstack.num_and_gate).reveal())
            # print_ln("cstack.num_and_gate: %s", (cstack.num_and_gate).reveal())

        return cstack
    
