#!/bin/sh
module load fsl/fsl-6.0.1
set -e

BIDS_DIR=$1
RAWS_DIR=$2

#Image file type converter using fslchfiletype
#This script converts various image files into NIFTI format (.nii) files.
#K. Nemoto 19 Jan 2013

sub_raw_dirs=($(ls -d ${RAWS_DIR}/*)) 
for sub_raw_dir in ${sub_raw_dirs[@]}; do
  sub=$(echo ${sub_raw_dir} | awk -F'/' '{print $(NF-1)}')
  sub="sub-$sub"
  echo $sub
  mkdir -p "${BIDS_DIR}/$sub/anat"
  cmd="fslchfiletype NIFTI \
        $sub_raw_dir/ \ 
        ${BIDS_DIR}/$sub/anat"
  echo Commandline: $cmd
  eval $cmd
done