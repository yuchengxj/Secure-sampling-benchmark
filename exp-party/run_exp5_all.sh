#!/bin/bash

N=(4096)
# N=(4096)
LAMBDAS=(64 128 256)
LAMBDAS=(128)
nparty=3
# remember to change the definition of MAX_N_PARTIES in BMR/config.h and rerun make -j 8 shamir-bmr-party.x 
dir="exp-party/logs-bmr-${nparty}"
mkdir "$dir"

make -j 8 shamir-bmr-party.x
Scripts/setup-ssl.sh $nparty

# laplace ostack
output_file="exp-party/logs-bmr-${nparty}/ostack_lap.log"
for lambd in "${LAMBDAS[@]}"; do
    for n in "${N[@]}"; do
        echo "Running with n=$n and lambd=$lambd" >> "$output_file"
        echo "========================================" >> "$output_file"
        python main.mpc -B 64 --num_party $nparty --type bitwise --mechanism lap --lambd $lambd --n $n --ostack 1 >> "$output_file"
        bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/biased-input -N $nparty >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
    done
done

# laplace periodic ostack
output_file="exp-party//logs-bmr-${nparty}/periodic_lap.log"
for lambd in "${LAMBDAS[@]}"; do
    for n in "${N[@]}"; do
        echo "Running with n=$n and lambd=$lambd" >> "$output_file"
        echo "========================================" >> "$output_file"
        python main.mpc -B 64 --num_party $nparty --type bitwise --mechanism lap --lambd $lambd --n $n --ostack 1 --periodic 1 >> "$output_file"
        bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/biased-input -N $nparty >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
    done
done

# laplace odo
output_file="exp-party//logs-bmr-${nparty}/direct_lap.log"
for lambd in "${LAMBDAS[@]}"; do
    for n in "${N[@]}"; do
        echo "Running with n=$n and lambd=$lambd" >> "$output_file"
        echo "========================================" >> "$output_file"
        python main.mpc -B 64 --num_party $nparty --type bitwise --mechanism lap --lambd $lambd --n $n --ostack 0 >> "$output_file"
        bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/biased-input -N $nparty >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
    done
done


# gaussian ostack
output_file="exp-party//logs-bmr-${nparty}/ostack_gauss.log"
for lambd in "${LAMBDAS[@]}"; do
    for n in "${N[@]}"; do
        echo "Running with n=$n and lambd=$lambd" >> "$output_file"
        echo "========================================" >> "$output_file"
        python main.mpc -B 64 --num_party $nparty --type bitwise --mechanism gauss --lambd $lambd --n $n --ostack 1 >> "$output_file"
        bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/biased-input -N $nparty >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
    done
done


# gaussian odo
output_file="exp-party//logs-bmr-${nparty}/direct_gauss.log"
for lambd in "${LAMBDAS[@]}"; do
    for n in "${N[@]}"; do
        echo "Running with n=$n and lambd=$lambd" >> "$output_file"
        echo "========================================" >> "$output_file"
        python main.mpc -B 64 --num_party $nparty --type bitwise --mechanism gauss --lambd $lambd --n $n --ostack 0 >> "$output_file"
        bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/biased-input -N $nparty >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
    done
done



# gaussian dng
output_file="exp-party//logs-bmr-${nparty}/dng_gauss.log"
for lambd in "${LAMBDAS[@]}"; do
    for n in "${N[@]}"; do
        echo "Running with n=$n and lambd=$lambd" >> "$output_file"
        echo "========================================" >> "$output_file"
        python main.mpc -B 64 --num_party $nparty --type dng --mechanism gauss --lambd $lambd --n $n --ostack 0 --periodic 1 --bin 1 >> "$output_file"
        bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/client-input -N $nparty >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
    done
done


# laplace dng
output_file="exp-party//logs-bmr-${nparty}/dng_lap.log"
for lambd in "${LAMBDAS[@]}"; do
    for n in "${N[@]}"; do
        echo "Running with n=$n and lambd=$lambd" >> "$output_file"
        echo "========================================" >> "$output_file"
        python main.mpc -B 64 --num_party $nparty --type dng --mechanism lap --lambd $lambd --n $n --ostack 0 --periodic 1 --bin 1 >> "$output_file"
        bash Scripts/shamir-bmr.sh -v test-sampling-main -IF Player-Data/client-input -N $nparty >> "$output_file"
        echo "----------------------------------------" >> "$output_file"
    done
done