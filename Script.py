#!/usr/bin/env python
# coding=utf-8
import os
import argparse

def GenerateScript(QueueingSystem, Filename, JobName, Executable, FolderName, Nodes=1, NumCore=1, WallTime='48:00:00', Partition='', ProjectName='', MPI=0, PPN=1, umask='022'):
    JobScript = ["#!/bin/bash",]
    if QueueingSystem == "PBS":
        JobScript.append("#PBS -V")
        JobScript.append("#PBS -o pbs.out")
        JobScript.append("#PBS -j oe")
        JobScript.append("##PBS -t # Job array ONLY")
        JobScript.append("".join(["#PBS -l nodes=", str(Nodes), ":ppn=", str(NumCore)]))
        JobScript.append("".join(["#PBS -l walltime=", WallTime]))
        JobScript.append("".join(["#PBS -d ", FolderName]))
        JobScript.append("".join(["#PBS -N ", JobName]))
        JobScript.append("cd $PBS_O_WORKDIR")
        JobScript.append("##cd $PBS_O_WORKDIR/$PBS_ARRAYID # Job array ONLY")
    elif QueueingSystem == "TORQUE":
        JobScript.append("#$ -V ")
        JobScript.append("#$ -o torque.out")
        JobScript.append("#$ -j y")
        JobScript.append("#$ -S /bin/bash")
        JobScript.append("".join(["#$ -pe smp ", str(NumCore)]))
        JobScript.append("".join(["#$ -l h_rt=", WallTime]))
        JobScript.append("".join(["#$ -N ", JobName]))
        JobScript.append("".join(["#$ -cwd"]))
        JobScript.append("".join(["cd ", FolderName]))
    elif QueueingSystem == "SLURM":
        if len(ProjectName):
            JobScript.append("".join(["#SBATCH --account=", ProjectName]))
        if len(Partition):
            JobScript.append("".join(["#SBATCH --partition=", Partition]))
        JobScript.append("".join(["#SBATCH --nodes=", str(Nodes)]))
        JobScript.append("##SBATCH --array= # Job array ONLY")
        JobScript.append("##SBATCH --mail-type=END,FAIL # Mail events (NONE, BEGIN, END, FAIL, ALL)")
        JobScript.append("##SBATCH --mail-user=chenyenl@lanl.gov # Where to send mail")
        if MPI:
            JobScript.append("".join(["#SBATCH --ntasks=", str(MPI)]))
            JobScript.append("".join(["#SBATCH --ntasks-per-node=", str(PPN)]))
        JobScript.append("".join(["#SBATCH --cpus-per-task=", str(NumCore)]))
        JobScript.append("".join(["#SBATCH --time=", WallTime]))
        JobScript.append("".join(["#SBATCH --job-name=", JobName]))
        JobScript.append("".join(["##SBATCH --output=slurm.out"]))
        JobScript.append("".join(["#SBATCH --export=all"]))
        JobScript.append("##cd CH${SLURM_ARRAY_TASK_ID}OP1 # Job array ONLY")
    JobScript.append("".join(['export OMP_NUM_THREADS=', str(NumCore)]))
    JobScript.append('echo ----------------------------------------------')
    JobScript.append('echo "Job started on" `date`')
    JobScript.append('echo ----------------------------------------------')
    JobScript.append('umask ' + umask)
    JobScript.extend(Executable)
    JobScript.append('echo ----------------------------------------------')
    JobScript.append('echo "Job ended on" `date`')
    JobScript.append('echo ----------------------------------------------')
    JobScript.append('exit 0')
    JobScript.append('\n')
    f = open(Filename, 'w')
    f.write( "\n".join(JobScript) )
    f.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Scripts.py", usage='%(prog)s [options]', description="Generate submit scripts.", epilog="All's well that ends well.")
    parser.add_argument('-qs', '--system', metavar='(SLURM|PBS|TORQUE)', type=str, default="SLURM", help='Which queuing system? All caps! Default: SLURM')
    parser.add_argument('-fn', '--filename', metavar='job', type=str, default="job", help='Filename. Default: job')
    parser.add_argument('-jn', '--jobname', metavar='MyJob', type=str, default="MyJob", help='Job name for this job. Default: MyJob')
    parser.add_argument('-ap', '--apps', metavar='do_this.app', nargs="+", type=str, default=["/users/chengyanlai/GitRepo/tensorapps/build2/EF1dtebd.app","/bin/mv trace.dyn DONE.arpes"], help='Executables. Array.')
    parser.add_argument('-nd', '--nodes', metavar='1', type=int, default=1, help='Number of nodes requested. Default: 1')
    parser.add_argument('-np', '--cores', metavar='36', type=int, default=36, help='Number of cores requested. Default: 36')
    parser.add_argument('-wt', '--walltime', metavar='168:00:00', type=str, default="168:00:00", help='Walltime requested. Default: 7 days')
    parser.add_argument('-pt', '--partition', metavar='standard', type=str, default="standard", help='Partition. SLURM only. Default: standard')
    parser.add_argument('-pj', '--project', metavar='w18_xasrixs', type=str, default="w18_xasrixs", help='Project. SLURM only. Default: w18')
    parser.add_argument('--mpi', metavar='(0|1)', type=int, default=0, help='Is MPI job? Default: 0 (not MPI job)')
    parser.add_argument('--ppn', metavar='36', type=int, default=1, help='Number task per node. MPI only. Default: 1')
    parser.add_argument('--umask', metavar='022', type=str, default="022", help='You know it. Default: 022')
    args = vars(parser.parse_args())
    GenerateScript(args["system"], args["filename"], args["jobname"], args["apps"],  os.getcwd(), args["nodes"], args["cores"], args["walltime"], args["partition"], args["project"], args["mpi"], args["ppn"], args["umask"])
