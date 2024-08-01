#!/bin/bash

lambdas=(2 4 8 16 32)
# lambdas=(1)

## gaussian
# odo
for lambda in ${lambdas[@]}; do
    python compile.py -B 64 sampling_gaussian.mpc 0 4096 0.1 $lambda
    bash Scripts/shamir-bmr.sh -v sampling_gaussian-0-4096-0.1-${lambda} -IF Player-Data/biased-input > exp_frequency/gauss/ddp_noise_lambd/odo/${lambda}/out.log
    
    # bash Scripts/yao.sh -v sampling_gaussian-0-4096-48.44-128 -IF Player-Data/biased-input > exp_frequency/gauss/ddp_noise_eps/odo/0.1/out.log

done


for lambda in ${lambdas[@]}; do
    python compile.py -B 64 sampling_gaussian.mpc 0 4096 0.1 $lambda
    bash Scripts/shamir-bmr.sh -v sampling_gaussian-0-4096-0.1-${lambda} -IF Player-Data/biased-input > exp_frequency/gauss/ddp_noise_lambd/ostack1/${lambda}/out.log
    
    # bash Scripts/yao.sh -v sampling_gaussian-0-4096-48.44-128 -IF Player-Data/biased-input > exp_frequency/gauss/ddp_noise_eps/odo/0.1/out.log

done


python exp_frequency/compare-lambd.py