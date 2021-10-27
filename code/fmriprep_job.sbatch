#!/bin/bash
#SBATCH --time=168:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4gb
#SBATCH --partition=bigmemwk
# Outputs ----------------------------------
#SBATCH --output=log/%x_%A-%a.out   
#SBATCH --error=log/%x_%A-%a.err   
# ------------------------------------------


pwd; hostname; date
set -e

# sbatch --array=1-130%5 --job-name="fmriprep-MSSM" --export=DATA="MSSM" fmriprep_job.sbatch

#==============Shell script==============#
#Load the software needed
spack load singularity@3.7.1

HOST_DIR="/gpfs1/home/m/r/mriedel"
PROJECT="pace"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
BIDS_DIR="${DSETS_DIR}/dset-${DATA}"
IMG_DIR="${HOST_DIR}/${PROJECT}/software"
SCRATCH_DIR="${HOST_DIR}/${PROJECT}/scratch/dset-${DATA}/fmriprep-20.2.5"
DERIVS_DIR="${BIDS_DIR}/derivatives/fmriprep-20.2.5"
mkdir -p ${SCRATCH_DIR}
mkdir -p ${DERIVS_DIR}

# Prepare some writeable bind-mount points.
TEMPLATEFLOW_HOST_HOME=${HOME}/.cache/templateflow
FMRIPREP_HOST_CACHE=${HOME}/.cache/fmriprep
mkdir -p ${TEMPLATEFLOW_HOST_HOME}
mkdir -p ${FMRIPREP_HOST_CACHE}


# Make sure FS_LICENSE is defined in the container.
FS_LICENSE="/gpfs1/home/m/r/mriedel/pace/software/freesurfer"

# Designate a templateflow bind-mount point
export SINGULARITYENV_TEMPLATEFLOW_HOME=${TEMPLATEFLOW_HOST_HOME}

SINGULARITY_CMD="singularity run --cleanenv \
      -B $BIDS_DIR:/data \
      -B ${DERIVS_DIR}:/out \
      -B ${TEMPLATEFLOW_HOST_HOME}:${SINGULARITYENV_TEMPLATEFLOW_HOME} \
      -B ${SCRATCH_DIR}:/work \
      -B ${FS_LICENSE}:/freesurfer
      $IMG_DIR/nipreps-fmriprep_20.2.5.sif"

# Parse the participants.tsv file and extract one subject ID from the line corresponding to this SLURM task.
subject=$( sed -n -E "$((${SLURM_ARRAY_TASK_ID} + 1))s/sub-(\S*)\>.*/\1/gp" ${BIDS_DIR}/participants.tsv )

# Compose the command line
mem_gb=`echo "${SLURM_MEM_PER_CPU} * ${SLURM_CPUS_PER_TASK}" | bc -l`
echo ${SLURM_MEM_PER_CPU}
echo ${SLURM_CPUS_PER_TASK}
echo ${mem_gb}
cmd="${SINGULARITY_CMD} /data \
      /out \
      participant \
      --participant-label $subject \
      -w /work/ \
      -vv \
      --omp-nthreads ${SLURM_CPUS_PER_TASK} \
      --nprocs ${SLURM_CPUS_PER_TASK} \
      --mem_mb ${mem_gb} \
      --output-spaces MNI152NLin2009cAsym:res-2 anat fsnative fsaverage5 \
      --cifti-output 91k \
      --notrack \
      --skip_bids_validation \
      --fs-license-file /freesurfer/license.txt"

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
