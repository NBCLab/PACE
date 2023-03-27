#!/bin/bash
#SBATCH --job-name=amygdala
#SBATCH --time=29:30:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --mem-per-cpu=8gb
#SBATCH --partition=bluemoon
# Outputs ----------------------------------
#SBATCH --output=log/rsfc/group/%x/COC-rh-gsr-3dlmer_%A-%a.out   
#SBATCH --error=log/rsfc/group/%x/COC-rh-gsr-3dlmer_%A-%a.err   
# ------------------------------------------

pwd; hostname; date
set -e

# In this case, ${SLURM_ARRAY_TASK_ID} indexes the ROI for a defined seed.
# sbatch --array=0 rsfc-group_job.sbatch # Run the first elemt to generate the tables
# sbatch --array=1-2 rsfc-group_job.sbatch # Wait ~5 min after submiting 0 to run the rest

#==============Shell script==============#
# Load the software needed
module load singularity/3.7.1
# spack load singularity@3.7.1 # Sometimes "module load" doesn't work.

DATA="COC"
HOST_DIR="/gpfs1/home/m/r/mriedel"
PROJECT="pace"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
BIDS_DIR="${DSETS_DIR}/dset-${DATA}"
CODE_DIR="${HOST_DIR}/${PROJECT}/code"
IMG_DIR="${HOST_DIR}/${PROJECT}/software"
DERIVS_DIR="${BIDS_DIR}/derivatives"
TEMPLATE_DIR="${HOST_DIR}/${PROJECT}/templates"
mriqc_ver=0.16.1
fmriprep_ver=20.2.5
afni_ver=22.0.20

gsr="-gsr"
#gsr=""
FMRIPREP_DIR="${DERIVS_DIR}/fmriprep-${fmriprep_ver}/fmriprep"
MRIQC_DIR="${DERIVS_DIR}/mriqc-${mriqc_ver}"
CLEAN_DIR="${DERIVS_DIR}/denoising${gsr}-${afni_ver}"

# program=3dttest++
# program=3dmema
program=3dlmer
# program=combat
seed_region=amygdala
hemis=rh
template="tpl-MNI152NLin2009cAsym_res-02_desc-brain_T1w.nii.gz"
template_mask="tpl-MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz"

if [[ ${seed_region} ==  "vmPFC" ]]; then
    ROIs=("vmPFC1" "vmPFC2" "vmPFC3" "vmPFC4" "vmPFC5" "vmPFC6")
    RSFC_DIR="${DERIVS_DIR}/rsfc${gsr}-${seed_region}_C1-C2-C3-C4-C5-C6"
elif [[ ${seed_region} ==  "insula" ]]; then
    ROIs=("insulaD${hemis}" "insulaP${hemis}" "insulaV${hemis}")
    RSFC_DIR="${DERIVS_DIR}/rsfc${gsr}-${seed_region}_D${hemis}-P${hemis}-V${hemis}"
elif [[ ${seed_region} ==  "hippocampus" ]]; then
    ROIs=("hippocampus3solF1${hemis}" "hippocampus3solF2${hemis}" "hippocampus3solF3${hemis}")
    RSFC_DIR="${DERIVS_DIR}/rsfc${gsr}-${seed_region}_3solF1${hemis}-3solF2${hemis}-3solF3${hemis}"
elif [[ ${seed_region} ==  "amygdala" ]]; then
    ROIs=("amygdala1${hemis}" "amygdala2${hemis}" "amygdala3${hemis}")
    RSFC_DIR="${DERIVS_DIR}/rsfc${gsr}-${seed_region}_C1${hemis}-C2${hemis}-C3${hemis}"
elif [[ ${seed_region} ==  "striatum" ]]; then
    ROIs=("striatumMatchCD${hemis}" "striatumMatchCV${hemis}" "striatumMatchDL${hemis}" "striatumMatchD${hemis}" "striatumMatchR${hemis}" "striatumMatchV${hemis}")
    RSFC_DIR="${DERIVS_DIR}/rsfc${gsr}-${seed_region}_matchCD${hemis}-matchCV${hemis}-matchDL${hemis}-matchD${hemis}-matchR${hemis}-matchV${hemis}"
fi

# Run group analysis
ROI=${ROIs[${SLURM_ARRAY_TASK_ID}]}
SHELL_CMD="singularity exec --cleanenv \
    -B ${BIDS_DIR}:/data \
    -B ${DERIVS_DIR}:/deriv \
    -B ${CODE_DIR}:/code \
    -B ${MRIQC_DIR}:/mriqc \
    -B ${FMRIPREP_DIR}:/fmriprep \
    -B ${CLEAN_DIR}:/clean \
    -B ${TEMPLATE_DIR}:/template_dir \
    -B ${RSFC_DIR}:/rsfc \
    $IMG_DIR/afni-22.3.05.sif"
# afni-22.3.05
# afni-23.0.04

# temp: /opt/miniconda-latest/envs/combat_env/bin/python
# Run python script inside afni-${afni_ver}.sif environment
analysis="${SHELL_CMD} python /code/rsfc-group.py \
    --dset /data \
    --deriv_dir /deriv \
    --mriqc_dir /mriqc \
    --preproc_dir /fmriprep \
    --clean_dir /clean \
    --rsfc_dir /rsfc \
    --template /template_dir/${template} \
    --template_mask /template_dir/${template_mask} \
    --roi_lst ${ROIs[@]} \
    --roi ${ROI} \
    --program ${program} \
    --n_jobs ${SLURM_CPUS_PER_TASK}"

# Setup done, run the command
echo
echo Commandline: $analysis
eval $analysis 
exitcode=$?

echo Finished tasks with exit code $exitcode
date

exit $exitcode