import argparse
import json
import os.path as op

import bids
import numpy as np
from bids.layout import BIDSLayout

from utils import get_slicetiming, get_TR

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
]


def fixjsons(bids_dir, func_template):
    """
    Fix *.json

    Parameters
    ----------
    bids_dir : str
    """
    layout = BIDSLayout(bids_dir)
    subjects = sorted(layout.get_subjects())

    print(subjects, flush=True)
    for subj in subjects:
        # Functional scans
        scans = layout.get(subject=subj, extension=".nii.gz", task="rest")
        for scan in scans:
            print(scan)
            json_file = layout.get_nearest(scan, extension=".json")
            if json_file is None:
                # Add metadata
                scan_name = op.basename(scan)
                base_name, ext = op.splitext(scan_name)
                if ext == ".gz":
                    base_name, _ = op.splitext(base_name)
                base_path = op.dirname(scan)
                json_file = op.join(base_path, f"{base_name}.json")

                if func_template == "None":
                    metadata = {}
                    # metadata["EchoTime"] = get_echotime(scan)
                    # metadata["EchoTime"] = np.float64(0.03)
                    metadata["RepetitionTime"] = np.float64(get_TR(scan))
                else:
                    metadata = json.loads
                    with open(func_template) as f:
                        metadata = json.load(f)
            else:
                # Fix metadata
                metadata = scan.get_metadata()

            metadata2 = {key: metadata[key] for key in keep_keys if key in metadata.keys()}

            # Add task name
            if "TaskName" not in metadata.keys():
                metadata2["TaskName"] = "rest"
            # Add slice timing
            if "SliceTiming" not in metadata.keys():
                mode = "interleaved"
                metadata2["SliceTiming"] = get_slicetiming(scan, mode, ascending=True)

            # Write json
            with open(json_file, "w") as fo:
                json.dump(metadata2, fo, sort_keys=True, indent=4)

        # Anatomical scans
        scans = layout.get(subject=subj, extension=".nii.gz", suffix="T1w")

        # DWi scans
        scans = layout.get(subject=subj, extension=".nii.gz", suffix="dwi")


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
        "-f",
        "--func_template",
        dest="func_template",
        required=False,
        help="JSON functional template",
    )
    return parser


def main(bids_dir, func_template):
    fixjsons(bids_dir, func_template)


def _main(argv=None):
    option = _get_parser().parse_args(argv)
    kwargs = vars(option)
    main(**kwargs)


if __name__ == "__main__":
    _main()
