#!/bin/bash

# laplace ostack
# N=(16 64 256 1024 4096)
N=(4096)
# LAMBDAS=(64 128 256)
LAMBDAS=(128)
nparty=2
# remember to change the definition of MAX_N_PARTIES in BMR/config.h and rerun make -j 8 shamir-bmr-party.x 
dir="exp-party/logs-yao"
mkdir "$dir"
output_file="exp-party/logs-yao/ostack_lap.log"

# make -j 8 shamir-bmr-party.x
Scripts/setup-ssl.sh $nparty
# 开始循环
for lambd in "${LAMBDAS[@]}"; do
    for n in "${N[@]}"; do
        # 输出分隔符
        echo "Running with n=$n and lambd=$lambd" >> "$output_file"
        echo "========================================" >> "$output_file"
        python main.mpc -B 64 --num_party $nparty --type bitwise --mechanism lap --lambd $lambd --n $n --ostack 1 >> "$output_file"
        bash Scripts/yao.sh -v test-sampling-main -IF Player-Data/biased-input  >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
    done
done

# laplace periodic ostack
output_file="exp-party//logs-yao/periodic_lap.log"
# 开始循环
for lambd in "${LAMBDAS[@]}"; do
    for n in "${N[@]}"; do
        # 输出分隔符
        echo "Running with n=$n and lambd=$lambd" >> "$output_file"
        echo "========================================" >> "$output_file"
        python main.mpc -B 64 --num_party $nparty --type bitwise --mechanism lap --lambd $lambd --n $n --ostack 1 --periodic 1 >> "$output_file"
        bash Scripts/yao.sh -v test-sampling-main -IF Player-Data/biased-input  >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
    done
done

# laplace odo
output_file="exp-party//logs-yao/direct_lap.log"
# 开始循环
for lambd in "${LAMBDAS[@]}"; do
    for n in "${N[@]}"; do
        # 输出分隔符
        echo "Running with n=$n and lambd=$lambd" >> "$output_file"
        echo "========================================" >> "$output_file"
        python main.mpc -B 64 --num_party $nparty --type bitwise --mechanism lap --lambd $lambd --n $n --ostack 0 >> "$output_file"
        bash Scripts/yao.sh -v test-sampling-main -IF Player-Data/biased-input  >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
    done
done


# gaussian ostack
output_file="exp-party//logs-yao/ostack_gauss.log"
# 开始循环
for lambd in "${LAMBDAS[@]}"; do
    for n in "${N[@]}"; do
        # 输出分隔符
        echo "Running with n=$n and lambd=$lambd" >> "$output_file"
        echo "========================================" >> "$output_file"
        python main.mpc -B 64 --num_party $nparty --type bitwise --mechanism gauss --lambd $lambd --n $n --ostack 1 >> "$output_file"
        bash Scripts/yao.sh -v test-sampling-main -IF Player-Data/biased-input  >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
    done
done


# gaussian odo
output_file="exp-party//logs-yao/direct_gauss.log"
# 开始循环
for lambd in "${LAMBDAS[@]}"; do
    for n in "${N[@]}"; do
        # 输出分隔符
        echo "Running with n=$n and lambd=$lambd" >> "$output_file"
        echo "========================================" >> "$output_file"
        python main.mpc -B 64 --num_party $nparty --type bitwise --mechanism gauss --lambd $lambd --n $n --ostack 0 >> "$output_file"
        bash Scripts/yao.sh -v test-sampling-main -IF Player-Data/biased-input  >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
    done
done



# gaussian dng
output_file="exp-party//logs-yao/dng_gauss.log"
# 开始循环
for lambd in "${LAMBDAS[@]}"; do
    for n in "${N[@]}"; do
        # 输出分隔符
        echo "Running with n=$n and lambd=$lambd" >> "$output_file"
        echo "========================================" >> "$output_file"
        python main.mpc -B 64 --num_party $nparty --type dng --mechanism gauss --lambd $lambd --n $n --ostack 0 --periodic 1 --bin 1 >> "$output_file"
        bash Scripts/yao.sh -v test-sampling-main -IF Player-Data/client-input  >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
    done
done


# laplace dng
output_file="exp-party//logs-yao/dng_lap.log"
# 开始循环
for lambd in "${LAMBDAS[@]}"; do
    for n in "${N[@]}"; do
        # 输出分隔符
        echo "Running with n=$n and lambd=$lambd" >> "$output_file"
        echo "========================================" >> "$output_file"
        python main.mpc -B 64 --num_party $nparty --type dng --mechanism lap --lambd $lambd --n $n --ostack 0 --periodic 1 --bin 1 >> "$output_file"
        bash Scripts/yao.sh -v test-sampling-main -IF Player-Data/client-input  >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
    done
done