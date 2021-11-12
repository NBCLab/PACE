#!/bin/bash
#SBATCH --time=03:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1gb
#SBATCH --partition=short
# Outputs ----------------------------------
#SBATCH --output=log/%x_%j.out   
#SBATCH --error=log/%x_%j.err   
# ------------------------------------------

pwd; hostname; date
set -e

# Submit the job using the variable DATA="data-name"
# sbatch --job-name="jsons-NIAAA" --export=DATA="NIAAA" metadata_job.sh

#==============Shell script==============#
#Load the software needed
module load python/python-miniconda3-rdchem-deepchem
source activate /gpfs1/home/m/r/mriedel/pace/env/env_bidsify

HOST_DIR="/gpfs1/home/m/r/mriedel"
PROJECT="pace"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
CODE_DIR="${DSETS_DIR}/code"
BIDS_DIR="${DSETS_DIR}/dset-${DATA}"
FUNC_TEMPLATE=None

# Fix json files
cmd="python ${CODE_DIR}/metadata_fix.py \
      --bids_dir ${BIDS_DIR} \
      --func_template ${FUNC_TEMPLATE}"
# Setup done, run the command
echo Commandline: $cmd
eval $cmd 


echo "Fix json file for ${DATA} with exit code $exitcode"
date
exit $exitcode
