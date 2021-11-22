import argparse
import os
import os.path as op
from glob import glob

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
import seaborn as sns
from ddmra import analysis, plot_analysis, run_analyses, utils
from scipy.stats import ks_2samp, normaltest
from sklearn.neighbors import KernelDensity

sns.set_style("white")


def _get_parser():
    parser = argparse.ArgumentParser(description="Perform QCFC analyses")
    parser.add_argument(
        "--dset",
        dest="dset",
        required=True,
        help="Path to BIDS dataset",
    )
    parser.add_argument(
        "--subjects",
        dest="subjects",
        required=True,
        nargs="+",
        help="List with subject IDs",
    )
    parser.add_argument(
        "--n_jobs",
        dest="n_jobs",
        required=True,
        help="CPUs",
    )
    parser.add_argument(
        "--qc_thresh",
        dest="qc_thresh",
        required=True,
        help="FD threshold",
    )
    return parser


def get_kde(in_vector):
    print("\tKDE for QCFC", flush=True)
    bw_used = 0.05
    a = in_vector.reshape(-1, 1)
    kde = KernelDensity(kernel="gaussian", bandwidth=bw_used).fit(a.reshape(-1, 1))
    s = np.linspace(in_vector.min(), in_vector.max(), num=in_vector.shape[0])
    e = kde.score_samples(s.reshape(-1, 1))
    return s, e


def ks_test(x, y):
    """Kolmogorov–Smirnov test"""
    x = np.array(x)
    y = np.array(y)
    distance, pval = ks_2samp(x, y)

    return distance, pval


def qcfc_plot(in_dir, subjects, qc):
    # Adapted from https://github.com/ME-ICA/ddmra/blob/main/ddmra/plotting.py
    """Plot the results for all three analyses from a workflow run and save to a file.

    This function leverages the output file structure of :func:`workflows.run_analyses`.
    It writes out an image (analysis_results.png) to the output directory.

    Parameters
    ----------
    in_dir : str
        Path to the output directory of a ``run_analyses`` run.
    """
    METRIC_LABELS = {
        "rsfc": "RSFC distribution",
        "qcrsfcD": "QC:RSFC distribution",
        "qcrsfc": r"QC:RSFC $z_{r}$" + "\n(QC = mean FD)",
        "highlow": "High-low motion\n" + r"${\Delta}z_{r}$",
    }
    YLIMS = {
        "rsfc": (-1.0, 1.0),
        "qcrsfcD": (-1.0, 1.0),
        "qcrsfc": (-1.0, 1.0),
        "highlow": (-1.0, 1.0),
    }
    analysis_values = pd.read_table(op.join(in_dir, "analysis_values.tsv.gz"))
    smoothing_curves = pd.read_table(op.join(in_dir, "smoothing_curves.tsv.gz"))
    null_curves = np.load(op.join(in_dir, "null_smoothing_curves.npz"))
    sub_matrices = np.load(op.join(in_dir, "rsfc.npz"))
    corr_mats = sub_matrices["rsfc"]

    fig, axes = plt.subplots(figsize=(32, 8), ncols=len(METRIC_LABELS))

    for i_analysis, (analysis_type, label) in enumerate(METRIC_LABELS.items()):
        if analysis_type == "rsfc":
            for subject in range(len(subjects)):
                xlim = (-1, 1)
                values = corr_mats[subject]
                ax = sns.kdeplot(values, bw_method=0.1, fill=True, ax=axes[i_analysis])
            ax.set_xlabel(label, fontsize=32, labelpad=-30)
            ax.set_xticks(xlim)
            ax.set_xticklabels(xlim, fontsize=32)
            ax.set_xlim(xlim)
            ax.set_ylabel("")
            ax.set_yticklabels("")
            ax.vlines(x=0, ymin=0, ymax=values.max() + 0.05, colors="k", ls="-", lw=5)

        elif analysis_type == "qcrsfcD":
            values = analysis_values["qcrsfc"].values
            smoothing_curve = smoothing_curves["qcrsfc"].values
            # null_curve = null_curves["qcrsfc"][0]

            ax = sns.kdeplot(values, bw_method=0.1, fill=True, color="gray", ax=axes[i_analysis])
            ax.vlines(x=0, ymin=0, ymax=2.2, colors="k", ls="-", lw=5)

            # Create unsmoothed null_curve
            mean_qcs = np.array([np.mean(subj_qc) for subj_qc in qc])
            perm_mean_qcs = np.random.RandomState(seed=0).permutation(mean_qcs)
            perm_qcrsfc_zs = analysis.qcrsfc_analysis(perm_mean_qcs, corr_mats)
            distan, pval = ks_test(values, perm_qcrsfc_zs)
            print(f"\tSimilarity {round((1-distan)*100,1)}%", flush=True)
            sns.kdeplot(
                perm_qcrsfc_zs, bw_method=0.1, color="red", ls="--", lw=5, ax=axes[i_analysis]
            )
            ax.annotate(
                f"{round(np.mean(values),2)}"
                + r"$\pm$"
                + f"{round(np.std(values),2)}"
                + f"\n{round((1-distan)*100,1)}% math with NH",
                xy=(1, 1),
                xycoords="axes fraction",
                horizontalalignment="right",
                verticalalignment="top",
                fontsize=32,
            )
            ax.set_xlabel(label, fontsize=32, labelpad=-30)
            ax.set_xticks(xlim)
            ax.set_xticklabels(xlim, fontsize=32)
            ax.set_xlim(xlim)
            ax.set_ylabel("")
            ax.set_yticklabels("")
        else:
            values = analysis_values[analysis_type].values
            smoothing_curve = smoothing_curves[analysis_type].values

            fig, axes[i_analysis] = plot_analysis(
                values,
                analysis_values["distance"],
                smoothing_curve,
                smoothing_curves["distance"],
                null_curves[analysis_type],
                n_lines=50,
                ylim=YLIMS[analysis_type],
                metric_name=label,
                fig=fig,
                ax=axes[i_analysis],
            )

    fig.savefig(op.join(in_dir, "new_analysis_results.png"), dpi=100)


def main(dset, subjects, n_jobs, qc_thresh):
    """Run QCFC workflow on a given dataset."""
    # Taken from Taylor's pipeline
    deriv_dir = op.join(dset, "derivatives")
    nuis_dir = op.join(deriv_dir, "3dtproject")
    preproc_dir = op.join(deriv_dir, "fmriprep-20.2.5", "fmriprep")
    space = "MNI152NLin2009cAsym"
    qc_thresh = float(qc_thresh)
    n_jobs = int(n_jobs)
    dummy_scans = 5

    preproc_qcs = []
    denoised_qcs = []
    scrub_qcs = []
    preproc_imgs = []
    denoised_imgs = []
    scrub_imgs = []
    for subject in subjects:
        preproc_subj_func_dir = op.join(preproc_dir, subject, "func")
        nuis_subj_dir = op.join(nuis_dir, subject, "func")

        # Collect important files
        confounds_files = glob(op.join(preproc_subj_func_dir, "*_desc-confounds_timeseries.tsv"))
        assert len(confounds_files) == 1
        confounds_file = confounds_files[0]

        preproc_files = glob(
            op.join(preproc_subj_func_dir, f"*task-rest*_space-{space}*_desc-preproc_bold.nii.gz")
        )
        assert len(preproc_files) == 1
        preproc_file = preproc_files[0]

        denoised_files = glob(op.join(nuis_subj_dir, "*_desc-aCompCor_bold.nii.gz"))
        assert len(denoised_files) == 1
        denoised_file = denoised_files[0]

        scrub_files = glob(op.join(nuis_subj_dir, "*_desc-aCompCorScrub_bold.nii.gz"))
        assert len(scrub_files) == 1
        scrub_file = scrub_files[0]

        censor_files = glob(op.join(nuis_subj_dir, "*_scrubbing*.1D"))
        assert len(censor_files) == 1
        tr_censor = pd.read_csv(censor_files[0], header=None)
        tr_keep = tr_censor.index[tr_censor[0] == 0].tolist()

        confounds_df = pd.read_csv(confounds_file, sep="\t")
        qc = confounds_df["framewise_displacement"].values
        qc = np.nan_to_num(qc, 0)

        preproc_qcs.append(qc)
        denoised_qcs.append(qc[dummy_scans:])
        scrub_qcs.append(np.delete(qc[dummy_scans:], tr_keep))

        preproc_imgs.append(preproc_file)
        denoised_imgs.append(denoised_file)
        scrub_imgs.append(scrub_file)

    # ###################
    # QCFC analyses
    # ###################
    imgs_dict = {"preproc": preproc_imgs, "denoised": denoised_imgs, "scrubbing": scrub_imgs}
    for imgs in imgs_dict.keys():
        if imgs == "denoised":
            qc_list = denoised_qcs
        elif imgs == "scrubbing":
            qc_list = scrub_qcs
        else:
            qc_list = preproc_qcs

        print(f"\tRun QCFC workflow on {len(denoised_imgs)} subjects for {imgs}", flush=True)
        print(f"\tUse {len(qc_list)} fd vectors", flush=True)
        assert len(imgs_dict[imgs]) == len(qc_list)

        out_dir = op.join(deriv_dir, "QCFC", imgs)
        os.makedirs(out_dir, exist_ok=True)

        run_analyses(
            imgs_dict[imgs],
            qc_list,
            out_dir=out_dir,
            n_iters=10000,
            n_jobs=n_jobs,
            qc_thresh=qc_thresh,
        )
        # Create QC plots
        qcfc_plot(out_dir, subjects, qc_list)


def _main(argv=None):
    option = _get_parser().parse_args(argv)
    kwargs = vars(option)
    main(**kwargs)


if __name__ == "__main__":
    _main()
