#!/bin/bash
#SBATCH --job-name=nii2bids_CANN122
#SBATCH --time=30:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1gb
#SBATCH --partition=bluemoon
# Outputs ----------------------------------
#SBATCH --output=log/nii2bids_CANN122-%j.out   
#SBATCH --error=log/nii2bids_CANN122-%j.err   
# ------------------------------------------

pwd; hostname; date
set -e

#==============Shell script==============#
#Load the software needed
module load python/python-miniconda3-rdchem-deepchem
source activate /gpfs1/home/m/r/mriedel/pace/env/env_bidsify

PROJECT="pace"
HOST_DIR="/gpfs1/home/m/r/mriedel"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
RAWS_DIR="${HOST_DIR}/${PROJECT}/raw/CANN122-Romina_Mizrahi/ENIGMA"
DATA="CANN122"
CODE_DIR="${DSETS_DIR}/dset-${DATA}/code"
BIDS_DIR="${DSETS_DIR}/dset-${DATA}"
SOFT_DIR="/gpfs1/home/m/r/mriedel/pace/software/MRIcroGL/Resources"

# Script for DICOM to NII of dwi 
chmod +x ${CODE_DIR}/dcm2nii.sh
echo "Look for dcm files"
dcms=($(find ${RAWS_DIR}/ -type f -name '*.dcm' | awk -F'/' '{print $(NF-2)"/"$(NF-1)}' |uniq))
echo ${dcms[@]}
for dcm in ${dcms[@]}; do
    echo "found dicoms in $dcm"
    cmd="bash ${CODE_DIR}/dcm2nii.sh \
        ${RAWS_DIR}/$dcm \
        ${SOFT_DIR}"
    # Setup done, run the command
    echo Commandline: $cmd
    eval $cmd 
done

# Run python script for BIDSifying anat and func and dwi
cmd="python ${CODE_DIR}/nii2bids.py \
      --bids_dir ${BIDS_DIR} \
      --raw_dir ${RAWS_DIR}"
# Setup done, run the command
echo Commandline: $cmd
eval $cmd 

echo "BIDSify data ${DATA} with exit code $exitcode"
date
exit $exitcode