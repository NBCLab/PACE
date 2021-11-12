import nibabel as nib
import numpy as np


def get_TR(nifti_file):
    # Looking for TR in the nifti header
    img = nib.load(nifti_file)
    header = img.header
    print(header)
    print(header.get_zooms())
    return round(header.get_zooms()[3], 1)


def get_nslices(nifti_file):
    # Looking for nslices in the nifti header
    img = nib.load(nifti_file)
    header = img.header
    return header.get_n_slices()


def get_echotime(nifti_file):
    # Looking for nslices in the nifti header
    img = nib.load(nifti_file)
    header = img.header
    echo_time = str(header["descrip"]).split("TE=")[1].split(";")[0]

    return int(echo_time) / 1000


def get_slicetiming(nifti_file, ascending=True, interleaved=True):
    TR = get_TR(nifti_file)
    nslices = get_nslices(nifti_file)
    print(f"TR = {TR}, Slices = {nslices}", flush=True)

    # Slice Timing
    sliceduration = TR / nslices
    slicetiming = np.linspace(0, TR - sliceduration, nslices)
    if not ascending:
        slicetiming = np.flip(slicetiming)
    if interleaved:
        order = list(range(0, nslices, 2)) + list(range(1, nslices, 2))
        slicetiming[order] = slicetiming.copy()

    slicetiming = slicetiming.tolist()
    return slicetiming
