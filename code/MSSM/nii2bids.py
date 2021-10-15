import argparse
import os
import os.path as op
from glob import glob
from shutil import copyfile


def nii2bids(bids_dir, raw_dir):
    """
    Rename and restructre nifti files.

    Parameters
    ----------
    deriv_dir : str
    work_dir : str
    """

    # Collect anat and func
    modalities = {"T1w": "anat", "T2w": "anat", "dwi": "dwi", "events": "func", "bold": "func"}

    in_files = sorted(glob(op.join(raw_dir, "*")))
    prev_sub = None
    prev_ses = None
    updt_ses = None
    for in_file in in_files:
        orig_bids_name = os.path.basename(in_file)
        base, ext = os.path.splitext(orig_bids_name)
        if ext == ".gz":
            base, ext2 = os.path.splitext(base)
            if ext2 == ".nii_":
                ext2 = ".nii"
            ext = ext2 + ext
        base_list = base.split("_")
        sub = base_list[0]
        ses = base_list[1]
        if (sub == prev_sub) and ((ses != prev_ses) or (updt_ses == "ses-02")):
            base_list[1] = "ses-02"
        else:
            base_list[1] = "ses-01"
        prev_ses = ses
        prev_sub = sub
        updt_ses = base_list[1]
        base = "_".join(base_list)

        mod = base_list[-1]
        if mod == "scans":
            continue

        if mod == "sbref":
            if base_list[2] == "task-rest":
                mod_dir = "func"
            else:
                mod_dir = "dwi"
        else:
            mod_dir = modalities[mod]

        # Create Bids directory
        img_bids_dir = op.join(bids_dir, sub, updt_ses, mod_dir)
        if op.exists(img_bids_dir):
            pass
        else:
            os.makedirs(img_bids_dir)

        bids_name = f"{base}{ext}"
        print(f"Storing file {bids_name}")
        out_file = op.join(img_bids_dir, bids_name)
        copyfile(in_file, out_file)


def _get_parser():
    parser = argparse.ArgumentParser(
        description="Collecting partially preprocesed image from fmriprep"
    )
    parser.add_argument(
        "-b", "--bids_dir", dest="bids_dir", required=True, help="Path to BIDS dir"
    )
    parser.add_argument(
        "-r", "--raw_dir", dest="raw_dir", required=True, help="Path to raw data dir"
    )
    return parser


def main(bids_dir, raw_dir):
    nii2bids(bids_dir, raw_dir)


def _main(argv=None):
    option = _get_parser().parse_args(argv)
    kwargs = vars(option)
    main(**kwargs)


if __name__ == "__main__":
    _main()
