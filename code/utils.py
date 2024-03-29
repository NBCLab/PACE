import json as js
import math
import os
import os.path as op
import subprocess

import nibabel as nib
import numpy as np
import pandas as pd


def run_command(command, env=None):
    """Run a given shell command with certain environment variables set."""
    # https://github.com/NBCLab/power-replication/blob/master/processing/processing_utils.py
    merged_env = os.environ
    if env:
        merged_env.update(env)
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        env=merged_env,
    )
    line = process.stdout.readline()
    line = str(line, "utf-8")[:-1]

    return line


def get_acompcor(regressfile, out_file, trs_to_delete):
    df_in = pd.read_csv(regressfile, sep="\t")
    with open("{0}.json".format(regressfile.replace(".tsv", ""))) as json_file:
        data = js.load(json_file)
        acompcors = sorted([x for x in data.keys() if "a_comp_cor" in x])
        # for muschelli 2014
        acompcor_list_CSF = [x for x in acompcors if data[x]["Mask"] == "CSF"]
        acompcor_list_CSF = acompcor_list_CSF[0:3]
        acompcor_list_WM = [x for x in acompcors if data[x]["Mask"] == "WM"]
        acompcor_list_WM = acompcor_list_WM[0:3]
        acompcor_list = []
        acompcor_list.extend(acompcor_list_CSF)
        acompcor_list.extend(acompcor_list_WM)

    df_out = df_in[acompcor_list]
    df_out = df_out.replace("n/a", 0)
    df_out = df_out.drop([i for i in range(trs_to_delete)])
    df_out.to_csv(out_file, sep="\t", header=False, index=False)


def fd_censoring(tmp_file, fd_thresh):
    df_in = pd.read_csv(tmp_file, sep="\t")
    fd = df_in["framewise_displacement"]
    fd = fd[
        1:,
    ]
    fd_cens = np.ones(len(fd.index) + 1)
    fd_list = []
    for i, tmp_fd in enumerate(fd):
        if float(tmp_fd) > fd_thresh:
            fd_list.append(i + 1)
    fd_cens[fd_list] = 0
    return fd_cens


def enhance_censoring(censor_data, n_contig=2, n_before=1, n_after=2):
    """
    Censor non-contiguous TRs based on outlier file.
    """

    censor_vec = 1 - censor_data.astype(int)

    out_vec = np.zeros(censor_vec.shape, int)
    cens_vols = np.where(censor_vec)[0]

    # Flag volumes before each outlier
    temp = np.copy(cens_vols)
    for trs_before in range(1, n_before + 1):
        temp = np.hstack((temp, cens_vols - trs_before))
    cens_vols = np.unique(temp)
    all_vols = np.arange(len(censor_vec))

    # Remove censored index outside range
    # Unnecessary here but keeps everything interpretable
    cens_vols = np.intersect1d(all_vols, cens_vols)

    # Flag volumes after each outlier
    temp = np.copy(cens_vols)
    for trs_after in range(1, n_after + 1):
        temp = np.hstack((temp, cens_vols + trs_after))
    cens_vols = np.unique(temp)
    all_vols = np.arange(len(censor_vec))

    # Remove censored index outside range
    cens_vols = np.intersect1d(all_vols, cens_vols)

    # Flag orphan volumes (unflagged volumes between flagged ones)
    temp = np.copy(cens_vols)
    contig_idx = np.where(np.diff(cens_vols) < n_contig)[0]
    for idx in contig_idx:
        start = cens_vols[idx]
        end = cens_vols[idx + 1]
        temp = np.hstack((temp, np.arange(start, end)))
    cens_vols = np.unique(temp)

    # Create improved censor vector
    out_vec[cens_vols] = 1

    out_data = 1 - out_vec

    return out_data


def motion_parameters(tmp_file, derivatives=None):
    df_in = pd.read_csv(tmp_file, sep="\t")
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
    motion_regressors = df_in[motion_labels]
    return motion_regressors


def get_TR(nifti_file):
    # Looking for TR in the nifti header
    img = nib.load(nifti_file)
    header = img.header
    return round(header["pixdim"][4], 1)


def get_nslices(nifti_file):
    # Looking for nslices in the nifti header
    img = nib.load(nifti_file)
    header = img.header
    # header.get_n_slices()
    return header.get_data_shape()[2]


def get_nvol(nifti_file):
    # Looking for nvol in the nifti header
    img = nib.load(nifti_file)
    header = img.header
    return header.get_data_shape()[3]


def get_echotime(nifti_file):
    # Looking for nslices in the nifti header
    img = nib.load(nifti_file)
    header = img.header
    echo_time = str(header["descrip"]).split("TE=")[1].split(";")[0]

    return int(echo_time) / 1000


def get_slicetiming(nifti_file, mode, ref, ascending=True):
    # Mode default = 1 3 5 ... 2 4 6 ...
    # Mode interleaved = 1 4 7 10 2 5 8 3 6 9
    TR = get_TR(nifti_file)
    nslices = get_nslices(nifti_file)
    print(f"\tTR = {TR}, Slices = {nslices}", flush=True)

    # Slice Timing
    sliceduration = TR / nslices
    slicetiming = np.linspace(0, TR - sliceduration, nslices)

    if mode == "interleaved":
        order = []
        idx = round(math.sqrt(nslices))
        for i in range(idx):
            order = order + list(range(i, nslices, idx))
    elif mode == "default":
        if ref == 0:
            order = list(range(0, nslices, 2)) + list(range(1, nslices, 2))
        else:
            # ref == 1:
            order = list(range(1, nslices, 2)) + list(range(0, nslices, 2))
    else:
        # mode == "sequential":
        order = list(range(0, nslices, 1))

    slicetiming[order] = slicetiming.copy()

    if not ascending:
        slicetiming = np.flip(slicetiming)

    slicetiming = slicetiming.tolist()
    return slicetiming


def keep_trs(confounds_file, qc_thresh):
    print("\tGet TRs to censor")
    confounds_df = pd.read_csv(confounds_file, sep="\t")
    qc_arr = confounds_df["framewise_displacement"].values
    qc_arr = np.nan_to_num(qc_arr, 0)
    threshold = 3

    mask = qc_arr >= qc_thresh

    K = np.ones(threshold)
    dil = np.convolve(mask, K, mode="same") >= 1
    dil_erd = np.convolve(dil, K, mode="same") >= threshold

    prop_incl = np.sum(dil_erd) / qc_arr.shape[0]
    print(f"\t\tPecentage of TRS flagged {round(prop_incl*100,2)}", flush=True)
    out = np.ones(qc_arr.shape[0])
    out[dil_erd] = 0
    return out


def submit_job(job_name, cores, mem, partition, output_file, error_file, queue, account, command):

    os.makedirs(op.dirname(output_file), exist_ok=True)
    os.makedirs(op.dirname(error_file), exist_ok=True)

    cmd = 'sbatch -J {job_name} \
                  -c {cores} \
                  -p {partition} \
                  -o {output_file} \
                  -e {error_file} \
                  --qos {queue} \
                  --account {account} \
                  --wrap="{command}"'.format(
        job_name=job_name,
        cores=cores,
        partition=partition,
        output_file=output_file,
        error_file=error_file,
        queue=queue,
        account=account,
        command=command,
    )
    print(cmd)
    os.system(cmd)
