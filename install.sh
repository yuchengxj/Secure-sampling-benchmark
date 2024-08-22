#!/bin/bash

conda create -y -n sampling-py python=3.9
conda activate sampling-py
conda install -y matplotlib==3.6.1 mpmath==1.3.0 numpy==1.22.4 scipy==1.7.1 pandas

git clone https://github.com/data61/MP-SPDZ.git &&
cp -r MP-SPDZ/* . &&
rm -r MP-SPDZ &&
apt update
apt-get install -y automake build-essential clang cmake git libboost-dev libboost-iostreams-dev libboost-thread-dev libgmp-dev libntl-dev libsodium-dev libssl-dev libtool python3 &&
make setup &&
bash Scripts/setup-ssl.sh 16 &&
make -j8 shamir-bmr-party.x &&
make -j8 yao-party.x