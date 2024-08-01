# Secure Sampling Benchmark

This is the code of the paper 'Benchmarking Secure Sampling Protocols for Differential Privacy', written in [MP-SDPZ framework](https://github.com/data61/MP-SPDZ). It can be used to evaluate and compare the performance of sampling protocols. Also, you can use it as a library in your own MPC protocols that need differential privacy.


### Setup

Run scripts ```bash install.sh``` to automatically install and setup [MP-SDPZ](https://github.com/data61/MP-SPDZ). It then takes some time to generate enough random bits used by sampling protocols (you can modify the ```n = int(1e8)``` in random_bit.py to reduce the generating time). 

### Run protocols

#### Complie
Compile a sampling protocol with binary computation. Set parameters for main.mpc to run different protocols (the meanings of parameters are described in main.py).

For arithmetics protocols (gc, bmr, etc.), compile with

```
python main.mpc -B 64 --n <number of samples> --epsilon <privacy parameter> ...
```
For arithmetics protocols (shamir, spdz, etc.), compile with 

```
python main.mpc -F 64 --n <number of samples> --epsilon <privacy parameter> ...
```

The most important parameters are:
- **mechanism**: the type of ddp noise: lap or gauss
- **type**: the method for noise generation, dng, dngsemi, or bitwise (distributed noise generation and bitwise sampling in the paper) 
- **n**: the number of secret noise samples you want
- **epsilon**: the privacy parameter in differential privacy
- **lambd**: it determines the statistical distance between generated samples and 'perfect' samples

Other parameters (bit length presenting samples, accuracy of bernoulli sampling etc.) will be automatically chosed and optimized by the program.

The compilation will compute optimized parameters, decide input (operation) size, and generate bytecodes for execution.

#### Run compiled protocol
Run the protocol and check the time and communication.
```
make shamir-bmr-party.x
bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/biased-input (Player-Data/client-input (for dng))
```
test-sampling-main can be executed with other protocols in Scripts, e.g. yao's protocol. 

```
make yao-party.x
bash Scripts/yao.sh -v test-sampling-main -IF <path of input random bits or partial noise> 
```

### Get the main results in the paper

#### 1. Comparison under different $\lambda$ and $n$

```exp-comparison-lambda-n``` contains scripts for **Section 7.2 Efficiency of Sampling Protocols**. 


Run ```python exp-comparison-lambda-n/plot.py``` to get Figure 2 (a)(b)(c) from the log files. The figures will be saved in exp-comparison-lambda-n/plots.

To re-run the whole experiment, run ```bash exp-comparison-lambda-n/compare.sh``` (You can also read compare.sh to see how to use these protocols).

#### 2. Comparison under different $\epsilon$

```exp-epsilon``` contains scripts for **Section 7.4 Efficiency under Various Privacy Demands**. 

Run ```python exp-epsilon/plot.py``` to get Figure 5, the figures will be saved in exp-epsilon/plots.


#### 3. Comparison under different numbers of participants

```exp-party``` contains scripts for **Section 7.5 Varying the Number of Computing Parties**. 

Run ```python exp-epsilon/plot.py``` to get Figure 6, the figures will be saved in exp-party/plots.


#### 4. Compare the utility of DDP, CDP, shuffle DP, and LDP

Run ```python exp_frequency/compare-epsilon.py``` and ```python exp_frequency/compare-lambd.py```. The results are six csv files (already generated) saving the MSE, RE, and MAE of frequency query using DDP, CDP, shuffle DP, and LDP under different $\epsilon$ and $\lambda$.
You can als run ```bash exp_frequency/run_ddp_eps.sh``` and ```bash exp_frequency/run_ddp_lambd.sh``` to re-run all the protocols.

It is a more complete version of **Section 7.6 Utility of Distributed DP: Case Study**; we are revising this Section.

### Use Secure Sampling Benchmark as a Library

Import ```primitives_mpc``` into your code written with MP-SDPZ and use `binary=1` for binary and `binary=0` for arithmetics protocols. For example, you can add a discrete Laplace to the secret Array X. 
```python
import primitives_mpc

X = Array(n, sint)

Your code saving statistical results in secret Array X 

noised_X = X + primitives_mpc.bitwise_sample(n=n, mechanism='lap', binary=1)

# or use dng

noised_X = X + primitives_mpc.distributed_sample(n=n, mechanism='lap', binary=1)

```
