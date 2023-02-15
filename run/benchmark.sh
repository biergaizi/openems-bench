#!/bin/bash
set -e

lstopo > lstopo
lscpu > lscpu
uname -a > uname

mkdir /tmp/$(whoami)

cd pyems
./benchmark.sh
cd -
cd openems-python
./benchmark.sh
cd -
cd openems-octave
./benchmark.sh
cd -

rm -rf /tmp/$(whoami)

python3 report.py > result.csv
