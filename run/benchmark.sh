#!/bin/bash
set -e

lstopo > lstopo
lscpu > lscpu
uname -a > uname

mkdir /tmp/$(whoami)

cd openems-python
./benchmark.sh
cd -
cd openems-octave
./benchmark.sh
cd -
