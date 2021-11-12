import argparse
import gzip
import os
import os.path as op
import shutil
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
    modalities = {"anat": "T1w", "func": "task-rest_bold"}

    sub_raw_dirs = sorted(glob(op.join(raw_dir, "*")))
    for sub_raw_dir in sub_raw_dirs:
        if op.isdir(sub_raw_dir):
            sub = sub_raw_dir.split("/")[-1]
            if "sub-" not in sub:
                if "subj" in sub:
                    # For COC106
                    sub.replace("subj", "")
                    sub = "{:03d}".format(int(sub))
                sub = "sub-" + sub

            img_raw_dirs = sorted(glob(op.join(sub_raw_dir, "*")))
            for img_raw_dir in img_raw_dirs:
                mod = None
                dir_name = os.path.basename(img_raw_dir)
                if ("T1" in dir_name) or ("anat" in dir_name):
                    mod = "anat"
                elif ("est" in dir_name) or ("func" in dir_name):
                    mod = "func"
                else:
                    print("Not func or anat file")
                    break

                print(f"Processing {sub} modality {mod}", flush=True)

                in_files = glob(op.join(img_raw_dir, "*.nii*")) + glob(
                    op.join(img_raw_dir, "*.json")
                )
                for in_file in in_files:
                    # Create Bids directory
                    img_bids_dir = op.join(bids_dir, sub, mod)
                    if not op.exists(img_bids_dir):
                        os.makedirs(img_bids_dir)

                    # Conform output name
                    orig_bids_name = os.path.basename(in_file)
                    base, ext = os.path.splitext(orig_bids_name)
                    if ext == ".nii":
                        ext = ext + ".gz"
                        bids_name = f"{sub}_{modalities[mod]}{ext}"
                        out_file = op.join(img_bids_dir, bids_name)
                        if not op.isfile(out_file):
                            with open(in_file, "rb") as f_in:
                                with gzip.open(out_file, "wb") as f_out:
                                    shutil.copyfileobj(f_in, f_out)
                    else:
                        if ext == ".gz":
                            _, ext2 = os.path.splitext(base)
                            ext = ext2 + ext
                        bids_name = f"{sub}_{modalities[mod]}{ext}"
                        out_file = op.join(img_bids_dir, bids_name)
                        if not op.isfile(out_file):
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
