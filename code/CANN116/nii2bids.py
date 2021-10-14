import argparse
import os
import os.path as op
import zipfile
from glob import glob
from shutil import copyfile

import nibabel as nib


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
        sub = sub_raw_dir.split("/")[-1]

        # Collect anat and func
        modalities = {"anat": "T1w", "func": "taks-rest_bold"}
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
                copyfile(in_file, out_file)

        # For DWI data
        dwi_dir = op.join(sub_raw_dir, "dwi")
        if (os.path.exists(dwi_dir)) and (sub != "sub-1011"):
            print(f"Processing {sub} modality dwi")
            img_bids_dir = op.join(bids_dir, sub, "dwi")

            # Unzip raw imgs dir
            zip_dir = glob(op.join(sub_raw_dir, "dwi", "Z*.zip"))[0]
            with zipfile.ZipFile(zip_dir, "r") as zip_ref:
                zip_ref.extractall(dwi_dir)

            # Create Bids directory
            if op.exists(img_bids_dir):
                pass
            else:
                os.makedirs(img_bids_dir)

            # Collect dwi
            acqs = ["A", "P"]
            for acq in acqs:
                img_files = glob(op.join(dwi_dir, "*", f"*_{acq}_*.PAR"))
                bvec_files = glob(op.join(dwi_dir, "*", f"*_{acq}_*.bvec"))
                bval_files = glob(op.join(dwi_dir, "*", f"*_{acq}_*.bval"))
                for file, img_file in enumerate(img_files):
                    # Conform output name
                    extensions = ["nii.gz", "bvec", "bval"]
                    for ext in extensions:
                        bids_name = f"{sub}_acq-{acq.lower()}_dwi.{ext}"
                        out_file = op.join(bids_dir, sub, "dwi", bids_name)
                        if ext == "nii.gz":
                            img = nib.load(img_file)
                            nifti = nib.Nifti1Image(img.dataobj, img.affine, header=img.header)
                            nifti.set_data_dtype("<f4")
                            nifti.to_filename(out_file)
                        elif ext == "bvec":
                            copyfile(bvec_files[file], out_file)
                        else:
                            copyfile(bval_files[file], out_file)


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
