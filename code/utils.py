import math

import nibabel as nib
import numpy as np


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

    if mode == "default":
        if ref == 0:
            order = list(range(0, nslices, 2)) + list(range(1, nslices, 2))
        else:
            # ref == 1:
            order = list(range(1, nslices, 2)) + list(range(0, nslices, 2))
    else:
        # mode == "interleaved":
        order = []
        idx = round(math.sqrt(nslices))
        for i in range(idx):
            order = order + list(range(i, nslices, idx))

    slicetiming[order] = slicetiming.copy()

    if not ascending:
        slicetiming = np.flip(slicetiming)

    slicetiming = slicetiming.tolist()
    return slicetiming
