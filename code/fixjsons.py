import argparse
import json

import bids
from bids.layout import BIDSLayout

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


def fixjsons(bids_dir):
    """
    Fix *.json

    Parameters
    ----------
    bids_dir : str
    """
    layout = BIDSLayout(bids_dir)
    subjects = layout.get_subjects()

    # Functional scans
    print(subjects)
    for subj in subjects:
        scans = layout.get(subject=subj, extension=".nii.gz", task="rest")
        for scan in scans:
            json_file = layout.get_nearest(scan, extension=".json")
            metadata = scan.get_metadata()
            metadata2 = {key: metadata[key] for key in keep_keys if key in metadata.keys()}
            if "TaskName" not in metadata.keys():
                metadata2["TaskName"] = "rest"
                with open(json_file, "w") as fo:
                    json.dump(metadata2, fo, sort_keys=True, indent=4)


def _get_parser():
    parser = argparse.ArgumentParser(description="Generate participants.tsv")
    parser.add_argument(
        "-b", "--bids_dir", dest="bids_dir", required=True, help="Path to BIDS dir"
    )
    return parser


def main(bids_dir):
    fixjsons(bids_dir)


def _main(argv=None):
    option = _get_parser().parse_args(argv)
    kwargs = vars(option)
    main(**kwargs)


if __name__ == "__main__":
    _main()
