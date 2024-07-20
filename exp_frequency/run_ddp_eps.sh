#!/bin/bash

epsilons=(0.1 0.2 0.3 0.4 0.5)


## laplace
# odo
for eps in ${epsilons[@]}; do
    python main.mpc -B 64 --mechanism lap --lambd 128 --n 41270 --ostack 0 --periodic 1 --epsilon $eps
    bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/biased-input > exp_frequency/lap/ddp_noise_eps/odo/${eps}/out.log
done

# ostack1
for eps in ${epsilons[@]}; do
    python main.mpc -B 64 --mechanism lap --lambd 128 --n 41270 --ostack 1 --periodic 0 --epsilon $eps
    bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/biased-input > exp_frequency/lap/ddp_noise_eps/ostack1/${eps}/out.log
done

# ostack2
for eps in ${epsilons[@]}; do
    python main.mpc -B 64 --mechanism lap --lambd 128 --n 41270 --ostack 1 --periodic 1 --epsilon $eps
    bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/biased-input > exp_frequency/lap/ddp_noise_eps/ostack2/${eps}/out.log
done

# dng
for eps in ${epsilons[@]}; do
    python main.mpc -B 64 --mechanism lap --lambd 128 --n 41270 --ostack 0 --periodic 1 --type dngsemi --epsilon $eps
    bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/client-input > exp_frequency/lap/ddp_noise_eps/dng/${eps}/out.log
done

## gaussian
# odo
for eps in ${epsilons[@]}; do
    python main.mpc -B 64 --mechanism gauss --lambd 128 --n 41270 --ostack 0 --periodic 1 --epsilon $eps
    bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/biased-input > exp_frequency/gauss/ddp_noise_eps/odo/${eps}/out.log
done

# ostack1
for eps in ${epsilons[@]}; do
    python main.mpc -B 64 --mechanism gauss --lambd 128 --n 41270 --ostack 1 --periodic 0 --epsilon $eps
    bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/biased-input > exp_frequency/gauss/ddp_noise_eps/ostack1/${eps}/out.log
done

# dng
for eps in ${epsilons[@]}; do
    python main.mpc -B 64 --mechanism gauss --lambd 128 --n 41270 --ostack 0 --periodic 0 --type dngsemi --epsilon $eps
    bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/client-input > exp_frequency/gauss/ddp_noise_eps/dng/${eps}/out.log
done

# local dp and shuffle dp
python exp_frequency/olh.py >> exp_frequency/ldp/olh_out.log
python exp_frequency/olh_shuffle.py >> exp_frequency/ldp/olh_shuffle_out.log

# output comparison results to csv
python exp_frequency/compare-epsilon.py
