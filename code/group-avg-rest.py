#!/usr/bin/env python3
"""
Based on
https://github.com/BIDS-Apps/example/blob/aa0d4808974d79c9fbe54d56d3b47bb2cf4e0a0d/run.py
"""
import os
import os.path as op
import shutil
import subprocess
from glob import glob
import argparse
import pandas as pd
import numpy as np


def run(command, env={}):
    merged_env = os.environ
    merged_env.update(env)
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, shell=True,
                               env=merged_env)
    while True:
        line = process.stdout.readline()
        #line = str(line).encode('utf-8')[:-1]
        line=str(line, 'utf-8')[:-1]
        print(line)
        if line == '' and process.poll() is not None:
            break

    if process.returncode != 0:
        raise Exception("Non zero return code: {0}\n"
                        "{1}\n\n{2}".format(process.returncode, command,
                                            process.stdout.read()))


def get_parser():
    parser = argparse.ArgumentParser(description='Run MRIQC on BIDS dataset.')
    parser.add_argument('-b', '--bidsdir', required=True, dest='bids_dir',
                        help=('Output directory for BIDS dataset and '
                              'derivatives.'))
    parser.add_argument('--derivative', required=True, dest='deriv',
                        help='Full path to ROI file', default=None)
    parser.add_argument('--dset', required=True, dest='dset',
                        help='dset name', default=None)
    return parser


def main(argv=None):
    args = get_parser().parse_args(argv)

    shutil.copyfile(op.join(args.bids_dir, 'code', 'group-avg-rest.fsf'), op.join(args.bids_dir, 'dsets', args.dset, 'derivatives', args.deriv, 'group-avg-rest.fsf'))

    #get a list of subjects in ROI derivative directory
    subs=sorted(glob(op.join(args.bids_dir, 'dsets', args.dset, 'derivatives', args.deriv, 'sub-*', '*.feat')))
    if len(subs) < 1:
        subs=sorted(glob(op.join(args.bids_dir, 'dsets', args.dset, 'derivatives', args.deriv, 'sub-*', 'ses-*', '*.feat')))

    subs = [i for i in subs if op.isfile(op.join(i, 'thresh_zstat2.nii.gz'))]

    with open(op.join(args.bids_dir, 'dsets', args.dset, 'derivatives', args.deriv, 'group-avg-rest.fsf'), 'r') as fo:
        fsf_data = fo.readlines()

    fsf_data[32] = 'set fmri(outputdir) "{outputdir}"\n'.format(outputdir=op.join(args.bids_dir, 'dsets', args.dset, 'derivatives', args.deriv, 'group-avg-rest'))
    fsf_data[38] = 'set fmri(npts) {}\n'.format(len(subs))
    fsf_data[47] = 'set fmri(multiple) {}\n'.format(len(subs))
    fsf_data_extra = fsf_data[289:]
    for a in range(1,len(subs)+1):
        fsf_data.insert(280+3*(a-1), '# 4D AVW data or FEAT directory ({a})\n'.format(a=a))
        fsf_data.insert(281+3*(a-1), 'set feat_files({a}) "{feat_file}"\n'.format(a=a, feat_file=subs[a-1]))
        fsf_data.insert(282+3*(a-1), '\n')

    fsf_data[282+3*(a-1)+1:282+3*(a-1)+1+len(fsf_data_extra)] = fsf_data_extra
    next_start = 282+3*(a-1)+1+44
    fsf_data_extra = fsf_data[next_start+9:]
    for a in range(1,len(subs)+1):
        fsf_data.insert(next_start+3*(a-1), '# Higher-level EV value for EV 1 and input {a}\n'.format(a=a))
        fsf_data.insert(next_start+1+3*(a-1), 'set fmri(evg{a}.1) 1\n'.format(a=a))
        fsf_data.insert(next_start+2+3*(a-1), '\n')

    fsf_data[next_start+2+3*(a-1)+1:next_start+2+3*(a-1)+1+len(fsf_data_extra)] = fsf_data_extra
    next_start2 = next_start+1+3*(a-1)+5
    fsf_data_extra = fsf_data[next_start2+9:]
    for a in range(1,len(subs)+1):
        fsf_data.insert(next_start2+3*(a-1), '# Group membership for input {a}\n'.format(a=a))
        fsf_data.insert(next_start2+1+3*(a-1), 'set fmri(groupmem.{a}) 1\n'.format(a=a))
        fsf_data.insert(next_start2+2+3*(a-1), '\n')

    fsf_data[next_start2+2+3*(a-1)+1:next_start2+2+3*(a-1)+1+len(fsf_data_extra)] = fsf_data_extra

    with open(op.join(args.bids_dir, 'dsets', args.dset, 'derivatives', args.deriv, 'group-avg-rest.fsf'), 'w') as fo:
        fo.writelines(fsf_data)

    cmd='feat {0}'.format(op.join(args.bids_dir, 'dsets', args.dset, 'derivatives', args.deriv, 'group-avg-rest.fsf'))
    run(cmd)

if __name__ == '__main__':
    main()
