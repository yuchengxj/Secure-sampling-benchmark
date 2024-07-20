#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created by tianhao.wang at 9/18/18

"""
import numpy as np
from fo.fo import FO
import gc

def generate_ue(domain, datum, samples_one, p, q):
    samples_zero = np.random.random_sample(domain)
    y = np.zeros(domain, dtype=np.int32)

    y[samples_zero < q] = 1

    y[datum] = 1 if samples_one < p else 0

    perturbed_datas = y.copy()  
    # del samples_zero, y
    # gc.collect()
    return perturbed_datas


class UE(FO):

    def init_e(self, eps, domain):
        self.ee = np.exp(eps)
        self.p = 0.5
        self.q = 1 / (self.ee + 1)
        self.var = 4 * self.ee / (self.ee - 1) ** 2
    

    
    def perturb(self, datas, domain):
        n = len(datas)
        perturbed_datas = np.zeros(domain)
        samples_one = np.random.random_sample(n)

        for i in range(n):
            perturbed_datas += generate_ue(domain, datas[i], samples_one[i], self.p, self.q)


        return perturbed_datas

    def support_sr(self, report, value):
        return report[value] == 1

    def aggregate(self, domain, perturbed_datas):
        ESTIMATE_DIST = perturbed_datas
        return ESTIMATE_DIST
