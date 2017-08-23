#!/usr/bin/env python3
# coding=utf-8
import os
import sys
import fileinput
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

def main(fileName, textToSearch, textToReplace):
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == fileName:
               fileToSearch = os.path.join(root, file)
               with fileinput.FileInput(fileToSearch, inplace=True, backup='.bak') as currentFile:
                   for line in currentFile:
                       print(line.replace(textToSearch, textToReplace), end='')

if __name__ == "__main__":
    # Need to read the user manual @ https://docs.python.org/3/library/argparse.html
    parser=argparse.ArgumentParser(description="My Description. And what a lovely description it is.",
                                   epilog="All's well that ends well.")
    parser.add_argument('--replace-text', type=int, default=42, help='replace text1 to text2 in file')
    parser.add_argument('bar', nargs='*', default=[1, 2, 3], help='BAR!')
    args=parser.parse_args()
    main(sys.argv[1], sys.argv[2], sys.argv[3])
