from bitwise_sampler.ostack import *
from bitwise_sampler.laplace_sampler_direct import *
from bitwise_sampler.laplace_sampler_ostack import *
from bitwise_sampler.gaussian_sampler_ostack import *
from bitwise_sampler.gaussian_sampler_direct import *
from bitwise_sampler.AND_gate_counter import *
from bitwise_sampler.test import *
from DNG.dng_dlap import dlap_generator
from DNG.dng_gauss import dgauss_generator

def find_max_i(num):
    i = 0
    while True:
        val = (2 ** (-i)) * math.log(2)
        if val < num:
            return i  
        i += 1

def dtype_convert(noise, binary):
    if binary == 0:
        n = noise.length
        noise_sint = Array(n, sint)
        @for_range(n)
        def _(i):
            noise_sint[i] = sint.bit_compose(noise[i])
        return noise_sint
    else:
        return noise

class dp_option(object):
    def __init__(self, n, s, epsilon, delta, lambd, num_party) -> None:
        # general parameters
        self.n = n
        self.sensitivity = s
        self.epsilon = epsilon
        self.delta = delta
        self.lambd = lambd
        self.num_party = num_party


class dp_option_bitwise(dp_option):
    def __init__(self, n, s, epsilon, delta, lambd, num_party, ostack, periodic, r) -> None:
        dp_option.__init__(self, n, s, epsilon, delta, lambd, num_party)
        # bitwise sampling parameters
        self.r1, self.r2, self.r3, self.r4 = r
        self.ostack = ostack
        self.periodic = periodic
        self.num_real = find_max_i(epsilon) if self.periodic == 1 else 0
        self.recusion = 0
        
        
def bitwise_sample(mechanism='lap', n=4096, s=1, epsilon=0.1, delta=1e-5, lambd=128, num_party=3, ostack=1, approximation=0, r=(1, 1, 1, 1), binary=0): 
    option = dp_option_bitwise(n=n, s=s, epsilon=epsilon, delta=delta, lambd=lambd, num_party=num_party, ostack=ostack, periodic=approximation, r=r) 
    if mechanism == 'lap':
        if option.ostack == 1:
            sa = laplace_sampler_ostack(option) 
            ans = sa.discrete_laplace_geo_ostack()
        else:
            sa = laplace_sampler_direct(option)
            ans = sa.discrete_laplace_geo_direct()

    elif mechanism == 'gauss':
        if option.ostack == 1:
            sa = gauss_sampler_ostack(option) 
            ans = sa.discrete_gaussian_dlap_rejection_ostack()
        else:
            sa = gauss_sampler(option)
            ans = sa.discrete_gaussian_dlap_rejection()

    return dtype_convert(ans, binary)



def distributed_sample(mechanism='lap', n=4096, s=1, epsilon=0.1, delta=1e-5, lambd=128, num_party=3, compile_partial=1, check=0, binary=1):
    option = dp_option(n=n, s=s, epsilon=epsilon, delta=delta, lambd=lambd, num_party=num_party) 

    if mechanism == 'lap':
        generator = dlap_generator(option)
    elif mechanism == 'gauss':
        generator = dgauss_generator(option)


    if compile_partial == 1:
        generator.generate_partial_noise()

    ans = generator.aggregate_discrete()
    noise = dtype_convert(ans, binary)

    if check == 1:
        res = generator.KS_test_discrete(noise, binary)
    
    return ans


def distributed_transform():
    pass
