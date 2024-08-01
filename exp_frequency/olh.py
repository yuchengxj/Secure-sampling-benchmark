import argparse
import math
import numpy as np
import xxhash
from fo.fo_factory import FOFactory
domain = 0
epsilon = 0.0
n = 0
g = 0
X = []
Y = []
REAL_DIST = []
ESTIMATE_DIST = []

def load_data(filepath):
    with open(filepath, 'r') as file:
        data = file.read().split()
    data = list(map(int, data))
    return data

def generate_dist_from_data(filepath):
    global X, REAL_DIST, domain, n
    data = load_data(filepath)
    domain = max(data) + 1
    n = len(data)
    X = np.array(data)
    REAL_DIST = np.zeros(domain)
    for number in X:
        REAL_DIST[number] += 1
    print(f'domain size: {domain}, number of users: {len(X)}')

# def perturb():
#     global Y
#     Y = np.zeros(n)
#     for i in range(n):
#         v = X[i]
#         x = (xxhash.xxh32(str(v), seed=i).intdigest() % g)
#         y = x
#         p_sample = np.random.random_sample()
#         if p_sample > p - q:
#             y = np.random.randint(0, g)
#         Y[i] = y

# def aggregate():
#     global ESTIMATE_DIST
#     ESTIMATE_DIST = np.zeros(domain)
#     for i in range(n):
#         print(i)
#         for v in range(domain):
#             if Y[i] == (xxhash.xxh32(str(v), seed=i).intdigest() % g):
#                 ESTIMATE_DIST[v] += 1
#     a = 1.0 * g / (p * g - 1)
#     b = 1.0 * n / (p * g - 1)
#     ESTIMATE_DIST = a * ESTIMATE_DIST - b

def error_metric(est, real):
    abs_error = 0.0
    for x in range(domain):
        abs_error += np.abs(est[x] - real[x]) ** 2
    return abs_error / domain

def main():
    generate_dist_from_data(args.filepath)
    results = np.zeros(args.exp_round)
    oue = FOFactory.create_fo('ue', args, args.epsilon, domain)
    oue.init_e(args.epsilon, domain)
    for i in range(args.exp_round):
        print(f'round: {i}')
        perturb_datas = oue.perturb(X, domain)
        ESTIMATE_DIST = oue.aggregate(domain, perturb_datas)
        results[i] = error_metric(ESTIMATE_DIST, REAL_DIST)
    print(np.mean(results), np.std(results))
    print()

def dispatcher():
    global g
    for e in np.arange(0.5, 0.6, 0.1):
        print(e, end=' ')
        args.epsilon = float(e)
        g = args.projection_range
        g = int(round(math.exp(args.epsilon))) + 1
        print(g, end=' ')
        main()

parser = argparse.ArgumentParser(description='Comparison of different privacy schemes.')
parser.add_argument('--filepath', type=str, default='exp_frequency/dataset/kosarak.txt', help='Path to the data file')
parser.add_argument('--domain', type=int, default=1024, help='specify the domain of the representation of domain')
parser.add_argument('--exp_round', type=int, default=10, help='specify the iterations for the experiments, default 10')
parser.add_argument('--epsilon', type=float, default=2, help='specify the differential privacy parameter, epsilon')
parser.add_argument('--projection_range', type=int, default=2, help='specify the domain for projection')
args = parser.parse_args()
dispatcher()
