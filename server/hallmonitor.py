#!/usr/bin/env python3

import pyinotify
import os
import subprocess
import configparser
import handler
import time
import glob
import ftncl
import signal
import errno

from contextlib import contextmanager

processes = {}

def handleIncoming(filename):
    print(filename)
    time.sleep(1)
    config = configparser.ConfigParser(strict=False, interpolation=None)
    config.read(filename)
    p = subprocess.Popen(["./handler.py", config["Job"]["url"], "--title",
            filename.split("/")[-1] + "---" + config["Job"]["title"], 
            "--rotation", config["Job"]["rx"], config["Job"]["ry"], 
            config["Job"]["rz"],  "--resolution", config["Job"]["width"], 
            config["Job"]["height"], "--output", "/tmp/panosteal"])
    processes[filename] = [p, time.time()]

class createHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        if "." not in event.pathname:
            try:
                handleIncoming(event.pathname)
            except Exception as e:
                with open(event.pathname + ".err", "w") as errorfile:
                    errorfile.write("")
                print(e)

def run():
    global processes

    watch = pyinotify.WatchManager()
    worker = pyinotify.ThreadedNotifier(watch, createHandler())
    worker.start()
    path = watch.add_watch("/tmp/panosteal", pyinotify.IN_CREATE)

    while True:
        try:
            for process, details in processes.items():
                if glob.glob("/tmp/panosteal/%s---*" % process):
                    del processes[process]
                    continue
                if time.time() - details[1] > 1200:
                    details[0].kill()
                if details[0].returncode is not None:
                    del processes[process]
                    with open("/tmp/panosteal/%s.err" % process, "w") as errorfile:
                        errorfile.write("")
        except Exception as e:
            raise
        finally:
            time.sleep(30)

@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        pass

    original_handler = signal.signal(signal.SIGALRM, timeout_handler)

    try:
        signal.alarm(seconds)
        yield

    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)

def create_lock():
    with timeout(1):
        fileobj = open('/tmp/panosteal/monitor.lock', 'w+')
        try:
            fcntl.flock(fileobj.fileno(), fcntl.LOCK_EX)
        except IOError as e:
            if e.errno != errno.EINTR:
                raise e
            exit("Already running - exiting")
        return fileobj
    exit("An error has occurred - exiting")

if __name__ == "__main__":
    create_lock()
    run()
