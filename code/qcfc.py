import argparse
import json
import os
import os.path as op
from glob import glob

import nibabel as nib
import numpy as np
import pandas as pd
from ddmra import run_analyses, utils


def _get_parser():
    parser = argparse.ArgumentParser(description="Perform QCFC analyses")
    parser.add_argument(
        "--dset",
        dest="dset",
        required=True,
        help="Path to BIDS dataset",
    )
    parser.add_argument(
        "--subjects",
        dest="subjects",
        required=True,
        nargs="+",
        help="List with subject IDs",
    )
    parser.add_argument(
        "--n_jobs",
        dest="n_jobs",
        required=True,
        help="CPUs",
    )
    parser.add_argument(
        "--qc_thresh",
        dest="qc_thresh",
        required=True,
        help="FD threshold",
    )
    return parser


def main(dset, subjects, n_jobs, qc_thresh):
    """Run QCFC workflow on a given dataset."""
    # Taken from Taylor's pipeline
    deriv_dir = op.join(dset, "derivatives")
    nuis_dir = op.join(deriv_dir, "3dtproject")
    preproc_dir = op.join(deriv_dir, "fmriprep-20.2.5", "fmriprep")
    space = "MNI152NLin2009cAsym"
    qc_thresh = float(qc_thresh)
    n_jobs = int(n_jobs)
    dummy_scans = 5

    imgs = []
    QCs = []
    for subject in subjects:
        preproc_subj_func_dir = op.join(preproc_dir, subject, "func")
        nuis_subj_dir = op.join(nuis_dir, subject, "func")

        # Collect important files
        confounds_files = glob(op.join(preproc_subj_func_dir, "*_desc-confounds_timeseries.tsv"))
        assert len(confounds_files) == 1
        confounds_file = confounds_files[0]

        preproc_files = glob(
            op.join(preproc_subj_func_dir, f"*task-rest*_space-{space}*_desc-preproc_bold.nii.gz")
        )
        assert len(preproc_files) == 1
        preproc_file = preproc_files[0]

        denoised_files = glob(op.join(nuis_subj_dir, "*_desc-aCompCor_bold.nii.gz"))
        assert len(denoised_files) == 1
        denoised_file = denoised_files[0]

        confounds_df = pd.read_csv(confounds_file, sep="\t")
        QCs.append(confounds_df["framewise_displacement"].values[dummy_scans:])

        imgs.append(denoised_file)

    print(f"\tRun QCFC workflow on {len(imgs)} subjects", flush=True)
    print(f"\tUse {len(QCs)} fd vectors", flush=True)
    # ###################
    # QCFC analyses
    # ###################
    run_analyses(imgs, QCs, out_dir=nuis_dir, n_iters=10000, n_jobs=n_jobs, qc_thresh=qc_thresh)


def _main(argv=None):
    option = _get_parser().parse_args(argv)
    kwargs = vars(option)
    main(**kwargs)


if __name__ == "__main__":
    _main()
