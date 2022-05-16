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
import getpass


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
    parser = argparse.ArgumentParser(description='Run fMRIPREP on BIDS dataset.')
    parser.add_argument('-b', '--bidsdir', required=True, dest='bids_dir',
                        help=('Output directory for BIDS dataset and '
                              'derivatives.'))
    parser.add_argument('-w', '--workdir', required=False, dest='work_dir',
                        default=None,
                        help='Path to a working directory. Defaults to work '
                             'subfolder in dset_dir.')
    parser.add_argument('--sub', required=True, dest='sub',
                        help='The label of the subject to analyze.')
    parser.add_argument('--ses', required=False, dest='ses',
                        help='Session number', default=None)
    parser.add_argument('--n_procs', required=False, dest='n_procs',
                        help='Number of processes with which to run the job.',
                        default=1, type=int)
    return parser


def main(argv=None):
    args = get_parser().parse_args(argv)

    if not op.isdir(op.join(args.work_dir, 'dset')):
        os.makedirs(op.join(args.work_dir, 'dset'))
    else:
        shutil.rmtree(args.work_dir)

    if args.ses is not None:
        data_dir = op.join(args.bids_dir, args.sub, args.ses)
        work_dir = op.join(args.work_dir, 'dset', args.sub, args.ses)
    else:
        data_dir = op.join(args.bids_dir, args.sub)
        work_dir = op.join(args.work_dir, 'dset', args.sub)

    shutil.copytree(data_dir, work_dir)
    shutil.copyfile(op.join(args.bids_dir, 'dataset_description.json'), op.join(args.work_dir, 'dset', 'dataset_description.json'))
    shutil.copyfile(op.join(args.bids_dir, '.bidsignore'), op.join(args.work_dir, 'dset', '.bidsignore'))

    mriqc_file = 'poldracklab_mriqc_0.15.1.sif'
    shutil.copyfile(op.join('/users/m/r/mriedel/pace/code/singularity-images', mriqc_file), op.join(args.work_dir, mriqc_file))

    if op.isdir(op.join(work_dir, 'dwi')):
        shutil.rmtree(op.join(work_dir, 'dwi'))

    os.makedirs(op.join(args.work_dir, 'mriqc_0.15.1'))

    #if not op.isdir(op.join(args.work_dir, 'templateflow')):
    #    shutil.copytree('/users/m/r/mriedel/pace/code/templateflow', op.join(args.work_dir, 'templateflow'))

    #os.makedirs(op.join('/users/home/m/r/mriedel/.cache/templateflow'), exist_ok=True)
    os.makedirs(op.join(args.work_dir, 'mriqc_0.15.1', 'logs'), exist_ok=True)
    #-B {templateflowdir}:$HOME/.cache/templateflow
    #templateflowdir=op.join(args.work_dir, 'templateflow'),
    cmd = ('singularity run --cleanenv {sing} {bids} {out} participant --no-sub --verbose-reports '
           '-w {work} --n_procs {n_procs} --correct-slice-timing '.format(sing=op.join(args.work_dir, mriqc_file),
                                                   bids=op.join(args.work_dir, 'dset'),
                                                   out=op.join(args.work_dir, 'mriqc_0.15.1'),
                                                   work=op.join(args.work_dir, 'mriqc-work'),
                                                   n_procs=args.n_procs))
    print(cmd)
    run(cmd)

    if args.ses is None:
        os.makedirs(op.join(args.bids_dir, 'derivatives', 'mriqc_0.15.1'), exist_ok=True)
        shutil.copytree(op.join(args.work_dir, 'mriqc_0.15.1'), op.join(args.bids_dir, 'derivatives', 'mriqc_0.15.1', args.sub))
    else:
        os.makedirs(op.join(args.bids_dir, 'derivatives', 'mriqc_0.15.1', args.sub), exist_ok=True)
        shutil.copytree(op.join(args.work_dir, 'mriqc_0.15.1'), op.join(args.bids_dir, 'derivatives', 'mriqc_0.15.1', args.sub, args.ses))


    shutil.rmtree(args.work_dir)

if __name__ == '__main__':
    main()
