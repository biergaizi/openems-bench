#!/bin/bash
set -e

lstopo > lstopo
lscpu > lscpu
uname -a > uname

cd openems-python
./benchmark.sh
cd -
cd openems-octave
./benchmark.sh
cd -
