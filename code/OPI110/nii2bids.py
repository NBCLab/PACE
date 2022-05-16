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

    sourcedata = glob(op.join(raw_dir, "*"))
    modalities = {"anat": "T1w", "func": "task-rest_bold", "fmap": ["fieldmap", "magnitude"]}

    for data in sourcedata:
        if op.isdir(data):
            raw_mod = "structural"
            sub_raw_dirs = sorted(glob(op.join(data, raw_mod, "*.nii*")))
            for sub_raw_dir in sub_raw_dirs:
                sub_id = sub_raw_dir.split("/")[-1].split("_")[1].split(".")[0][2:]
                for mod in modalities.keys():
                    if mod == "anat":
                        raw_mod = "structural"
                        in_files = glob(
                            op.join(
                                data,
                                raw_mod,
                                f"*{sub_id}*.nii*",
                            )
                        )
                    elif mod == "func":
                        raw_mod = "resting"
                        in_files = glob(
                            op.join(
                                data,
                                raw_mod,
                                f"*{sub_id}*.nii*",
                            )
                        )
                    elif mod == "fmap":
                        raw_mod = "fieldmaps"
                        in_files = glob(
                            op.join(
                                data,
                                raw_mod,
                                "*",
                                f"*{sub_id}*.nii*",
                            )
                        )

                    # Collect anat and func
                    print(f"Processing {sub_id} modality {mod}")

                    for in_file in in_files:
                        sub = "sub-{:03d}".format(int(sub_id))
                        # Create Bids directory
                        img_bids_dir = op.join(bids_dir, sub, mod)
                        if not op.exists(img_bids_dir):
                            os.makedirs(img_bids_dir)

                        # Conform output name
                        orig_bids_name = os.path.basename(in_file)
                        base, ext = os.path.splitext(orig_bids_name)
                        if ext == ".gz":
                            base2, ext2 = os.path.splitext(base)
                            ext = ext2 + ext
                            if mod == "fmap":
                                if "fieldmap" in base2:
                                    bids_name = f"{sub}_{modalities[mod][0]}{ext}"
                                elif "magnitude" in base2:
                                    bids_name = f"{sub}_{modalities[mod][1]}{ext}"
                            else:
                                bids_name = f"{sub}_{modalities[mod]}{ext}"
                            out_file = op.join(img_bids_dir, bids_name)
                            if not op.isfile(out_file):
                                copyfile(in_file, out_file)
                            print(f"\t{base2} -> {bids_name}", flush=True)
                        else:
                            ext = ext + ".gz"
                            bids_name = f"{sub}_{modalities[mod]}{ext}"
                            out_file = op.join(img_bids_dir, bids_name)
                            if not op.isfile(out_file):
                                with open(in_file, "rb") as f_in:
                                    with gzip.open(out_file, "wb") as f_out:
                                        shutil.copyfileobj(f_in, f_out)
                            print(f"\t{base} -> {bids_name}", flush=True)


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
