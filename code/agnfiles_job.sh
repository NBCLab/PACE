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
# sbatch --job-name="files-ALC134" --export=DATA="ALC134" agnfiles_job.sh

#==============Shell script==============#
#Load the software needed
module load python/python-miniconda3-rdchem-deepchem
source activate /gpfs1/home/m/r/mriedel/pace/env/env_bidsify

HOST_DIR="/gpfs1/home/m/r/mriedel"
PROJECT="pace"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
CODE_DIR="${DSETS_DIR}/code"
BIDS_DIR="${DSETS_DIR}/dset-${DATA}"

echo "Adding files for ${BIDS_DIR}"

# Generate .bidsignore file
bidsignore="${BIDS_DIR}/.bidsignore"
if [ -f "$bidsignore" ]; then
    echo "$bidsignore exists."
else
    echo ".*" >> $bidsignore
    echo "!*.icloud" >> $bidsignore
    echo "/derivatives" >> $bidsignore
    echo "/sourcedata" >> $bidsignore
    echo "/code" >> $bidsignore
fi

# dataset_description.json and participant.tsv
participants="${BIDS_DIR}/participants.tsv"
if [ -f "${participants}" ]; then
    echo "${participants} exists."
else 
    cmd="python ${CODE_DIR}/agnfiles.py \
          --bids_dir ${BIDS_DIR}"
    # Setup done, run the command
    echo Commandline: $cmd
    eval $cmd 
fi

# Generate README
README="${BIDS_DIR}/README"
if [ -f "${README}" ]; then
    echo "${README} exists."
else 
    echo "" >> ${README}
fi

# CHANGES
CHANGES="${BIDS_DIR}/CHANGES"
if [ -f "${CHANGES}" ]; then
    echo "${CHANGES} exists."
else 
    echo "" >> ${README}
    date >> "${CHANGES}"
    echo -e "\t Bidsification." >> "${CHANGES}"
fi


echo "Generate participants.tsv file for ${DATA} with exit code $exitcode"
date
exit $exitcode
