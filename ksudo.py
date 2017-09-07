#!/usr/bin/env python3
# coding=utf-8
import os
import sys
import subprocess
import fileinput
import re
import argparse

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def ReplaceText(fileName, textToSearch, textToReplace):
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == fileName:
               fileToSearch = os.path.join(root, file)
               with fileinput.FileInput(fileToSearch, inplace=True, backup='.bak') as currentFile:
                   for line in currentFile:
                       print(line.replace(textToSearch, textToReplace), end='')

def checkIfRunningTorque():
    f = open("job", "r")
    for line in f:
        text = re.search("(.*)(-N)(.*)", line)
        if text:
            jobName = text.groups()[2]
    f.close()
    if jobName:
        qme = subprocess.run(["qstat", "-r"], stdout=subprocess.PIPE).stdout.decode("utf-8").split("\n")
        for line in qme:
            if jobName in line:
                return True
    return False

def checkIfRunningPBS():
    f = open("job", "r")
    for line in f:
        text = re.search("(.*)(-N )(.*)", line)
        if text:
            jobName = text.groups()[2]
    f.close()
    if jobName:
        qme = subprocess.run(["qstat", "-f"], stdout=subprocess.PIPE).stdout.decode("utf-8").split("\n")
        Queue = []
        for line in qme:
            text2 = re.search("(.*)(Job_Name = )(.*)", line)
            try:
                Queue.append(text2.groups()[2])
            except AttributeError:
                pass
            except:
                raise
        if any(jobName in s for s in Queue):
            return True
    return False

def resubmitPBS(CheckFunction, action="show", queue="standard"):
    folder_list = [f for f in os.listdir() if os.path.isdir(f)]
    for folder in folder_list:
        with cd(folder):
            if os.path.isfile("DONE"):
                continue
            else:
                if CheckFunction():
                    command = "echo $(pwd)\' is running or queuing\'"
                elif action == "show":
                    command = "echo $(pwd)\' will be submmitted\'"
                elif action == "qsub":
                    command = "sbatch --qos=" + queue + " job;sleep 1"
                subprocess.call(command, shell=True)

def checkIfRunningSlurm():
    f = open("job", "r")
    for line in f:
        text = re.search("(.*)(--job-name=)(.*)", line)
        if text:
            jobName = text.groups()[2]
            break
    f.close()
    if jobName:
        # Get squeue results
        qme = subprocess.run(['squeue', '-u', 'chengyanlai', '-o', '"%.10i %.9P %.30j %.15u %.2t %.13M %.9l %.6D %R"'], stdout=subprocess.PIPE).stdout.decode("utf-8").split("\n")
        # Search jobName
        for line in qme:
            if jobName in line:
                return True
    return False

def resubmitSlurm(action="show", queue="standard"):
    folder_list = [f for f in os.listdir() if os.path.isdir(f)]
    for folder in folder_list:
        with cd(folder):
            if os.path.isfile("DONE"):
                continue
            else:
                if checkIfRunningSlurm():
                    command = "echo $(pwd)\' is running or queuing\'"
                elif action == "show":
                    command = "echo $(pwd)\' will be submmitted\'"
                elif action == "qsub":
                    command = "sbatch --qos=" + queue + " job;sleep 1"
                subprocess.call(command, shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="ksudo", usage='%(prog)s [options]',
                                     description="My Description. And what a lovely description it is.",
                                     epilog="All's well that ends well.")
    parser.add_argument('-rt', '--ReplaceText', nargs=3, metavar=('filename', 'textToSearch', 'textToReplace'), type=str, default=['job', 'standard', 'standard'], help='Replace textToSearch to textToReplace in file.')#, dest='cmd', action='store_const', const=test)
    parser.add_argument('-rs', '--resubmit', metavar=['pbs', 'show', 'std.q'], nargs="+", type=str, default=['pbs', 'show', 'std.q'], help='Resubmit jobs to queue.')
    # parser.add_argument('bar', nargs='*', default=[1, 2, 3], help='BAR!')
    parsed_args = parser.parse_args()
    if sys.argv[1] == "--ReplaceText" or sys.argv[1] == "-rt":
        assert len(sys.argv) == 5, print("Too less arguments")
        ReplaceText(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "--resubmit" or sys.argv[1] == "-rs":
        assert len(sys.argv) > 2, print("Too less arguments")
        if len(sys.argv) < 4:
          action = "show"
          queue = "std.q"
        else:
          action = sys.argv[3]
          if len(sys.argv) < 5:
              queue = "std.q"
          else:
              queue = sys.argv[4]
        if sys.argv[2] == "slurm":
            resubmitSlurm(action=action, queue=queue)
        elif sys.argv[2] == "pbs":
            resubmitPBS(checkIfRunningPBS, action=action, queue=queue)
        elif sys.argv[2] == "torque":
            resubmitPBS(checkIfRunningTorque, action=action, queue=queue)
        else:
            print("Supportive queuing systems - slurm, pbs.")
