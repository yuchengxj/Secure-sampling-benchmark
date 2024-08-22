from Compiler.GC.types import *
from Compiler.circuit import *
from Compiler.util import *
from Compiler.library import *
from Compiler.types import *
from decimal import *
from mpmath import *
from bitwise_sampler.ostack import *
from bitwise_sampler.gaussian_sampler_odo import *
from bitwise_sampler.laplace_sampler_ostack import *
from bitwise_sampler.laplace_sampler_odo import *
from scipy import stats

def test_ostack():
    N = 189 # N = 3 * (2^l - 1)
    test_list = stats.bernoulli.rvs(size=N, p=0.5)
    push_only_stk = obliv_stack(N)
    pop_only_stk = obliv_stack(N)
    s = pop_only_stk.initialize_slots(0.56)

    print_ln("\ntesting push only stack\n")

    for i in range(test_list.shape[0]):
        input = Array(1, sbit)
        input[0] = sbit(int(test_list[i]))
        push_only_stk.CPUSH(sbit(1), input, 0)

    output_bits = push_only_stk.PURGE()
    clear_bits = [i.reveal() for i in output_bits]
    # debug(push_only_stk, 3)
    for i in range(test_list.shape[0]):
        print_ln("coin in stack: %s, clear coin: %s", clear_bits[i], test_list[i])

    print_ln("\ntesting pop only stack")
    print_ln("\ntesting pop")
    L1 = []
    for i in range(N):
        s, d = pop_only_stk.RPOP(sbit(1), 0)
        L1.append(d)
    print_ln("bit expansion: 100011110101110000101000111101011100001010001111011")
    for i in range(N):
        print_ln("pop coin: %s", L1[i].reveal())
    
    L2 = []
    pop_only_stk.CRESET(sbit(1), 0)
    for i in range(N):
        s, d = pop_only_stk.RPOP(sbit(1), 0)
        L2.append(d)

    print_ln("\ntesting reset")
    for i in range(N):
        print_ln("before pop: %s, after reset: %s", L1[i].reveal(), L2[i].reveal())
    
def test_make_batch(args):
    sa = basic_sampler(args)
    def decfrac2bin(dec, acc):
        bin = []
        for i in range(acc):
            dec *= 2
            bit = int(dec)
            dec -= bit
            bin.append(sbit(bit))
        return list(reversed(bin))
    g = 3069
    u = 6947
    p = 0.9
    acc = 144
    rands = stats.bernoulli.rvs(size=u, p=0.9)
    @for_range(1)
    def _(k):
        p_bitarr = sbitint.get_type(acc).bit_compose(decfrac2bin(p, acc))
        biased_coins = sa.make_batch(u, g, p_bitarr, acc)
        output_bits = biased_coins.PURGE()
        clear_bits = [i.reveal() for i in output_bits]
        print_ln("g:%s", g)
        for i in range(g):
            print_ln("coin in stack: %s", clear_bits[i])