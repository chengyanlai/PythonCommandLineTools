#!/usr/bin/env python
# coding=utf-8
import os
import sys
import subprocess
import re

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def checkIfRunning():
    f = open("job", "r")
    for line in f:
        text = re.search("(.*)(--job-name=)(.*)", line)
        if text:
            jobName = text.groups()[2]
    f.close()
    if jobName:
        # Get squeue results
        qme = subprocess.run(['squeue', '-u', 'chengyanlai', '-o', '"%.10i %.9P %.30j %.15u %.2t %.13M %.9l %.6D %R"'], stdout=subprocess.PIPE).stdout.decode("utf-8").split("\n")
        # Search jobName
        for line in qme:
            if jobName in line:
                return True
    return False
         
def main(action="show"):
    folder_list = [f for f in os.listdir() if os.path.isdir(f)]
    for folder in folder_list:
        with cd(folder):
            if os.path.isfile("DONE"):
                continue
            else:
                if action == "qsub":
                    if checkIfRunning():
                       command = "pwd;echo \' is running or queuing\'"
                    else:
                       command = "pwd"#"sbatch --qos=long job;sleep 1"
                else:
                    command = "pwd"
                subprocess.call(command, shell=True)

if __name__ == "__main__":
    main(action=sys.argv[1])
