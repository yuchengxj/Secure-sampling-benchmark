#!/bin/bash

lambdas=(64 128 192 256)
epsilons=(0.001 0.01 0.1 1 10)

output_file="exps/out_exp1_dng_compile_eps.log"

> $output_file

for lambda in "${lambdas[@]}"; do
    for epsilon in "${epsilons[@]}"; do
        echo "Running with lambda = $lambda and epsilon = $epsilon" | tee -a $output_file
        python compile.py -B 64 distributed_sampler/dng_dlap.mpc $lambda 4096 $epsilon | tee -a $output_file
    done
done

echo "Script finished!" | tee -a $output_file

output_file="exps/out_exp1_dng_compile_gauss_eps.log"

> $output_file

for lambda in "${lambdas[@]}"; do
    for epsilon in "${epsilons[@]}"; do
        echo "Running with lambda = $lambda and epsilon = $epsilon" | tee -a $output_file
        python compile.py -B 64 distributed_sampler/dng_gauss.mpc $lambda 4096 $epsilon | tee -a $output_file
    done
done

echo "Script finished!" | tee -a $output_file


> exps/out_exp1_trans_compile_esp.log
for lambda in "${lambda_values[@]}"
do
    for epsilon in "${epsilon_values[@]}"
    do
        echo "Executing for lambda=$lambda and epsilon=$epsilon" >> exps/out_exp1_trans_compile_esp.log
        
        python compile.py -B 64 transformation/trans_dlap.mpc $lambda 4096 $epsilon >> exps/out_exp1_trans_compile_esp.log
        
        echo "--------------------------------------------" >> exps/out_exp1_trans_compile_esp.log
    done
done


## gauss
output_file="exps/out_exp1_dng_compile_gauss_eps.log"

> $output_file

for lambda in "${lambdas[@]}"; do
    for epsilon in "${epsilons[@]}"; do
        echo "Running with lambda = $lambda and epsilon = $epsilon" | tee -a $output_file
        python compile.py -B 64 distributed_sampler/dng_gauss.mpc $lambda 4096 $epsilon | tee -a $output_file
    done
done

echo "Script finished!" | tee -a $output_file

## lap
output_file="exps/out_exp1_dng_compile_eps.log"

> $output_file

for lambda in "${lambdas[@]}"; do
    for epsilon in "${epsilons[@]}"; do
        echo "Running with lambda = $lambda and epsilon = $epsilon" | tee -a $output_file
        python compile.py -B 64 distributed_sampler/dng_dlap.mpc $lambda 4096 $epsilon | tee -a $output_file
    done
done

echo "Script finished!" | tee -a $output_file
