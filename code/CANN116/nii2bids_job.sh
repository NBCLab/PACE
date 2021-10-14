#!/bin/bash
#SBATCH --job-name=nii2bids_CANN116
#SBATCH --time=03:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1gb
#SBATCH --partition=short
# Outputs ----------------------------------
#SBATCH --output=log/nii2bids_CANN116-%j.out   
#SBATCH --error=log/nii2bids_CANN116-%j.err   
# ------------------------------------------

pwd; hostname; date
set -e

#==============Shell script==============#
#Load the software needed
module load python/python-miniconda3-rdchem-deepchem
# conda create -p /gpfs1/home/m/r/mriedel/pace/env/env_bidsify python=3.8 -yq
# source activate
# pip install pip -U
source activate /gpfs1/home/m/r/mriedel/pace/env/env_bidsify

PROJECT="pace"
HOST_DIR="/gpfs1/home/m/r/mriedel"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
RAWS_DIR="${HOST_DIR}/${PROJECT}/raw/CANN116_sourcedata_Janna_Cousijn/sourcedata"
DATA="CANN116"
CODE_DIR="${DSETS_DIR}/dset-${DATA}/code"
BIDS_DIR="${DSETS_DIR}/dset-${DATA}"


# Run python script
cmd="python -u ${CODE_DIR}/nii2bids.py \
      --bids_dir ${BIDS_DIR} \
      --raw_dir ${RAWS_DIR} \
      >> log/logfile.log"
# Setup done, run the command
echo Commandline: $cmd
eval $cmd 

echo "BIDSify data ${DATA} with exit code $exitcode"
date
exit $exitcode