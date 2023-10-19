# MPC-DP Benchmark

This is the code of paper 'Benchmarking Secure Sampling Protocols for Differential Privacy', written in [MP-SDPZ framework](https://github.com/data61/MP-SPDZ). It can be used to evaluate and compare perfomance of sampling protocols. Also, you can used it as a library in your own MPC protocols that needs differential privacy.


### MP-SPDZ set-up

Should have MP-SPDZ correctly installed, see its [documnet](https://mp-spdz.readthedocs.io/en/latest) for installation. Put all the project files under your MP-SPDZ direcotry.


### Run Evaluation

Compile a sampling protocol with binary computation. Set parameters for main.mpc to run differen protocols (the means of parameters are described in main.py).
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
test-sampling-main can be excuted with other protocols in Scripts, e.g. yao's protocol. 

```
make yao-party.x
bash Scripts/yao.sh -v test-sampling-main -IF <path of input random bits or partial noise> 
```



### Use MPC-DP Benchmark as a Library

In your code written witn MP-SDPZ. `binary=1` for binary and `binary=0` for arithmetics protocols.
```python

from primitives_mpc import

# Your code to obtain a secret Array X of length n of statistical results

noised_X = X + primitives_mpc.bitwise_sample(n=n, mechanism='lap', binary=1)

```
