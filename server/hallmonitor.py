#!/usr/bin/env python3

import pyinotify
import os
import subprocess
import configparser
import handler
import time
import glob

processes = {}

def handleIncoming(filename):
    time.sleep(1)
    config = configparser.ConfigParser()
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

if __name__ == "__main__":
    run()
