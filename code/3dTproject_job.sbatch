#!/bin/bash
#SBATCH --time=08:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4gb
#SBATCH --partition=bluemoon
# Outputs ----------------------------------
#SBATCH --output=log/%x_%A-%a.out   
#SBATCH --error=log/%x_%A-%a.err   
# ------------------------------------------


pwd; hostname; date
set -e

# sbatch --array=1-$(( $( wc -l ../dset-ATS107/participants.tsv | cut -f1 -d' ' ) - 1 ))%4 --job-name="3dTproject-ATS107" --export=DATA="ATS107" 3dTproject_job.sbatch

#==============Shell script==============#
#Load the software needed
spack load singularity@3.7.1

HOST_DIR="/gpfs1/home/m/r/mriedel"
PROJECT="pace"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
BIDS_DIR="${DSETS_DIR}/dset-${DATA}"
IMG_DIR="${HOST_DIR}/${PROJECT}/software"
SCRATCH_DIR="${HOST_DIR}/${PROJECT}/scratch/dset-${DATA}/afni-20.2.5"
DERIVS_DIR="${BIDS_DIR}/derivatives/3dtproject"
mkdir -p ${SCRATCH_DIR}
mkdir -p ${DERIVS_DIR}

# Parse the participants.tsv file and extract one subject ID from the line corresponding to this SLURM task.
subject=$( sed -n -E "$((${SLURM_ARRAY_TASK_ID} + 1))s/sub-(\S*)\>.*/\1/gp" ${BIDS_DIR}/participants.tsv )
mem_gb=`echo "${SLURM_MEM_PER_CPU} * ${SLURM_CPUS_PER_TASK}" | bc -l`

# Compose the command line
SHELL_CMD="singularity exec --cleanenv \
      -B ${DSETS_DIR}/code:/code
      -B ${BIDS_DIR}:/data \
      $IMG_DIR/nipreps-fmriprep_20.2.5.sif"

# Run python script inside fmriprep environment
cmd="${SHELL_CMD} python /code/3dTproject.py \
      --dset /data \
      --subject sub-${subject}"

# Setup done, run the command
echo Commandline: $cmd
eval $cmd 

exitcode=$?

# Output results to a table
echo "sub-$subject   ${SLURM_ARRAY_TASK_ID}    $exitcode" \
      >> ${BIDS_DIR}/code/log/${SLURM_JOB_NAME}.${SLURM_ARRAY_JOB_ID}.tsv
echo Finished tasks ${SLURM_ARRAY_TASK_ID} with exit code $exitcode
exit $exitcode

date
