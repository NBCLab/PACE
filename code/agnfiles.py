import argparse
import json
import os.path as op
from glob import glob

import pandas as pd


def participants(bids_dir):
    """
    Generate participants.tsv and dataset_description.json

    Parameters
    ----------
    bids_dir : str
    """

    # dataset_description.json
    dictionary = {"Name": "ENIGMA-Addiction", "BIDSVersion": "1.8.0"}
    outfile = op.join(bids_dir, "dataset_description.json")
    with open(outfile, "w") as outfile_json:
        json.dump(dictionary, outfile_json, indent=4)

    # participants.tsv
    sub_dirs = sorted(glob(op.join(bids_dir, "*")))
    df = pd.DataFrame()
    sub_list = []
    for sub_dir in sub_dirs:
        dir_name = op.basename(sub_dir)
        if op.isdir(sub_dir) and ("sub-" in dir_name):
            sub_list.append(dir_name)

    df["participant_id"] = sub_list
    df["exclude"] = [0] * len(sub_dirs)
    df.to_csv(op.join(bids_dir, "participants.tsv"), index=False, sep="\t")


def _get_parser():
    parser = argparse.ArgumentParser(
        description="Generate participants.tsv and dataset_description.json"
    )
    parser.add_argument(
        "-b", "--bids_dir", dest="bids_dir", required=True, help="Path to BIDS dir"
    )
    return parser


def main(bids_dir):
    participants(bids_dir)


def _main(argv=None):
    option = _get_parser().parse_args(argv)
    kwargs = vars(option)
    main(**kwargs)


if __name__ == "__main__":
    _main()
