
import numpy as np
import os
import math
import re
import pandas as pd
from collections import defaultdict
import random

def count_frequencies(filename):
    frequencies = defaultdict(int)
    f = []
    with open(filename, "r") as file:
        for line in file:
            numbers = line.split()
            for num in numbers:
                frequencies[num] += 1
    for key, value in frequencies.items():
        f.append(value)
    f = np.array(f)
    print(f)
    np.random.shuffle(f)
    return f[:4096]

data = count_frequencies('exp_frequency/dataset/kosarak.txt')
ddp_log_path_gauss = 'exp_frequency/gauss/ddp_noise_eps/'
ddp_log_path_lap = 'exp_frequency/lap/ddp_noise_eps/'
ldp_log_path = 'exp_frequency/ldp/olh_out.log'
shuffle_dp_log_path = 'exp_frequency/ldp/olh_shuffle_out.log'


n_sample = data.shape[0]
sensitivity = 1
delta = 1e-5

def parse_ddp_log(path):
    
    numbers = []
    pattern = re.compile(r'^-?\d+$')  
    with open(path, 'r') as file:
        for line in file:
            line = line.strip()
            if pattern.match(line):  
                numbers.append(int(line))
    numbers = np.array(numbers)
    perturbed_data = numbers[-n_sample:] + data
    # print(np.var(numbers[-n_sample:]))s
    return query_MSE(perturbed_data, data)


def query_MSE(noised_res, res):  
    # noised_res = np.round(np.clip(noised_res, a_max=None, a_min=0))
    mse = np.mean((res - noised_res) ** 2)
    re = np.mean(np.abs((res - noised_res) / res)) * 100
    mae = np.mean(np.abs(res - noised_res))
    return [mse, re, mae]

def parse_ldp(filename):
    pattern = re.compile(r'^\s*-?\d+(\.\d+)?(?:\s+-?\d+(\.\d+)?)*\s*$')
    first_numbers = []  

    with open(filename, 'r') as file:
        for line in file:
            if pattern.fullmatch(line.strip()):  
                first_number = float(line.split()[0])  
                first_numbers.append([first_number]*3)

    # first_numbers_array = np.array(first_numbers)
    return first_numbers

def parse_ddp_log_gauss(path):
    numbers = []
    pattern = re.compile(r'^\d+,\s*(-?\d+)$')
    with open(path, 'r') as file:
        for line in file:
            line = line.strip()
            match = pattern.match(line)
            if match:  
                number = int(line.split(',')[1])
                acc = int(line.split(',')[0])
                if acc == 1:
                    number = number if random.random() < 0.5 else -number
                    numbers.append(number)
    numbers = np.array(numbers)
    # print(numbers)
    perturbed_data = numbers[-n_sample:] + data
    # print(np.var(numbers[-n_sample:]))s
    return query_MSE(perturbed_data, data)

if __name__ == '__main__':
    mses = []
    names = []

    ## cdp lap 
    mse_cdp_lap = []
    for eps in np.arange(0.1, 0.6, 0.1):
        t = sensitivity / eps
        noise = np.random.laplace(loc=0, scale=t, size=n_sample)
        perturbed_data = data + noise 
        mse_cdp_lap.append(query_MSE(perturbed_data, data))
    mses.append(mse_cdp_lap)
    names.append('lap' + '-' + 'cdp' )
        
    ## cdp gauss
    mse_cdp_gauss = []
    for eps in np.arange(0.1, 0.6, 0.1):
        noise = 0 
        sigma = sensitivity * math.sqrt(2 * math.log(1.25 / delta)) / eps
        # print(sigma)
        noise = np.round(np.random.normal(loc=0, scale=sigma, size=n_sample))
        perturbed_data = data + noise 
        mse_cdp_gauss.append(query_MSE(perturbed_data, data))
    mses.append(mse_cdp_gauss)
    names.append('gauss' + '-' + 'cdp' )

    ## ddp lap
    for name in os.listdir(ddp_log_path_lap):
        name_path = os.path.join(ddp_log_path_lap, name)
        mses_eps = []
        for e in [0.1, 0.2, 0.3, 0.4, 0.5]:
            eps = str(e)
            name_eps_path = os.path.join(name_path, eps) + '/out.log'
            mse = parse_ddp_log(name_eps_path)
            mses_eps.append(mse)
        mses.append(mses_eps)
        names.append('lap' + '-' + str(name))

    ## ddp gauss
    for name in os.listdir(ddp_log_path_gauss):
        name_path = os.path.join(ddp_log_path_gauss, name)
        mses_eps = []
        for e in [0.1, 0.2, 0.3, 0.4, 0.5]:
            eps = str(e)
            name_eps_path = os.path.join(name_path, eps) + '/out.log'
            # print(name)

            if name == 'odo' or name == 'ostack1':
                mse = parse_ddp_log_gauss(name_eps_path)
            else:
                mse = parse_ddp_log(name_eps_path)
            mses_eps.append(mse)
        mses.append(mses_eps)
        names.append('gauss' + '-' + str(name) )


    ## ldp and shuffle dp
    mses_ldp = parse_ldp(ldp_log_path)
    mses_shuffle = parse_ldp(shuffle_dp_log_path)
    mses.append(mses_ldp)
    mses.append(mses_shuffle)
    names.append('ldp')
    names.append('shuffle')

    # mses = np.array(mses)
    print([len(l) for l in mses])
    mses = np.array(mses)
    epsilons = [0.1, 0.2, 0.3, 0.4, 0.5]
    matrix = ['mse', 're', 'mae']
    for i in range(3):
        ans = mses[:, :, i]
        df = pd.DataFrame(ans, index=names, columns=epsilons)
        df.to_csv(f"exp_frequency/compare-{matrix[i]}-epsilon.csv")