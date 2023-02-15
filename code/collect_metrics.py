import argparse
import os.path as op
from glob import glob

import numpy as np
import pandas as pd


def _get_parser():
    parser = argparse.ArgumentParser(description="Get subjects to download")
    parser.add_argument(
        "--dset",
        dest="dset",
        required=True,
        help="Path to BIDS directory",
    )
    return parser


def main(dset):
    """Generate list of subject ID from participants.tsv but not in dset"""
    participant_ids_fn = op.join(dset, "participants.tsv")
    participant_ids_df = pd.read_csv(participant_ids_fn, sep="\t")
    participant_ids = participant_ids_df["participant_id"].tolist()

    derivs_dir = op.join(dset, "derivatives")

    metrics = ["FALFF", "REHO"]
    seed_regions = ["vmPFC", "insula", "hippocampus", "striatum", "amygdala"]
    gsr_lb = ["-gsr", ""]

    for gsr in gsr_lb:
        for metric in metrics:
            metric_df = pd.DataFrame()
            metric_df["participant_id"] = participant_ids

            for seed_region in seed_regions:
                if seed_region == "vmPFC":
                    hemispheres = ["none"]
                else:
                    hemispheres = ["lh", "rh"]
                for hemis in hemispheres:
                    if seed_region == "vmPFC":
                        clusters = ["vmPFC1", "vmPFC2", "vmPFC3", "vmPFC4", "vmPFC5", "vmPFC6"]
                        rsfc_dir = op.join(
                            derivs_dir, f"rsfc{gsr}-{seed_region}_C1-C2-C3-C4-C5-C6"
                        )
                    elif seed_region == "insula":
                        clusters = [f"insulaD{hemis}", f"insulaP{hemis}", f"insulaV{hemis}"]
                        rsfc_dir = op.join(
                            derivs_dir, f"rsfc{gsr}-{seed_region}_D{hemis}-P{hemis}-V{hemis}"
                        )
                    elif seed_region == "hippocampus":
                        clusters = [
                            f"hippocampus3solF1{hemis}",
                            f"hippocampus3solF2{hemis}",
                            f"hippocampus3solF3{hemis}",
                        ]
                        rsfc_dir = op.join(
                            derivs_dir,
                            f"rsfc{gsr}-{seed_region}_3solF1{hemis}-3solF2{hemis}-3solF3{hemis}",
                        )
                    elif seed_region == "striatum":
                        clusters = [
                            f"striatumMatchCD{hemis}",
                            f"striatumMatchCV{hemis}",
                            f"striatumMatchDL{hemis}",
                            f"striatumMatchD{hemis}",
                            f"striatumMatchR{hemis}",
                            f"striatumMatchV{hemis}",
                        ]
                        rsfc_dir = op.join(
                            derivs_dir,
                            f"rsfc{gsr}-{seed_region}_matchCD{hemis}-matchCV{hemis}-matchDL{hemis}-matchD{hemis}-matchR{hemis}-matchV{hemis}",
                        )
                    elif seed_region == "amygdala":
                        clusters = [f"amygdala1{hemis}", f"amygdala2{hemis}", f"amygdala3{hemis}"]
                        rsfc_dir = op.join(
                            derivs_dir, f"rsfc{gsr}-{seed_region}_C1{hemis}-C2{hemis}-C3{hemis}"
                        )

                    for cluster in clusters:
                        metric_lst = []
                        for participant_id in participant_ids:
                            print(f"Processing {participant_id}", flush=True)
                            weighted_avg = float("NaN")
                            rsfc_subj_dir = op.join(rsfc_dir, participant_id, "**")

                            # Average fALFF of each voxel within each ROIs
                            roi_subj_falff_files = sorted(
                                glob(
                                    op.join(rsfc_subj_dir, f"*_desc-{cluster}_{metric}.txt"),
                                    recursive=True,
                                )
                            )
                            if len(roi_subj_falff_files) == 0:
                                metric_lst.append(weighted_avg)
                                continue
                            elif len(roi_subj_falff_files) > 1:
                                roi_subj_falff_file = None
                                temp_ses_lst = [
                                    op.basename(x).split("_")[1] for x in roi_subj_falff_files
                                ]
                                for ses_i, temp_ses in enumerate(temp_ses_lst):
                                    if temp_ses.split("-")[0] == "ses":
                                        sub_df = participant_ids_df[
                                            participant_ids_df["participant_id"] == participant_id
                                        ]
                                        sub_df = sub_df.fillna(0)
                                        if "session" in sub_df.columns:
                                            select_ses = int(sub_df["session"].values[0])
                                            if f"ses-{select_ses}" == temp_ses:
                                                roi_subj_falff_file = roi_subj_falff_files[ses_i]
                                                break
                                        if temp_ses == temp_ses_lst[-1]:
                                            roi_subj_falff_file = roi_subj_falff_files[0]
                            elif len(roi_subj_falff_files) == 1:
                                roi_subj_falff_file = roi_subj_falff_files[0]

                            metric_val = pd.read_csv(roi_subj_falff_file, header=None)[0][0]

                            # print(
                            #    f"\tProcessing files\n\t{roi_subj_falff_file}\n\t{metric_val}",
                            #    flush=True,
                            # )
                            metric_lst.append(metric_val)

                        metric_df[cluster] = metric_lst

            metric_df.to_csv(op.join(derivs_dir, f"{metric}{gsr}.tsv"), sep="\t", index=False)


def _main(argv=None):
    option = _get_parser().parse_args(argv)
    kwargs = vars(option)
    main(**kwargs)


if __name__ == "__main__":
    _main()
