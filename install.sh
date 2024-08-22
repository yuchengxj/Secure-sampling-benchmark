git clone https://github.com/data61/MP-SPDZ.git &&
cp -r MP-SPDZ/* . &&
rm -r MP-SPDZ &&
apt update
apt-get install -y automake build-essential clang cmake git libboost-dev libboost-iostreams-dev libboost-thread-dev libgmp-dev libntl-dev libsodium-dev libssl-dev libtool python3 &&
make setup &&
mkdir Player-Data &&
pip install -r requirements.txt &&
bash Scripts/setup-ssl.sh 16 &&
make -j8 shamir-bmr-party.x &&
make -j8 yao-party.x