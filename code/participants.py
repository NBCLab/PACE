import argparse
import os.path as op
from glob import glob

import pandas as pd


def participants(bids_dir):
    """
    Generate participants.tsv

    Parameters
    ----------
    bids_dir : str
    """

    sub_dirs = sorted(glob(op.join(bids_dir, "*")))
    df = pd.DataFrame()
    sub_list = []
    for sub_dir in sub_dirs:
        dir_name = op.basename(sub_dir)
        if op.isdir(sub_dir) and ("sub-" in dir_name):
            sub_list.append(dir_name)

    df["participant_id"] = sub_list
    df.to_csv(op.join(bids_dir, "participants.tsv"), index=False, sep="\t")


def _get_parser():
    parser = argparse.ArgumentParser(description="Generate participants.tsv")
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
