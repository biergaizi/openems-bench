import sys
import os
import threading
from time import sleep

lock = threading.Lock()

def _abort(sim_dir, seconds):
    # start evil Unix hack

    # create a pipe
    fd_read, fd_write = os.pipe()
    pipe_read = os.fdopen(fd_read, "r", buffering=1)
    pipe_write = os.fdopen(fd_write, "w", buffering=1)

    # redirect stdout to pipe
    old_stdout_fd = os.dup(1)
    os.dup2(fd_write, 1)

    # inspect stdout and reprint it via stderr
    while True:
        line = pipe_read.readline()
        if line.startswith("[@"):
            print(line, end="", file=sys.stderr)
            print("abort_after(): will abort simulation after %d seconds" 
                  % seconds, file=sys.stderr)

            # undo redirection
            os.dup2(old_stdout_fd, 1)
            break
        else:
            print(line, end="", file=sys.stderr)

    lock.acquire()

    lock.acquire(timeout=seconds)
    f = open(sim_dir + "/ABORT", "w+")
    f.close()

    lock.release()

def abort_after(sim, seconds):
    thread = threading.Thread(group=None, target=_abort, args=(sim.sim_dir, seconds))
    thread.start()

def abort_cleanup(sim):
    try:
        lock.release()
    except RuntimeError:
        pass

    max_try = 10
    while max_try > 0:
        sleep(1)

        try:
            max_try -= 1
            os.remove(sim.sim_dir + "/ABORT")
            break
        except FileNotFoundError:
            pass
