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
# sbatch --job-name="validator-ALC" --export=DATA="ALC" validator_job.sh

#==============Shell script==============#
#Load the software needed
module load singularity/3.7.1
# spack load singularity@3.7.1

HOST_DIR="/gpfs1/home/m/r/mriedel"
PROJECT="pace"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
BIDS_DIR="${DSETS_DIR}/dset-${DATA}"
IMG_DIR="${HOST_DIR}/${PROJECT}/software"
DERIVS_DIR="${BIDS_DIR}/derivatives"
mkdir -p ${DERIVS_DIR}

echo "Validating ${BIDS_DIR}"

#Run the program
rm -f $BIDS_DIR/derivatives/validator.txt
SINGULARITY_CMD="singularity run --cleanenv \
    -B $BIDS_DIR:/data \
    $IMG_DIR/bids-validator_1.8.0.sif"
cmd="${SINGULARITY_CMD} /data > ${DERIVS_DIR}/validator.txt"
echo Running task BIDS Validator
echo Commandline: $cmd
eval $cmd
exitcode=$?

date