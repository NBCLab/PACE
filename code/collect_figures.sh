#!/bin/bash
#SBATCH --time=10:00:00
#SBATCH --job-name=rsfc
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=15gb
#SBATCH --partition=bluemoon
# Outputs ----------------------------------
#SBATCH --output=log/%x/group/%x-plt_%j.out   
#SBATCH --error=log/%x/group/%x-plt_%j.err 
# ------------------------------------------

pwd; hostname; date
set -e


#==============Shell script==============#
#Load the software needed
spack load python@3.7.7

python /gpfs1/home/m/r/mriedel/pace/code/collect_figures.py


date
