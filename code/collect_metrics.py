import argparse
import os.path as op
from glob import glob

from neuroCombat import neuroCombat
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
    parser.add_argument(
        "--dset_name",
        dest="dset_name",
        required=True,
        help="Path to BIDS directory",
    )
    return parser


def main(dset, dset_name):
    """Generate list of subject ID from participants.tsv but not in dset"""
    participant_ids_fn = op.join(dset, "participants.tsv")
    participant_ids_df = pd.read_csv(participant_ids_fn, sep="\t")

    derivs_dir = op.join(dset, "derivatives")
    stats_fn = op.join(derivs_dir, f"{dset_name}-sumstats_table.txt")

    stats_df = pd.read_csv(stats_fn, sep="\t")
    participant_ids = stats_df["participant_id"].tolist()

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
                            metric_lst.append(metric_val)

                        metric_df[cluster] = metric_lst

            metric_df.to_csv(
                op.join(derivs_dir, f"{dset_name}-{metric}{gsr}.tsv"), sep="\t", index=False
            )

            # Run Combat
            data_df = pd.merge(metric_df, stats_df, on="participant_id")
            data_df = data_df.dropna()

            covars = data_df[["site", "group"]]
            data = (
                data_df.drop(columns=["participant_id", "site", "group", "age", "gender"])
                .to_numpy()
                .T
            )

            # To specify names of the variables that are categorical:
            categorical_cols = ["group"]
            # To specify the name of the variable that encodes for the scanner/batch covariate:
            batch_col = "site"

            # Harmonization step:
            data_combat = neuroCombat(
                dat=data, covars=covars, batch_col=batch_col, categorical_cols=categorical_cols
            )["data"]

            new_data_df = pd.DataFrame(
                data=data_combat.T,
                index=data_df["participant_id"].to_list(),
                columns=metric_df.columns[1:],
            )
            new_data_df.index.name = "participant_id"
            new_data_df.to_csv(
                op.join(derivs_dir, f"{dset_name}-{metric}{gsr}-combat.tsv"), sep="\t"
            )


def _main(argv=None):
    option = _get_parser().parse_args(argv)
    kwargs = vars(option)
    main(**kwargs)


if __name__ == "__main__":
    _main()
