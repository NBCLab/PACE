import argparse
import json
import os.path as op


def participants(bids_dir):
    """
    Generate dataset_description.json

    Parameters
    ----------
    bids_dir : str
    """

    # Data to be written
    dictionary = {"Name": "ENIGMA-Addiction", "BIDSVersion": "1.6.0"}

    outfile = op.join(bids_dir, "dataset_description.json")
    with open(outfile, "w") as outfile_json:
        json.dump(dictionary, outfile_json, indent=4)


def _get_parser():
    parser = argparse.ArgumentParser(description="Generate dataset_description.json")
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
