#!/bin/bash
#SBATCH --job-name=mriqc
#SBATCH --time=20:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4gb
#SBATCH --partition=bluemoon
# Outputs ----------------------------------
#SBATCH --output=log/%x/COC/%x-COC_%j.out   
#SBATCH --error=log/%x/COC/%x-COC_%j.err   
# ------------------------------------------

pwd; hostname; date
set -e

# Submit the job using the variable
# sbatch mriqc-group_job.sh

#==============Shell script==============#
#Load the software needed
module load singularity/3.7.1
mriqc_ver=0.16.1

DATA="COC"
HOST_DIR="/gpfs1/home/m/r/mriedel"
PROJECT="pace"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
CODE_DIR="${HOST_DIR}/${PROJECT}/code"
BIDS_DIR="${DSETS_DIR}/dset-${DATA}"
IMG_DIR="${HOST_DIR}/${PROJECT}/software"
DERIVS_DIR="${BIDS_DIR}/derivatives/mriqc-${mriqc_ver}"
mkdir -p ${DERIVS_DIR}


SINGULARITY_CMD="singularity run --cleanenv \
      -B ${BIDS_DIR}:/data \
      -B ${DERIVS_DIR}:/out \
      ${IMG_DIR}/poldracklab-mriqc_${mriqc_ver}.sif"

# Compose the command line
mem_gb=`echo "${SLURM_MEM_PER_CPU} * ${SLURM_CPUS_PER_TASK} / 1024" | bc`
cmd="${SINGULARITY_CMD} /data \
      /out \
      group \
      --no-sub \
      --verbose-reports \
      --fd_thres 0.35 \
      --n_procs ${SLURM_CPUS_PER_TASK} \
      --mem_gb ${mem_gb}"

# Setup done, run the command
echo Commandline: $cmd
eval $cmd
exitcode=$?

SHELL_CMD="singularity exec --cleanenv \
      -B ${DERIVS_DIR}:/out \
      -B ${CODE_DIR}:/code \
      ${IMG_DIR}/poldracklab-mriqc_${mriqc_ver}.sif"

mriqc="${SHELL_CMD} python /code/mriqc-group.py \
          --dset /data \
          --out /out"

# Setup done, run the command
echo
echo Commandline: $mriqc
eval $mriqc 
exitcode=$?

echo "MRIQC-group $exitcode"
date

exit $exitcode
