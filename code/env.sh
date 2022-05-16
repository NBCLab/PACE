#!/bin/bash
#SBATCH --job-name=env
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1gb
#SBATCH --partition=short
# Outputs ----------------------------------
#SBATCH --output=log/env-%j.out   
#SBATCH --error=log/env-%j.err   
# ------------------------------------------

set -e

conda create -p /gpfs1/home/m/r/mriedel/pace/env/env_bidsify python=3.8 -yq
source activate /gpfs1/home/m/r/mriedel/pace/env/env_bidsify
pip install pip -U
pip install numpy nibabel