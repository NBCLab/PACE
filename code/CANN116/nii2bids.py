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
    sub_raw_dirs = sorted(glob(op.join(raw_dir, "sub-*")))
    for sub_raw_dir in sub_raw_dirs:
        if op.isdir(sub_raw_dir):
            sub = sub_raw_dir.split("/")[-1]

            # Collect anat and func
            modalities = {"anat": "T1w", "func": "task-rest_bold"}
            for mod in modalities.keys():
                print(f"Processing {sub} modality {mod}")
                # Create Bids directory
                img_bids_dir = op.join(bids_dir, sub, mod)
                if op.exists(img_bids_dir):
                    pass
                else:
                    os.makedirs(img_bids_dir)

                img_raw_dir = op.join(sub_raw_dir, mod)
                in_files = glob(op.join(img_raw_dir, "*.nii*"))
                for in_file in in_files:
                    # Conform output name
                    orig_bids_name = os.path.basename(in_file)
                    base, ext = os.path.splitext(orig_bids_name)
                    if ext == ".gz":
                        _, ext2 = os.path.splitext(base)
                        ext = ext2 + ext
                    bids_name = f"{sub}_{modalities[mod]}{ext}"

                    # Copy new names to bids directory
                    out_file = op.join(img_bids_dir, bids_name)
                    if not op.isfile(out_file):
                        copyfile(in_file, out_file)

            # For DWI data
            dwi_dir = op.join(bids_dir, sub, "dwi")
            if os.path.exists(dwi_dir):
                print(f"Processing {sub} modality dwi")

                # Collect dwi
                dirs = ["A", "P"]
                for dir in dirs:
                    in_files = glob(op.join(dwi_dir, f"*_{dir}_*"))
                    for in_file in in_files:
                        orig_bids_name = os.path.basename(in_file)
                        base, ext = os.path.splitext(orig_bids_name)
                        if ext == ".gz":
                            _, ext2 = os.path.splitext(base)
                            ext = ext2 + ext
                        if dir == "A":
                            encode = "pa"
                        elif dir == "P":
                            encode = "ap"

                        bids_name = f"{sub}_dir-{encode}_dwi{ext}"

                        out_file = op.join(dwi_dir, bids_name)
                        if not op.isfile(out_file):
                            os.rename(in_file, out_file)


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
