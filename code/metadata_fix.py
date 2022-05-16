import argparse
import json
import os.path as op

import bids
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
        for t, suffix in enumerate(["T1w", "bold", "dwi", "fieldmap", "magnitude"]):
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
                        metadata["RepetitionTime"] = np.float64(get_TR(scan))
                        # For COC106
                        """
                        if suffix == "bold":
                            nvol = get_nvol(scan)
                            print(f"\t\t{nvol}", flush=True)
                            if nvol <= 295:
                                metadata["RepetitionTime"] = np.float64(2)
                            else:
                                metadata["RepetitionTime"] = np.float64(1)
                        else:
                            metadata["RepetitionTime"] = np.float64(get_TR(scan))
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
                    # if "SliceTiming" not in metadata.keys():
                    #    metadata2["SliceTiming"] = get_slicetiming(
                    #        scan, mode, int(ref), ascending=True
                    #    )

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
