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
# sbatch --job-name="jsons-OPI105" --export=DATA="OPI105" metadata_job.sh

#==============Shell script==============#
#Load the software needed
module load python/python-miniconda3-rdchem-deepchem
source activate /gpfs1/home/m/r/mriedel/pace/env/env_bidsify

HOST_DIR="/gpfs1/home/m/r/mriedel"
PROJECT="pace"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
CODE_DIR="${DSETS_DIR}/code"
BIDS_DIR="${DSETS_DIR}/dset-${DATA}"
ANAT_TEMPLATE="/gpfs1/home/m/r/mriedel/pace/raw/OPI105_JaneJoseph/sourcedata/SCOR_MPRAGE.json"
FUNC_TEMPLATE="/gpfs1/home/m/r/mriedel/pace/raw/OPI105_JaneJoseph/sourcedata/SCOR_RestingState.json"
DWI_TEMPLATE="None"
FMAP_TEMPLATE="/gpfs1/home/m/r/mriedel/pace/raw/OPI105_JaneJoseph/sourcedata/SCOR_rest_fieldmap.json"
MAG_TEMPLATE="/gpfs1/home/m/r/mriedel/pace/raw/OPI105_JaneJoseph/sourcedata/SCOR_rest_magnitude.json"
MODE="default"
REF=1

# Fix json files
cmd="python ${CODE_DIR}/metadata_fix.py \
      --bids_dir ${BIDS_DIR} \
      --mode ${MODE} \
      --ref ${REF} \
      --templates ${ANAT_TEMPLATE} ${FUNC_TEMPLATE} ${DWI_TEMPLATE} ${FMAP_TEMPLATE} ${MAG_TEMPLATE}"
# Setup done, run the command
echo Commandline: $cmd
eval $cmd 


echo "Fix json file for ${DATA} with exit code $exitcode"
date
exit $exitcode
