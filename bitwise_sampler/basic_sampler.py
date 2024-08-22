from Compiler.GC.types import *
from Compiler.circuit import *
from Compiler.util import *
from Compiler.library import *
from Compiler.types import *
from decimal import *
from mpmath import *
from bitwise_sampler.ostack import *
import numpy as np


class basic_sampler(object):
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
        self.bit_count = 0

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

    def generate_input_bits(self):
        print(self.bit_count)
        for i in range(self.num_party):
            output_file = 'Player-Data/Input-P' + str(i) + '-0'
            with open(output_file, 'w') as f:
                for j in range(self.bit_count):
                    f.write(str(random.randint(0,1)) + ' ')
            f.close()

    

    def debug(self, stk, n):
        for i in range(n):
            print_ln("level: %s s: %s count: %s %s", i, stk.s[i], stk.counts[2*i+1].reveal(), stk.counts[2*i].reveal())
            for j in range(3):
                begin = 2**i - 1
                end = 2**(i+1) - 1
                for k in range(begin, end):
                    print_ln("%s", stk.slots[j][k].reveal())

                    
    def recursive_bernoulli(self, u, n, p, acc):
        """
        ODO-1
        u: the total number of comparison to get targeted number of samples with same bias
        p: bias
        """
        class BiasedCoinCircuit(object):
            def __init__(self, depth, bias_probability, radnom_bit):
                self.depth = depth  
                self.bias_probability = util.bit_decompose(bias_probability)
                self.bias_probability.reverse()
                self.bias_index = [i for i in range(depth)]
                self.radnom_bit = radnom_bit

            def concat_coins(self, left_coins, right_coins, length_left, length_right, left_valid):
                left_coins_sbitint = sbitint.get_type(length_left+length_right).bit_compose(left_coins + [sbit(0)] * length_right)
                right_coins_sbitint = sbitint.get_type(length_left+length_right).bit_compose(right_coins)
                shift_bits = sbitint(length_left) - left_valid
                # right_coins_sbitint = right_coins_sbitint * shift_bits.pow2(k=length_left+length_right)
                # left shift right_coins
                # for i in range(length_left):
                # # @for_range(length_left)
                # # def _(i):
                #     shift_bits = sbitint(length_left) - left_valid
                #     shift_bits.pow2()
                #     shift = i>shift_bits
                #     right_coins_sbitint.update(shift.if_else(right_coins_sbitint*2, right_coins_sbitint))
                conis_sbitint = left_coins_sbitint + right_coins_sbitint
                return conis_sbitint.force_bit_decompose()


            
            def hierarchical_generate(self, num_coins, start_index=sbitint(0)):

                if num_coins == 0:
                    return sbit(0), 0, start_index
                
                if num_coins == 1:
                    r = self.radnom_bit()

                    # get the biased bit at start_index
                    b = sbit(0)
                    # for i in range(self.depth):
                    #     find = start_index.equal(self.bias_index[i])
                    #     b.update(find.if_else(self.bias_probability[i],b))

                    xor_res = b ^ r  
                    coin = xor_res.if_else(~r, sbit(0))
                    # print(coins)
                    n = xor_res.if_else(sbitint(1), sbitint(0))
                    start_index = xor_res.if_else(sbitint(0), (start_index + sbitint(1)))

                    return [coin], n, start_index

                mid = num_coins // 2
                left_coins, left_valid, next_index = self.hierarchical_generate(mid, start_index)
                right_coins, right_valid, final_index = self.hierarchical_generate(num_coins - mid, next_index)
                total_coins = self.concat_coins(left_coins, right_coins, len(left_coins), len(right_coins), left_valid)                

                total_valid = left_valid + right_valid
                return total_coins, total_valid, final_index
            
        circuit = BiasedCoinCircuit(acc, p, self.get_random)
        biased_coins, valid_coins_count, _ = circuit.hierarchical_generate(u)
        return biased_coins[:n]


    def basic_bernoulli(self, p):
        """
        ODO-2
        """
        if not isinstance(p, list):
            # the binary bias is reversed
            bias = util.bit_decompose(p)
        else:
            bias = p 
        ber = 0
        for b in bias: 
            r = self.get_random()
            ber = (r ^ b).if_else(~r, ber)
            self.and_counter.update(self.and_counter+1)
        return ber
    

    def probabilistic_bernoulli(self, p, input_b, d):
        """
        ODO-3
        """
        if not isinstance(p, list):
            # the binary bias is reversed
            bias = util.bit_decompose(p)
        else:
            bias = p 
        ber = 0
        for b in bias: 

            precompute_r = sbit.Array(d)
            @for_range(d)
            def _(i):
                precompute_r[i] = sbit(random.choice([0, 1]))
            r = sbit(0)
            # @for_range(d)
            # def _(i):
            #     r.update(r.bit_xor(precompute_r[i].bit_and(input_b[i])))
            ber = (r ^ b).if_else(~r, ber)
            self.and_counter.update(self.and_counter+1)
        return ber


    def ostack_bernoulli(self, u, g, p, acc, j=0):
        """
        Ostack
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

        return cstack.PURGE()
    
