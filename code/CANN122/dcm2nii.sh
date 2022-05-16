#!/bin/bash

set -e

RAWS_DIR=$1
SOFT_DIR=$2

chmod +x ${SOFT_DIR}/dcm2niix

cmd="${SOFT_DIR}/dcm2niix -o ${RAWS_DIR}/ \
    -f %z \
    -b y \
    -ba y \
    -z y \
    ${RAWS_DIR}/"
echo Commandline: $cmd
eval $cmd