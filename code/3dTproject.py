import argparse
import json
import os
import os.path as op
from glob import glob

import nibabel as nib
import numpy as np
import pandas as pd


def _get_parser():
    parser = argparse.ArgumentParser(description="Run 3dTproject in fmriprep derivatives")
    parser.add_argument(
        "--dset",
        dest="dset",
        required=True,
        help="Path to BIDS dataset",
    )
    parser.add_argument(
        "--subject",
        dest="subject",
        required=True,
        help="Subject identifier, with the sub- prefix.",
    )
    return parser


def get_motionpar(confounds_file, derivatives=None):
    confounds_df = pd.read_csv(confounds_file, sep="\t")
    if derivatives:
        motion_labels = [
            "trans_x",
            "trans_x_derivative1",
            "trans_y",
            "trans_y_derivative1",
            "trans_z",
            "trans_z_derivative1",
            "rot_x",
            "rot_x_derivative1",
            "rot_y",
            "rot_y_derivative1",
            "rot_z",
            "rot_z_derivative1",
        ]
    else:
        motion_labels = ["trans_x", "trans_y", "trans_z", "rot_x", "rot_y", "rot_z"]
    motion_regressors = confounds_df[motion_labels].values
    return motion_regressors


# Taken from Cody's pipeline
def get_acompcor(confounds_file):
    print("\tGet aCompCor")
    confounds_json_file = confounds_file.replace(".tsv", ".json")
    confounds_df = pd.read_csv(confounds_file, sep="\t")
    with open(confounds_json_file) as json_file:
        data = json.load(json_file)
    acompcors = sorted([x for x in data.keys() if "a_comp_cor" in x])
    # for muschelli 2014
    acompcor_list_CSF = [x for x in acompcors if data[x]["Mask"] == "CSF"]
    acompcor_list_CSF = acompcor_list_CSF[0:3]
    acompcor_list_WM = [x for x in acompcors if data[x]["Mask"] == "WM"]
    acompcor_list_WM = acompcor_list_WM[0:3]
    acompcor_list = []
    acompcor_list.extend(acompcor_list_CSF)
    acompcor_list.extend(acompcor_list_WM)

    print(f"\t\tComponents: {acompcor_list}", flush=True)
    acompcor_arr = confounds_df[acompcor_list].values

    return acompcor_arr


def run_3dtproject(preproc_file, mask_file, confounds_file, dummy_scans, out_dir):
    preproc_name = op.basename(preproc_file)
    prefix = preproc_name.split("desc-")[0].rstrip("_")
    preproc_json_file = preproc_file.replace(".nii.gz", ".json")

    # Determine output files
    denoised_file = op.join(out_dir, f"{prefix}_desc-aCompCor_bold.nii.gz")
    denoisedSM_file = op.join(out_dir, f"{prefix}_desc-aCompCorSM6_bold.nii.gz")

    img = nib.load(preproc_file)
    header = img.header
    n_trs = header["dim"][4]

    # Create regressor matrix
    demeaning = np.ones(n_trs)
    detrending = np.arange(n_trs)
    motionpar = get_motionpar(confounds_file, derivatives=True)
    acompcor = get_acompcor(confounds_file)
    nuisance_regressors = np.column_stack((demeaning, detrending, motionpar, acompcor))

    # Some fMRIPrep nuisance regressors have NaN in the first row (e.g., derivatives)
    nuisance_regressors = np.nan_to_num(nuisance_regressors, 0)
    nuisance_regressors = np.delete(nuisance_regressors, range(dummy_scans), axis=0)

    # Create regressor file
    regressor_file = op.join(out_dir, f"{prefix}_regressors.1D")
    np.savetxt(regressor_file, nuisance_regressors, fmt="%.5f")

    cmd = f"3dTproject \
            -input {preproc_file}[{dummy_scans}..$] \
            -polort 1 \
            -prefix {denoised_file} \
            -ort {regressor_file} \
            -passband 0.01 0.10 \
            -mask {mask_file}"
    print(f"\t{cmd}", flush=True)
    os.system(cmd)

    cmd = f"3dTproject \
            -input {preproc_file}[{dummy_scans}..$] \
            -polort 1 \
            -blur 6 \
            -prefix {denoisedSM_file} \
            -ort {regressor_file} \
            -passband 0.01 0.10 \
            -mask {mask_file}"
    print(f"\t{cmd}", flush=True)
    os.system(cmd)

    # Create json files with Sources and Description fields
    # Load metadata for writing out later and TR now
    with open(preproc_json_file, "r") as fo:
        json_info = json.load(fo)
    json_info["Sources"] = [denoised_file, mask_file, regressor_file]

    SUFFIXES = {
        "desc-aCompCor_bold": (
            "Denoising with an aCompCor regression model including 3 PCA components from"
            "WM and 3 from CSF deepest white matter, 6 motion parameters, and first"
            "temporal derivatives of motion parameters."
        ),
        "desc-aCompCorSM6_bold": (
            "Denoising with an aCompCor regression model including 3 PCA components from"
            "WM and 3 from CSF deepest white matter, 6 motion parameters, and first"
            "temporal derivatives of motion parameters. Spatial smoothing was applied."
        ),
    }
    for suffix, description in SUFFIXES.items():
        nii_file = op.join(out_dir, f"{prefix}_{suffix}.nii.gz")
        assert op.isfile(nii_file)

        suff_json_file = op.join(out_dir, f"{prefix}_{suffix}.json")
        json_info["Description"] = description
        with open(suff_json_file, "w") as fo:
            json.dump(json_info, fo, sort_keys=True, indent=4)


def main(dset, subject):
    """Run denoising workflows on a given dataset."""
    # Taken from Taylor's pipeline
    deriv_dir = op.join(dset, "derivatives")
    nuis_dir = op.join(deriv_dir, "3dtproject")
    preproc_dir = op.join(deriv_dir, "fmriprep-20.2.5", "fmriprep")
    space = "MNI152NLin2009cAsym"
    dummy_scans = 5

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

    mask_files = glob(
        op.join(preproc_subj_func_dir, f"*task-rest*_space-{space}*_desc-brain_mask.nii.gz")
    )
    assert len(mask_files) == 1
    mask_file = mask_files[0]

    os.makedirs(nuis_subj_dir, exist_ok=True)

    # ###################
    # Nuisance Regression
    # ###################
    print(f"Denoising {preproc_file}")
    run_3dtproject(preproc_file, mask_file, confounds_file, dummy_scans, nuis_subj_dir)


def _main(argv=None):
    option = _get_parser().parse_args(argv)
    kwargs = vars(option)
    main(**kwargs)


if __name__ == "__main__":
    _main()
