#!/bin/bash

set -e

BIDS_DIR=$1
RAWS_DIR=$2
SOFT_DIR=$3

chmod +x ${SOFT_DIR}/dcm2niix
sub_raw_dirs=($(ls -d ${RAWS_DIR}/*/dwi))
for sub_raw_dir in ${sub_raw_dirs[@]}; do
    sub=$(echo ${sub_raw_dir} | awk -F'/' '{print $(NF-1)}')
    echo $sub
    mkdir -p "${BIDS_DIR}/$sub/dwi"
    cmd="${SOFT_DIR}/dcm2niix -o ${BIDS_DIR}/$sub/dwi \
        -f %p_%s_%z \
        -b y \
        -ba y \
        -z y \
        ${sub_raw_dirs}/*"
    echo Commandline: $cmd
    eval $cmd 
done