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
user = getpass.getuser()

print("Hostname, User, Script, Trial, Threads, Speed")
for file in chain(os.scandir("openems-python"), os.scandir("openems-octave"), os.scandir("pyems")):
    for i in range(0, 4):
        if file.name.endswith(".result.%d" % i):
            script_name = ".".join([file.name.split(".")[0], file.name.split(".")[1]])
            trial = file.name.split(".result.")[-1]
            for threads, speed in parse_result(file):
                print("%s, %s, %s, %s, %d, %.2f" % (hostname, user, script_name, trial, threads, speed))
