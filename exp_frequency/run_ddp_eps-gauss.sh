#!/bin/bash

epsilons=(0.1 0.2 0.3 0.4 0.5)


## gaussian
# odo
for eps in ${epsilons[@]}; do
    python compile.py -B 64 sampling_gaussian.mpc 0 4096 $eps 128
    bash Scripts/shamir-bmr.sh -v sampling_gaussian-0-4096-${eps}-128 -IF Player-Data/biased-input > exp_frequency/gauss/ddp_noise_eps/odo/${eps}/out.log
    
    # bash Scripts/yao.sh -v sampling_gaussian-0-4096-48.44-128 -IF Player-Data/biased-input > exp_frequency/gauss/ddp_noise_eps/odo/0.1/out.log

done


for eps in ${epsilons[@]}; do
    python compile.py -B 64 sampling_gaussian.mpc 0 4096 $eps 128
    bash Scripts/shamir-bmr.sh -v sampling_gaussian-0-4096-${eps}-128 -IF Player-Data/biased-input > exp_frequency/gauss/ddp_noise_eps/ostack1/${eps}/out.log
    
    # bash Scripts/yao.sh -v sampling_gaussian-0-4096-48.44-128 -IF Player-Data/biased-input > exp_frequency/gauss/ddp_noise_eps/odo/0.1/out.log

done

for eps in ${epsilons[@]}; do
    python main.mpc -B 64 --mechanism gauss --lambd 128 --n 4096 --ostack 0 --periodic 0 --epsilon $eps
    bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/biased-input > exp_frequency/gauss/ddp_noise_eps/odo/${eps}/out.log
done

# ostack1
for eps in ${epsilons[@]}; do
    python main.mpc -B 64 --mechanism gauss --lambd 128 --n 4096 --ostack 1 --periodic 0 --epsilon $eps
    bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/biased-input > exp_frequency/gauss/ddp_noise_eps/ostack1/${eps}/out.log
done


# ostack1
# for eps in ${epsilons[@]}; do
#     python main.mpc -B 64 --mechanism gauss --lambd 128 --n 4096 --ostack 1 --periodic 0 --epsilon $eps
#     bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/biased-input > exp_frequency/gauss/ddp_noise_eps/ostack1/${eps}/out.log
# done


# local dp and shuffle dp
# python exp_frequency/olh.py >> exp_frequency/ldp/olh_out.log
# python exp_frequency/olh_shuffle.py >> exp_frequency/ldp/olh_shuffle_out.log

# output comparison results to csv
# python exp_frequency/compare-epsilon.py
