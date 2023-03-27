#!/bin/bash
#SBATCH --job-name=rsfc
#SBATCH --time=10:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8gb
#SBATCH --partition=bluemoon
# Outputs ----------------------------------
#SBATCH --output=log/%x/%x-metrics_%j.out   
#SBATCH --error=log/%x/%x-metrics_%j.err  
# ------------------------------------------

pwd; hostname; date
set -e

module load singularity/3.7.1

HOST_DIR="/gpfs1/home/m/r/mriedel"
PROJECT="pace"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
CODE_DIR="${HOST_DIR}/${PROJECT}/code"
IMG_DIR="${HOST_DIR}/${PROJECT}/software"

DATAs=(ALC ATS CANN COC)
for DATA in ${DATAs[@]}; do
    BIDS_DIR="${DSETS_DIR}/dset-${DATA}"

    SHELL_CMD="singularity exec --cleanenv \
        -B ${BIDS_DIR}:/data \
        -B ${CODE_DIR}:/code \
        ${IMG_DIR}/afni-22.3.05.sif"

    cmd="${SHELL_CMD} python /code/collect_metrics.py \
        --dset /data --dset_name ${DATA}"
                                            
    echo
    echo Commandline: $cmd
    eval $cmd 
    exitcode=$?

done

date
exit $exitcode