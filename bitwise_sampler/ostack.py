from Compiler.GC.types import *
from Compiler.circuit import *
from Compiler.util import *
from Compiler.library import *
from Compiler.types import *
from decimal import *
from mpmath import *

def MUX_sbit(cond, b1, b2):
    return (b1 ^ cond & (b1 ^ b2))

def MUX_bitarr(cond, begin1, begin2, length, arr1, arr2):
    "if cond: arr1=arr2 else arr1=arr1"
    @for_range(length)
    def _(i):
        arr1[begin1+i] = MUX_sbit(cond, arr1[begin1+i], arr2[begin2+i])


class obliv_stack(object):
    def __init__(self, acc):
        height = int(log2(acc/3+1))
        self.height = height
        self.acc = acc
        self.slots = Matrix(3, 2**height-1, sbit)
        for i in range(3):
            for j in range(2**height-1):
                self.slots[i][j] = sbit(0)
        self.counts = Array(2*height, sbit)
        self.r = Array(height, sbit)
        self.s = [MemValue(0) for i in range(height)] 
        for i in range(height*2):
            self.counts[i] = sbit(0)    
        for i in range(height):
            self.r[i] = sbit(0)
        self.counter = [0] * height

        # initial values for p
        self.init_slots = Matrix(3, 2**height-1, sbit)
        self.init_counts = Array(2*height, sbit)
        for i in range(height*2):
            self.init_counts[i] = sbit(0)    
        self.depths = None
        self.num_and_gate = regint(0)

    def MUX_sbit(self, cond, b1, b2):
        self.num_and_gate.update(self.num_and_gate + 1)
        return (b1 ^ cond & (b1 ^ b2))
        # return (((~cond) & b1) ^ (cond & b2))

    def MUX_bitarr(self, cond, begin1, begin2, length, arr1, arr2):
        "if cond: arr1=arr2 else arr1=arr1"
        @for_range(length)
        def _(i):
        # for i in range(length):
            arr1[begin1+i] = self.MUX_sbit(cond, arr1[begin1+i], arr2[begin2+i])

    def AND(self, a, b):
        self.num_and_gate.update(self.num_and_gate + 1)
        return a & b

    def SHIFT_bitarr(self, begin1, begin2, length, arr1, arr2):
        @for_range(length)
        def _(i):
            arr1[begin1+i] = arr2[begin2+i]

    def get_depth(self, u):
        depths = Array(u, regint)
        for j in range(u):
            i = 0
            while(self.counter[i]!=0 and i != self.height-1):
                self.counter[i] = 0
                i +=1 
            self.counter[i] = 1
            depths[j] = regint(i+1)
        self.depths = depths

    def RPOP(self, f, i): 
        slot_begin = 2**i-1
        slot_length = 2**i
        self.MUX_bitarr(self.r[i], 2*i, 2*i, 2, self.counts, self.init_counts)
        @for_range(3)
        def _f(j):
            self.MUX_bitarr(self.r[i], slot_begin, slot_begin, slot_length, self.slots[j], self.init_slots[j])
        self.r[i] = sbit(0)
        if (i!=self.height-1):
            @if_e(self.s[i]==1)
            def _():
                c1 = (self.counts[2*i+1] ^ sbit(1))
                self.MUX_bitarr(c1, slot_begin, slot_begin, slot_length, self.slots[0], self.slots[2])
                s, d1, d2 = self.RPOP(c1, i+1)
                self.MUX_bitarr(c1, slot_begin, 0, slot_length, self.slots[1], d1)
                self.MUX_bitarr(c1, slot_begin, 0, slot_length, self.slots[2], d2)
                self.counts[2*i+1] = self.MUX_sbit(c1, self.counts[2*i+1], sbit(1))
                c2 = (self.counts[2*i] ^ sbit(1))
                self.MUX_bitarr(c1 & c2, slot_begin, slot_begin, slot_length, self.slots[0], self.slots[1])
                self.MUX_bitarr(c1 & c2, slot_begin, slot_begin, slot_length, self.slots[1], self.slots[2])
                # self.s[i] = 0
                self.s[i].write(0)
            @else_
            def _():
                self.s[i].write(1)

        s = 1 
        if i == 0:
            # level 1 always pop
            self.counts[2*i] =  self.counts[2*i] ^ sbit(1)
            self.counts[2*i+1] = self.counts[2*i+1] ^ self.counts[2*i]
            d = self.slots[0][0]
            self.SHIFT_bitarr(slot_begin, slot_begin, slot_length, self.slots[0], self.slots[1])
            self.SHIFT_bitarr(slot_begin, slot_begin, slot_length, self.slots[1], self.slots[2])
            return s, d
        else:
            self.counts[2*i] =  self.counts[2*i] ^ f 
            self.counts[2*i+1] = self.MUX_sbit(f, self.counts[2*i+1], self.counts[2*i+1] ^ self.counts[2*i])
            d1 = Array(slot_length//2, sbit)
            d2 = Array(slot_length//2, sbit)
            @for_range(slot_length//2)
            def _(i):
                d1[i] = self.slots[0][slot_begin+i]
                d2[i] = self.slots[0][slot_begin+slot_length//2+i]
            self.MUX_bitarr(f, slot_begin, slot_begin, slot_length, self.slots[0], self.slots[1])
            self.MUX_bitarr(f, slot_begin, slot_begin, slot_length, self.slots[1], self.slots[2])
            return s, d1, d2
        
    def RPOP_iteration(self, depth):
        # level i: 2 + 3 * 

        # reset & 3 -> 1 & calculate c1
        length = regint(1)
        c1_list = Array(self.height, sbit)
        @for_range(depth)
        def _(i):
            # reset
            slot_begin = length - 1
            slot_length = length
            self.MUX_bitarr(self.r[i], 2*i, 2*i, 2, self.counts, self.init_counts)
            @for_range(3)
            def _f(j):
                self.MUX_bitarr(self.r[i], slot_begin, slot_begin, slot_length, self.slots[j], self.init_slots[j])
  
            self.r[i] = sbit(0)
            length.update(2*length)
        length = regint(1)
        @for_range(depth-1)
        def _(i):
            # 3 -> 1 & calculate c1
            slot_begin = length - 1
            slot_length = length
            c1 = (self.counts[2*i+1] ^ sbit(1))
            self.MUX_bitarr(c1, slot_begin, slot_begin, slot_length, self.slots[0], self.slots[2])
            c1_list[i+1] = c1
            length.update(2*length)
            
        # # iterating from high level to low level
        @for_range(depth-1, 0, -1)
        def _(i):

            # this level pop
            slot_begin = length - 1
            slot_length = length
            self.counts[2*i] =  self.counts[2*i] ^ c1_list[i] 
            self.counts[2*i+1] = self.MUX_sbit(c1_list[i] , self.counts[2*i+1], self.counts[2*i+1] ^ self.counts[2*i])
            
            slot_length_next = slot_length // 2
            slot_begin_next = slot_length_next - 1
            i_next = i - 1
            self.MUX_bitarr(c1_list[i], slot_begin_next, slot_begin, slot_length_next, self.slots[1], self.slots[0])
            self.MUX_bitarr(c1_list[i], slot_begin_next, slot_begin+slot_length_next, slot_length_next, self.slots[2], self.slots[0])

            self.MUX_bitarr(c1_list[i], slot_begin, slot_begin, slot_length, self.slots[0], self.slots[1])
            self.MUX_bitarr(c1_list[i], slot_begin, slot_begin, slot_length, self.slots[1], self.slots[2])

            # next level receive pop
            self.counts[2*i_next+1] = self.MUX_sbit(c1_list[i], self.counts[2*i_next+1], sbit(1))
            c2 = self.MUX_sbit(c1_list[i], sbit(0), self.counts[2*i_next] ^ sbit(1))
            self.MUX_bitarr(c2, slot_begin_next, slot_begin_next, slot_length_next, self.slots[0], self.slots[1])
            self.MUX_bitarr(c2, slot_begin_next, slot_begin_next, slot_length_next, self.slots[1], self.slots[2])
            length.update(length // 2)

        # always pop first level 
        self.counts[0] = self.counts[0] ^ sbit(1)
        self.counts[1] = self.counts[1] ^ self.counts[0]
        d = self.slots[0][0]
        self.slots[0][0] = self.slots[1][0]
        self.slots[1][0] = self.slots[2][0]

        # return sbit(1)
        return d
    
    def CPUSH_iteration(self, f, input, depth):

        length = regint(1)
        c1_list = Array(self.height, sbit)
        c1_list[0] = f
        @for_range(depth-1)
        def _(i):
            c1_list[i+1] = self.counts[2*i+1]
            length.update(2*length)

        @for_range(depth-1, 0, -1)
        def _(i):
            slot_begin = length - 1
            slot_length = length
            slot_length_next = slot_length // 2
            slot_begin_next = slot_length_next - 1
            i_next = i - 1

            # receive push
            s = ~ self.AND(self.counts[2*i], self.counts[2*i+1])
            for j in range(1, 4):
                x1, x2 = sbit(0), sbit(0)
                x1 = self.counts[2*i] ^ sbit(j&1)
                x2 = self.counts[2*i+1] ^ sbit(j>>1)
                c2 = self.AND(self.AND(x1, x2), c1_list[i])
                self.MUX_bitarr(c2, slot_begin, slot_begin_next, slot_length_next, self.slots[j-1], self.slots[1])
                self.MUX_bitarr(c2, slot_begin+slot_length_next, slot_begin_next, slot_length_next, self.slots[j-1], self.slots[2])
            f0 = self.AND(c1_list[i], s)
            self.counts[2*i+1] = self.MUX_sbit(f0, self.counts[2*i+1], self.counts[2*i] ^ self.counts[2*i+1])
            self.counts[2*i] = self.counts[2*i] ^ f0

            # push
            self.MUX_bitarr(f0, slot_begin_next, slot_begin_next, slot_length_next, self.slots[2], self.slots[0])
            self.counts[2*(i_next)+1] = self.MUX_sbit(f0, self.counts[2*(i_next)+1], sbit(0))
            length.update(length // 2)

        # first level
        s = ~ self.AND(self.counts[0], self.counts[1])
        for j in range(1, 4):
            x1, x2 = sbit(0), sbit(0)
            x1 = self.counts[0] ^ sbit(j&1)
            x2 = self.counts[1] ^ sbit(j>>1)
            c2 = self.AND(self.AND(x1, x2), c1_list[0])
            self.slots[j-1][0] = self.MUX_sbit(c2, self.slots[j-1][0], input)
        
        f0 = self.AND(c1_list[0], s)
        self.counts[1] = self.MUX_sbit(f0, self.counts[1], self.counts[0] ^ self.counts[1])
        self.counts[0] = self.counts[0] ^ f0
    
    def CPUSH(self, f, input, i):
        slot_begin = 2**i-1
        slot_length = 2**i
        if i != self.height - 1:
            @if_e(self.s[i] == 1)
            def _(): 
                c1 = self.counts[2*i+1]
                input_next = Array(2*slot_length, sbit)
                @for_range(slot_length)
                def _(j):
                    input_next[j] = self.slots[1][slot_begin+j]
                    input_next[slot_length+j] = self.slots[2][slot_begin+j]
                s0 = c1 & self.CPUSH(c1, input_next, i+1)
                self.MUX_bitarr(s0, slot_begin, slot_begin, slot_length, self.slots[2], self.slots[0])
                self.counts[2*i+1] = self.MUX_sbit(s0, self.counts[2*i+1], sbit(0))
                self.s[i].write(0)
            @else_
            def _():
                self.s[i].write(1)

        s = ~(self.counts[2*i] & self.counts[2*i+1])
        for j in range(1, 4):
            x1, x2 = sbit(0), sbit(0)
            x1 = self.counts[2*i] ^ sbit(j&1)
            x2 = self.counts[2*i+1] ^ sbit(j>>1)
            c2 = x1 & x2 & f
            self.MUX_bitarr(c2, slot_begin, 0, slot_length, self.slots[j-1], input)

        f0 = f & s
        self.counts[2*i+1] = self.MUX_sbit(f0, self.counts[2*i+1], self.counts[2*i] ^ self.counts[2*i+1])
        self.counts[2*i] = self.counts[2*i] ^ f0
        return s
        
    def initialize_slots(self, p):
        l = self.acc
        p_bitarr = util.bit_decompose(p)
        for i in range(self.height):
            for j in range(3):
                begin = 2**i - 1
                end = 2**(i+1) - 1
                for k in range(begin, end):
                    self.init_slots[j][k] = sbit(p_bitarr[l-1])
                    self.slots[j][k] = sbit(p_bitarr[l-1])
                    l -= 1
            self.counts[2*i] = sbit(1)
            self.counts[2*i+1] = sbit(1)
            self.init_counts[2*i] = sbit(1)
            self.init_counts[2*i+1] = sbit(1)


    def CRESET(self, f, i):
        self.r[i] = self.MUX_sbit(f, self.r[i], sbit(1))
        if i != self.height - 1:
            self.CRESET(f, i+1)

    def PURGE(self):
        purge_list = Array(self.acc, sbit)
        idx = self.acc - 1
        for i in range(self.height):
            for j in range(3):
                begin = 2**i - 1
                end = 2**(i+1) - 1
                for k in range(begin, end):
                    purge_list[idx] = self.slots[j][k]
                    idx = idx - 1
        return purge_list
    
    