import argparse
import json
import os.path as op

import bids
import nibabel as nb
import numpy as np
from bids.layout import BIDSLayout

from utils import get_nvol, get_slicetiming, get_TR

bids.config.set_option("extension_initial_dot", True)

keep_keys = [
    "CogAtlasID",
    "ConversionSoftware",
    "ConversionSoftwareVersion",
    "EchoTime",
    "FlipAngle",
    "ImageType",
    "InversionTime",
    "MagneticFieldStrength",
    "Manufacturer",
    "ManufacturersModelName",
    "ProtocolName",
    "RepetitionTime",
    "ScanOptions",
    "ScanningSequence",
    "SequenceVariant",
    "SeriesNumber",
    "SliceTiming",
    "SoftwareVersions",
    "TaskName",
    "Units",
]


def set_tr(img, tr):
    # Taken from https://neurostars.org/t/bids-validator-error-tr-
    # mismatch-between-nifti-header-and-json-file-and-bids-validator
    # -is-somehow-finding-tr-0-best-solution/1799
    header = img.header.copy()
    header = img.header
    header["pixdim"][4] = tr
    print(header["pixdim"][4], flush=True)
    return img.__class__(img.get_fdata().copy(), img.affine, header)


def fixjsons(bids_dir, mode, ref, templates, multi_ses):
    """
    Fix *.json

    Parameters
    ----------
    bids_dir : str
    """
    layout = BIDSLayout(bids_dir)
    subjects = sorted(layout.get_subjects())
    multi_ses = eval(multi_ses)

    print(subjects, flush=True)
    for subj in subjects:
        # , "T1w", "dwi", "fieldmap", "magnitude"
        for t, suffix in enumerate(["bold"]):
            print(f"Procesing {suffix}", flush=True)
            if suffix == "bold":
                scans = layout.get(subject=subj, extension=".nii.gz", task="rest")
            else:
                scans = layout.get(subject=subj, extension=".nii.gz", suffix=suffix)
            for scan in scans:
                print(f"\t{scan}", flush=True)
                json_file = layout.get_nearest(scan, extension=".json")
                if json_file is None:
                    # Add metadata
                    scan_name = op.basename(scan)
                    base_name, ext = op.splitext(scan_name)
                    if ext == ".gz":
                        base_name, _ = op.splitext(base_name)
                    base_path = op.dirname(scan)
                    json_file = op.join(base_path, f"{base_name}.json")

                    if templates[t] == "None":
                        metadata = {}
                        # metadata["RepetitionTime"] = round(np.float64(get_TR(scan)), 4)
                        metadata["RepetitionTime"] = np.float64(2.0)
                        # For COC106
                        """
                        temp_bold = layout.get(subject=subj, extension=".nii.gz", task="rest")[0]
                        bold_nvol = get_nvol(temp_bold)
                        if suffix == "bold":
                            print(f"\t\t{bold_nvol}", flush=True)
                            if bold_nvol <= 295:
                                metadata["RepetitionTime"] = np.float64(2)
                            else:
                                metadata["RepetitionTime"] = np.float64(1)
                        else:
                            print(f"\t\t{bold_nvol}", flush=True)
                            if bold_nvol <= 295:
                                metadata["RepetitionTime"] = np.float64(0.3)
                            else:
                                metadata["RepetitionTime"] = np.float64(1.9)
                        """
                    else:
                        with open(templates[t]) as f:
                            metadata = json.load(f)
                else:
                    # Fix metadata
                    metadata = scan.get_metadata()

                metadata2 = {key: metadata[key] for key in keep_keys if key in metadata.keys()}

                # Functional scans
                if suffix == "bold":
                    # Add task name
                    if "TaskName" not in metadata.keys():
                        metadata2["TaskName"] = "rest"
                    # Add slice timing
                    if "SliceTiming" not in metadata.keys():
                        metadata2["SliceTiming"] = get_slicetiming(
                            scan, metadata["RepetitionTime"], mode, int(ref), ascending=True
                        )

                if "RepetitionTime" in metadata.keys():
                    img = nb.load(scan)
                    print(img.header["pixdim"][4], flush=True)
                    if img.header["pixdim"][4] != (metadata2["RepetitionTime"],):
                        fixed_img = set_tr(img, metadata2["RepetitionTime"])
                        fixed_img.to_filename(scan)

                # Phasediff Fieldmaps
                if suffix == "fieldmap":
                    # Add units
                    if "Units" not in metadata.keys():
                        metadata2["Units"] = "Hz"
                    # Add IntendedFor
                    if "IntendedFor" not in metadata.keys():
                        if multi_ses:
                            print(f"\t{multi_ses}", flush=True)
                            scan_name = op.basename(scan)
                            scaname_list = scan_name.split("_")
                            ses = scaname_list[1]
                            intended_name = f"sub-{subj}_{ses}_task-rest_bold.nii.gz"
                            intended_for = op.join(scaname_list[1], "func", intended_name)
                        else:
                            intended_name = f"sub-{subj}_task-rest_bold.nii.gz"
                            intended_for = op.join("func", intended_name)

                        metadata2["IntendedFor"] = intended_for

                # Write json
                with open(json_file, "w") as fo:
                    json.dump(metadata2, fo, sort_keys=True, indent=4)


def _get_parser():
    parser = argparse.ArgumentParser(description="Generate participants.tsv")
    parser.add_argument(
        "-b",
        "--bids_dir",
        dest="bids_dir",
        required=True,
        help="Path to BIDS dir",
    )
    parser.add_argument(
        "-m",
        "--mode",
        dest="mode",
        required=False,
        help="Slice order mode",
    )
    parser.add_argument(
        "-r",
        "--ref",
        dest="ref",
        required=False,
        help="First slice",
    )
    parser.add_argument(
        "-t",
        "--templates",
        dest="templates",
        required=False,
        nargs="+",
        help="JSON templates",
    )
    parser.add_argument(
        "-ms",
        "--multi_ses",
        dest="multi_ses",
        default=False,
        required=False,
        help="Ses label",
    )
    return parser


def main(bids_dir, mode, ref, templates, multi_ses):
    fixjsons(bids_dir, mode, ref, templates, multi_ses)


def _main(argv=None):
    option = _get_parser().parse_args(argv)
    kwargs = vars(option)
    main(**kwargs)


if __name__ == "__main__":
    _main()
