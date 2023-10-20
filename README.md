# MPC-DP Benchmark

This is the code of paper 'Benchmarking Secure Sampling Protocols for Differential Privacy', written in [MP-SDPZ framework](https://github.com/data61/MP-SPDZ). It can be used to evaluate and compare the performance of sampling protocols. Also, you can use it as a library in your own MPC protocols that need differential privacy.


### Setup

numpy and matplotlib libraries are required.
Also you should have MP-SPDZ correctly installed. See its [documnet](https://mp-spdz.readthedocs.io/en/latest) for installation. Put all the project files under your MP-SPDZ directory.
Generate random bits input first.

```
python random_bit.py <number of bits> <number of parties> 
```

### Run Evaluation

Compile a sampling protocol with binary computation. Set parameters for main.mpc to run different protocols (the means of parameters are described in main.py).
```
python main.mpc -B 64
```
For arithmetics protocols, compile with `-bin 0`.

```
python main.mpc -F 64 -bin 0
```

Run the protocol and see the time and communication.
```
make shamir-bmr-party.x
bash Scripts/shamir-bmr.sh -v test-sampling-main -IF <path of input random bits or partial noise> 
```
test-sampling-main can be executed with other protocols in Scripts, e.g. yao's protocol. 

```
make yao-party.x
bash Scripts/yao.sh -v test-sampling-main -IF <path of input random bits or partial noise> 
```

To view the comparison of protocols, run `python exp/plot_line`. Or use `bash exp/compare.sh` to re-execute all the protocols and plot (it is time-consuming).


### Use MPC-DP Benchmark as a Library

Import ```primitives_mpc``` into your code written with MP-SDPZ and use `binary=1` for binary and `binary=0` for arithmetics protocols.
```python
from primitives_mpc import

X = Array(n, sint)

# Your code saving statistical results in secret Array X 

noised_X = X + primitives_mpc.bitwise_sample(n=n, mechanism='lap', binary=1)
```