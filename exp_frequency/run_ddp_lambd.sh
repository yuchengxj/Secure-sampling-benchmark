#!/bin/bash

# lambdas=(16 32 64 128 256)
lambdas=(1)


## laplace
# odo
for lambd in ${lambdas[@]}; do
    echo "Running Laplace ODO with lambda = $lambd"
    python main.mpc -B 64 --mechanism lap --lambd $lambd --n 4096 --ostack 0 --periodic 1 --epsilon 0.1
    bash Scripts/shamir-bmr.sh -v test-sampling-main  > exp_frequency/lap/ddp_noise_lambd/odo/${lambd}/out.log
done

# ostack1
for lambd in ${lambdas[@]}; do
    echo "Running Laplace Ostack1 with lambda = $lambd"
    python main.mpc -B 64 --mechanism lap --lambd $lambd --n 4096 --ostack 1 --periodic 0 --epsilon 0.1
    bash Scripts/shamir-bmr.sh -v test-sampling-main  > exp_frequency/lap/ddp_noise_lambd/ostack1/${lambd}/out.log
done

# ostack2
for lambd in ${lambdas[@]}; do
    echo "Running Laplace Ostack2 with lambda = $lambd"
    python main.mpc -B 64 --mechanism lap --lambd $lambd --n 4096 --ostack 1 --periodic 1 --epsilon 0.1
    bash Scripts/shamir-bmr.sh -v test-sampling-main  > exp_frequency/lap/ddp_noise_lambd/ostack2/${lambd}/out.log
done

# dng
for lambd in ${lambdas[@]}; do
    echo "Running Laplace DNG with lambda = $lambd"
    python main.mpc -B 64 --mechanism lap --lambd $lambd --n 4096 --ostack 0 --periodic 1 --type dngsemi --epsilon 0.1
    bash Scripts/shamir-bmr.sh -v test-sampling-main -IF  > exp_frequency/lap/ddp_noise_lambd/dng/${lambd}/out.log
done

## gaussian
# odo
for lambd in ${lambdas[@]}; do
    echo "Running Gaussian ODO with lambda = $lambd"
    python main.mpc -B 64 --mechanism gauss --lambd $lambd --n 4096 --ostack 0 --periodic 1 --epsilon 0.1
    bash Scripts/shamir-bmr.sh -v test-sampling-main  > exp_frequency/gauss/ddp_noise_lambd/odo/${lambd}/out.log
done

# ostack1
for lambd in ${lambdas[@]}; do
    echo "Running Gaussian Ostack1 with lambda = $lambd"
    python main.mpc -B 64 --mechanism gauss --lambd $lambd --n 4096 --ostack 1 --periodic 0 --epsilon 0.1
    bash Scripts/shamir-bmr.sh -v test-sampling-main  > exp_frequency/gauss/ddp_noise_lambd/ostack1/${lambd}/out.log
done

# dng
for lambd in ${lambdas[@]}; do
    echo "Running Gaussian DNG with lambda = $lambd"
    python main.mpc -B 64 --mechanism gauss --lambd $lambd --n 4096 --ostack 0 --periodic 0 --type dngsemi --epsilon 0.1
    bash Scripts/shamir-bmr.sh -v test-sampling-main -IF  > exp_frequency/gauss/ddp_noise_lambd/dng/${lambd}/out.log
done

python exp_frequency/compare-lambd.py