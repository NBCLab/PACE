#!/bin/bash
#SBATCH --job-name="mriqc"
#SBATCH --time=15:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4gb
#SBATCH --partition=bluemoon
# Outputs ----------------------------------
#SBATCH --output=log/%x/ALC134/%x-ALC134_%A-%a.out   
#SBATCH --error=log/%x/ALC134/%x-ALC134_%A-%a.err   
# ------------------------------------------


pwd; hostname; date
set -e

# sbatch --array=2-$(( $( wc -l ../dset-ALC134/participants.tsv | cut -f1 -d' ' ) - 1 ))%2 mriqc-participants_job.sbatch

#==============Shell script==============#
#Load the software needed
module load singularity/3.7.1
#spack load singularity@3.7.1
mriqc_ver=0.16.1

DATA="ALC134"
HOST_DIR="/gpfs1/home/m/r/mriedel"
PROJECT="pace"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
BIDS_DIR="${DSETS_DIR}/dset-${DATA}"
IMG_DIR="${HOST_DIR}/${PROJECT}/software"
SCRATCH_DIR="${HOST_DIR}/${PROJECT}/scratch/dset-${DATA}/mriqc-${mriqc_ver}/mriqc_${SLURM_ARRAY_TASK_ID}"
DERIVS_DIR="${BIDS_DIR}/derivatives/mriqc-${mriqc_ver}"
mkdir -p ${SCRATCH_DIR}
mkdir -p ${DERIVS_DIR}


# Make sure FS_LICENSE is defined in the container.
FS_LICENSE="/gpfs1/home/m/r/mriedel/pace/software/freesurfer/license.txt"

SINGULARITY_CMD="singularity run --cleanenv \
      -B $BIDS_DIR:/data \
      -B ${DERIVS_DIR}:/out \
      -B ${SCRATCH_DIR}:/work \
      ${IMG_DIR}/poldracklab-mriqc_0.16.1.sif"

# Parse the participants.tsv file and extract one subject ID from the line corresponding to this SLURM task.
subject=$( sed -n -E "$((${SLURM_ARRAY_TASK_ID} + 1))s/sub-(\S*)\>.*/\1/gp" ${BIDS_DIR}/participants.tsv )

# Compose the command line
mem_gb=`echo "${SLURM_MEM_PER_CPU} * ${SLURM_CPUS_PER_TASK} / 1024" | bc`
cmd="${SINGULARITY_CMD} /data \
      /out \
      participant \
      --participant-label $subject \
      --no-sub \
      --verbose-reports \
      -w /work \
      --ants-nthreads ${SLURM_CPUS_PER_TASK} \
      --n_procs ${SLURM_CPUS_PER_TASK} \
      --mem_gb ${mem_gb}"

# Setup done, run the command
echo Running task ${SLURM_ARRAY_TASK_ID}
echo Commandline: $cmd
eval $cmd
exitcode=$?

# Output results to a table
echo "sub-$subject   ${SLURM_ARRAY_TASK_ID}    $exitcode" \
      >> ${BIDS_DIR}/code/log/${SLURM_JOB_NAME}.${SLURM_ARRAY_JOB_ID}.tsv
echo Finished tasks ${SLURM_ARRAY_TASK_ID} with exit code $exitcode
exit $exitcode

date
