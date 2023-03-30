#!/bin/bash
#SBATCH --job-name=ibma
#SBATCH --time=29:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1gb
#SBATCH --partition=bluemoon
# Outputs ----------------------------------
#SBATCH --output=log/ibma_%A-%a.out   
#SBATCH --error=log/ibma_%A-%a.err   
# ------------------------------------------

pwd; hostname; date
set -e

#==============Shell script==============#
#Load the software needed
module load python/python-miniconda3-rdchem-deepchem

# sbatch sbatch --array=0-19 ibma-pace.sbatch

PROJECT="pace"
HOST_DIR="/gpfs1/home/m/r/mriedel"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
CODE_DIR="${HOST_DIR}/${PROJECT}/code"

TEMPLATE="${HOST_DIR}/${PROJECT}/templates/tpl-MNI152NLin2009cAsym_res-01_desc-brain_T1w.nii.gz"

# Run python script for BIDSifying anat and func and dwi
cmd="/gpfs1/home/m/r/mriedel/pace/env/env_bidsify/bin/python ${CODE_DIR}/ibma-pace.py
    --dset ${DSETS_DIR} 
    --template ${TEMPLATE}
    --index ${SLURM_ARRAY_TASK_ID}"
# Setup done, run the command
echo Commandline: $cmd
eval $cmd 

echo "IBMA exit with code $exitcode"
date
exit $exitcode