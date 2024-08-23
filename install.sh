#!/bin/bash

conda env remove -n sampling-py 
conda create -y -n sampling-py python=3.9 
conda install -n sampling-py   matplotlib mpmath numpy scipy pandas 

git clone https://github.com/data61/MP-SPDZ.git &&
cp -r MP-SPDZ/* . &&
sudo rm -r MP-SPDZ &&
sudo apt update
sudo apt-get install -y automake build-essential clang cmake git libboost-dev libboost-all-dev libboost-iostreams-dev libboost-thread-dev libgmp-dev libntl-dev libsodium-dev libssl-dev libtool python3 &&
sudo make setup &&
sudo bash Scripts/setup-ssl.sh 16 &&
make -j8 shamir-bmr-party.x &&
make -j8 yao-party.x