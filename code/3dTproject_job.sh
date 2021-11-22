#!/bin/bash
#SBATCH --time=29:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=3gb
#SBATCH --partition=bluemoon
# Outputs ----------------------------------
#SBATCH --output=log/%x_%j.out   
#SBATCH --error=log/%x_%j.err   
# ------------------------------------------


pwd; hostname; date
set -e

# sbatch --job-name="3dTproject-ATS107" --export=DATA="ATS107" 3dTproject_job.sh

#==============Shell script==============#
#Load the software needed
spack load singularity@3.7.1
module load python/python-miniconda3-rdchem-deepchem
source activate /gpfs1/home/m/r/mriedel/pace/env/env_bidsify

HOST_DIR="/gpfs1/home/m/r/mriedel"
PROJECT="pace"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
CODE_DIR="${DSETS_DIR}/code"
BIDS_DIR="${DSETS_DIR}/dset-${DATA}"
IMG_DIR="${HOST_DIR}/${PROJECT}/software"
SCRATCH_DIR="${HOST_DIR}/${PROJECT}/scratch/dset-${DATA}/afni-20.2.5"
PREPROC_DIR="${BIDS_DIR}/derivatives/fmriprep-20.2.5/fmriprep"
DERIVS_DIR="${BIDS_DIR}/derivatives/3dtproject"
mkdir -p ${SCRATCH_DIR}
mkdir -p ${DERIVS_DIR}
FD_THR=0.35

# setenv
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}

# List subjects with *desc-preproc_bold.nii.gz
subjects=($(ls ${PREPROC_DIR}/sub-*/func/*task-rest_*space-MNI152NLin2009cAsym*_desc-preproc_bold.nii.gz | awk -F'/' '{print $(NF)}' | awk -F'_' '{print $1}' | uniq))
for subject in ${subjects[@]}; do
    # Compose the command line
    SHELL_CMD="singularity exec --cleanenv \
          -B ${DSETS_DIR}/code:/code
          -B ${BIDS_DIR}:/data \
          $IMG_DIR/nipreps-fmriprep_20.2.5.sif"
    # Run python script inside fmriprep environment
    cmd="${SHELL_CMD} python /code/3dTproject.py \
          --dset /data \
          --subject ${subject}
          --qc_thresh ${FD_THR}"
    # Setup done, run the command
    echo Commandline: $cmd
    eval $cmd 
done

# Perform QCFC analyses
cmd="python ${CODE_DIR}/qcfc.py \
      --dset ${BIDS_DIR} \
      --subjects ${subjects[@]} \
      --n_jobs ${SLURM_CPUS_PER_TASK} \
      --qc_thresh ${FD_THR}"
# Setup done, run the command
echo
echo Commandline: $cmd
eval $cmd 


exitcode=$?

# Output results to a table
echo "sub-$subject   ${SLURM_ARRAY_TASK_ID}    $exitcode" \
      >> ${BIDS_DIR}/code/log/${SLURM_JOB_NAME}.${SLURM_ARRAY_JOB_ID}.tsv
echo Finished tasks ${SLURM_ARRAY_TASK_ID} with exit code $exitcode
exit $exitcode

date
