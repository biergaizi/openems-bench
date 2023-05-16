import sys
import os, getpass, socket
from itertools import chain

def parse_result(file):
    file = open(file, "r")

    threads = -1
    speed = -1
    retval = []
    for line in file.readlines():
        if line.startswith("Benchmark"):
            threads = line.split()[3]
        if line.startswith("Speed:  "):
            continue
        if line.startswith("Speed: "):
            speed = line.split()[1]
            if threads == -1 or speed == -1:
                raise ValueError
            retval += [[int(threads), float(speed)]]
    return retval


hostname = socket.gethostname()

print("Hostname, Target, Script, Trial, Threads, Speed")
for target in os.scandir("./result"):
    if not target.is_dir():
        continue

    for file in chain(
            os.scandir(target.path + "/openems-python"),
            os.scandir(target.path + "/openems-octave"),
            os.scandir(target.path + "/pyems")
    ):
        for i in range(0, 4):
            if file.name.endswith(".result.%d" % i):
                script_name = ".".join([file.name.split(".")[0], file.name.split(".")[1]])
                trial = file.name.split(".result.")[-1]
                for threads, speed in parse_result(file):
                    print("%s, %s, %s, %s, %d, %.2f" % (hostname, target.name, script_name, trial, threads, speed))
