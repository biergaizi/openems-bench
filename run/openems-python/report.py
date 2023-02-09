import os

for file in os.scandir():
    if file.name.endswith(".result"):
        os.system('grep -E "Benchmark|Speed: [0-9]" %s' % file.name)
