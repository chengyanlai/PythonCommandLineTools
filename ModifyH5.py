#!/usr/bin/env python3
# coding=utf-8
import os
import sys
import numpy as np
import h5py
import cmd

class H5Modify(cmd.Cmd):
  intro = 'Modify HDF5 files. Type help or ? to list commands.\n'
  prompt = '(H5PY) '

  def do_open(self, filename):
    """ open [filename]
    Open the file"""
    if os.path.isfile(filename):
      self.filename = filename
      self.file = h5py.File(self.filename, 'r+')
    else:
      print('No such file - ', filename)

  def do_close(self):
    """ close [filename]
    Close the file"""
    self.file.close()

  def dset(self, name):
    self.name = str(name)

  def do_show(self, name):
    """ show [name]
    Show dataset name's data """
    self.dset(name)
    if self.name in self.file:
      data = self.file[self.name][()]
      print("In group -", name, "value is", data)
    else:
      print(self.file)
      print("No such group - ", self.name)

  def do_delete(self, name):
    """ delete [name]
    Delete dataset name"""
    self.dset(name)
    if self.name in self.file:
      del self.file[self.name]
    else:
      print("No such group - ", self.name)

  def do_create(self, s):
    """ create [name] [data] [dtype]
    Create dataset with data """
    l = s.split()
    if len(l) != 3:
       print("*** invalid number of arguments")
       return
    if l[2] == 'i8':
      val = np.int(l[1])
    elif l[2] == 'f':
      val = np.float64(l[1])
    self.dset(l[0])
    if self.name in self.file:
      print("Dataset -", self.name, "is exist, will be deleted.")
      del self.file[self.name]
      self.file.create_dataset(self.name, data=val, dtype=l[2])
      print("Dataset -", self.name, "is", val)
    else:
      print(type(val))
      self.file.create_dataset(self.name, data=val, dtype=l[2])
      print("Dataset -", self.name, "is", val)

  def do_copy(self, s):
    """ copy [filename] [set/group prefix] [loop_from=0] [loop_to=0] [step=0]
    Copy dataset(s)/group(s) to file. """
    l = s.split()
    file = str(l[0])
    prefix = str(l[1])
    FileToWrite = h5py.File(file, 'a')
    if len(l) == 2:
      self.file.copy(prefix, FileToWrite)
    elif len(l) == 5:
      LoopFrom = np.int(l[2])
      LoopTo = np.int(l[3])
      Step = np.int(l[4])
      for i in range(LoopFrom, LoopTo, Step):
        gname = prefix + str(i)
        print("Copy " + gname, end="...\t")
        self.file.copy(gname, FileToWrite)
        print("DONE!")
    FileToWrite.close()

  def do_eof(self, line):
    return True

if __name__ == '__main__':
    H5Modify().cmdloop()
# if __name__ == "__main__":
#   if sys.argv[1] == 'tf':
#     if len(sys.argv) > 3:
#       ChangeTf(sys.argv[2], np.float(sys.argv[3]))
#     elif len(sys.argv) <= 3:
#       ChangeTf(sys.argv[2])
#   elif sys.argv[1] == 'err':
#     if len(sys.argv) > 3:
#       AddErrorTol(sys.argv[2], np.float(sys.argv[3]))
#     elif len(sys.argv) <= 3:
#       AddErrorTol(sys.argv[2])
#   else:
#     print(len(sys.argv), sys.argv[1], 'WHAT!!')
