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

def getQueueing(queueSystem="torque"):
    queue = []
    if queueSystem == "torque":
        qme = subprocess.run(["qstat", "-r"], stdout=subprocess.PIPE).stdout.decode("utf-8").split("\n")
        for line in qme:
            text = re.search("(.*)(Full jobname:)(.*)", line)
            try:
                queue.append(text.groups()[2].strip())
            except AttributeError:
                pass
            except:
                raise
    elif queueSystem == "pbs":
        qme = subprocess.run(["qstat", "-f"], stdout=subprocess.PIPE).stdout.decode("utf-8").split("\n")
        for line in qme:
            text = re.search("(.*)(Job_Name =)(.*)", line)
            try:
                queue.append(text.groups()[2].strip())
            except AttributeError:
                pass
            except:
                raise
    elif queueSystem == "slurm":
        qme = subprocess.run(['squeue', '-u', 'chengyanlai', '-o', '"%.15i %.9P %.30j %.15u %.2t %.13M %.9l %.6D %R"'], stdout=subprocess.PIPE).stdout.decode("utf-8").split("\n")
        for line in qme[1:(-1)]:
            queue.append(line.split()[3])
    return queue

def getJobName(filename="job"):
    f = open(filename, "r")
    for line in f:
        text1 = re.search("(.*)(-N)(.*)", line)
        text2 = re.search("(.*)(--job-name=)(.*)", line)
        if text1:
            return text1.groups()[2].strip()
        elif text2:
            return text2.groups()[2].strip()
    f.close()
    print("No jobName found in file ", filename)
    return NULL

def resubmit(queueSystem, action="show", queue="standard"):
    # get all running and queuing
    Queue = getQueueing(queueSystem=queueSystem)
    folder_list = [f for f in os.listdir() if os.path.isdir(f)]
    for folder in folder_list:
        with cd(folder):
            if os.path.isfile("DONE"):
                print(folder + " is DONE.")
                continue
            else:
                jobName = getJobName()
                if any(jobName in s for s in Queue):
                    print(jobName + " is running or queuing.")
                elif action == "show":
                    print(jobName + " is not running and not finished.")
                else:
                    if queueSystem == "torque" or  queueSystem == "pbs":
                        qsubCommand = "qsub -q "
                    elif queueSystem == "slurm":
                        qsubCommand = "sbatch --qos="
                    else:
                        print("the queueing system is not supported!")
                        continue
                    command = qsubCommand + queue + " job;sleep 1"
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
        resubmit(sys.argv[2], action=action, queue=queue)
