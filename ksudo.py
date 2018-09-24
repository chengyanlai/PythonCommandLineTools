#!/usr/bin/env python3
# coding=utf-8
import os
import sys
import subprocess
import fileinput
import re
import argparse
import glob
import getopt
import getpass

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def ReplaceText(filename, textToSearch, textToReplace):
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == filename:
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
        qme = subprocess.run(['squeue', '-u', getpass.getuser(), '-o', '"%.15i %.9P %.30j %.15u %.2t %.13M %.9l %.6D %R"'],
        stdout=subprocess.PIPE).stdout.decode("utf-8").split("\n")
        for line in qme[1:(-1)]:
            queue.append(line.split()[3])
    return queue

def getJobName(filename="job"):
    try:
        f = open(filename, "r")
    except FileNotFoundError:
        return ""
    except:
        raise
    for line in f:
        text1 = re.search("(.*)(-N )(.*)", line)
        text2 = re.search("(.*)(--job-name=)(.*)", line)
        if text1:
            return text1.groups()[2].strip()
        elif text2:
            return text2.groups()[2].strip()
    f.close()
    print("No jobName found in file ", filename)
    return ""

def getFolders(pattern=""):
    if pattern:
        return [f for f in glob.glob(pattern) if os.path.isdir(f)]
    else:
        return [f for f in os.listdir() if os.path.isdir(f)]

def SubmitQueue(filename, queueSystem, queueArgs, pattern=""):
    # Default stuff
    qsubCommand = {"torque": "qsub", "pbs": "qsub", "slurm": "sbatch"}
    qsubEscape = {"torque": "-", "pbs": "-", "slurm": "--"}
    # Get all running and queuing
    Queue = getQueueing(queueSystem=queueSystem)
    folder_list = getFolders(pattern)
    for folder in folder_list:
        with cd(folder):
            if len(glob.glob("DONE*")):
                print(folder + " is DONE.")
                continue
            else:
                jobName = getJobName(filename)
                if any(jobName in s for s in Queue):
                    print(jobName + " is running or queuing.")
                else:
                    if len(queueArgs) and jobName:
                        Args = ""
                        for s in queueArgs:
                            Args += qsubEscape[queueSystem] + s + " "
                        command = qsubCommand[queueSystem] + " " + Args + filename + ";sleep 1"
                        # print(command)
                        subprocess.call(command, shell=True)
                    else:
                        print(jobName + " is not running and not finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="ksudo", usage='%(prog)s [options] -f file',
                                     description="Chenyen's personal command to make life easier.",
                                     epilog="All's well that ends well.")
    parser.add_argument('-a', '--action', metavar='action', type=str, default="sj", choices=['sj', 'rt'], required=True, help='Choose to do submit job (sj) or replace text (rt).')
    # For replace text
    parser.add_argument('-s', '--search', metavar='TextToSearch', type=str, default="", help='If action=rt, search this text.')
    parser.add_argument('-r', '--replace', metavar='TextToReplace', type=str, help='If action=rt, replace TextToSearch to this text.')
    # For submit job
    parser.add_argument('-qs', '--queue-system', metavar='queue-system', type=str, default='torque', choices=['slurm', 'pbs', 'torque'], help='Set the queueing system. Default: torque.')
    parser.add_argument('-qa', '--queue-arguments', metavar='queue-arguments', nargs="+", type=str, default=[], help='Set the queue arguments.')
    parser.add_argument('-f', '--file', default='job', help='It is either the job script to submit or the file to search and replace text.')
    args = vars(parser.parse_args())
    if args["action"] == "rt":
        ReplaceText(filename=args["file"], textToSearch=args["search"], textToReplace=args["replace"])
    elif args["action"] == "sj":
        SubmitQueue(filename=args["file"], queueSystem=args["queue_system"], queueArgs=args["queue_arguments"], pattern=args["search"])
