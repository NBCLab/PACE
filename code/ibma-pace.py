import argparse
import os.path as op
import itertools
import os

import nibabel as nib
from nimare.dataset import Dataset
from nimare.results import MetaResult
from nimare.meta.ibma import Stouffers
from nilearn.glm.thresholding import threshold_stats_img
from nilearn import plotting


def _get_parser():
    parser = argparse.ArgumentParser(description="Run group analysis")
    parser.add_argument(
        "--dset_dir",
        dest="dset_dir",
        required=True,
        help="Path to BIDS directory",
    )
    parser.add_argument(
        "--template",
        dest="template",
        required=True,
        help="Path to BIDS directory",
    )
    parser.add_argument(
        "--index",
        dest="index",
        required=True,
        help="Path to BIDS directory",
    )

    return parser


def main(dset_dir, template, index):
    index = int(index)
    dataset = Dataset.load(op.join(dset_dir, "ibma-pace_dataset.pkl.gz"))
    template_img = nib.load(template)

    dsets = ["ALC", "ATS", "CANN", "COC"]
    seeds = ["amygdala", "hippocampus", "insula", "striatum", "vmPFC"]
    tests = ["1SampletTest", "2SampletTest"]
    gsrs = ["on", "off"]
    pipes = ["3dttest", "3dlmer", "combat"]

    # Parallelize by dsets and seeds
    dsets_seeds = list(itertools.product(dsets, seeds))
    dset, seed = dsets_seeds[index]

    derivs_dir = op.join(dset_dir, f"dset-{dset}", "derivatives")
    out_dir = op.join(derivs_dir, "ibma")
    fig_dir = op.join(derivs_dir, "figures")
    out2_dir = op.join(derivs_dir, "NIfTIs-ibma")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(out2_dir, exist_ok=True)
    print(derivs_dir, out_dir, out2_dir)

    print(f"Running workflow on {dset}, {seed}", flush=True)
    hemispheres = [""] if seed == "vmPFC" else ["lh", "rh"]
    for hemis in hemispheres:
        hemis_lb = "_hemis-lh" if hemis == "lh" else "_hemis-rh" if hemis == "rh" else ""
        if seed == "amygdala":
            rois = [f"amygdala1{hemis}", f"amygdala2{hemis}", f"amygdala3{hemis}"]
        elif seed == "hippocampus":
            rois = [
                f"hippocampus3solF1{hemis}",
                f"hippocampus3solF2{hemis}",
                f"hippocampus3solF3{hemis}",
            ]
        elif seed == "insula":
            rois = [f"insulaD{hemis}", f"insulaP{hemis}", f"insulaV{hemis}"]
        elif seed == "striatum":
            rois = [
                f"striatumMatchCD{hemis}",
                f"striatumMatchCV{hemis}",
                f"striatumMatchDL{hemis}",
                f"striatumMatchD{hemis}",
                f"striatumMatchR{hemis}",
                f"striatumMatchV{hemis}",
            ]
        elif seed == "vmPFC":
            rois = ["vmPFC1", "vmPFC2", "vmPFC3", "vmPFC4", "vmPFC5", "vmPFC6"]

        for roi, test in itertools.product(rois, tests):
            cont_lb = "group-average" if test == "1SampletTest" else "control-case"
            pval = 0.0001 if test == "1SampletTest" else 0.001
            minextent = 30 if test == "1SampletTest" else 90

            studies = []
            for gsr, pipe in itertools.product(gsrs, pipes):
                study = f"dset-{dset}_seed-{seed}{hemis_lb}_roi-{roi}_test-{test}_gsr-{gsr}_pipe-{pipe}"
                studies.append(f"{study}-{cont_lb}")

            nl, tab = ("\n", "\t")
            studies_lst = f"{nl}{tab}".join(studies)

            results_fn = op.join(
                out_dir, f"dset-{dset}_seed-{seed}{hemis_lb}_roi-{roi}_test-{test}_result.pkl.gz"
            )
            if not op.isfile(results_fn):
                print(f"Running IBMA on:{nl}{tab}{studies_lst}", flush=True)
                # Slice Dataset object
                temp_dset = dataset.slice(ids=studies)

                # Run IMBA
                meta = Stouffers(use_sample_size=False, resample=False)
                results = meta.fit(temp_dset)

                # Save MetaResult object
                print(f"\tSaving MetaResult object {results_fn}", flush=True)
                results.save(results_fn)
            else:
                print(f"Loading MetaResult object {results_fn}", flush=True)
                results = MetaResult.load(results_fn)

            z_map = results.get_map("z")
            img_fn = op.join(
                out2_dir,
                f"dset-{dset}_seed-{seed}{hemis_lb}_roi-{roi}_test-{test}_desc-ibma_result.nii.gz",
            )
            if not op.isfile(img_fn):
                print(f"\tSaving image {img_fn}", flush=True)
                nib.save(z_map, img_fn)

            map_fn = op.join(
                fig_dir,
                f"dset-{dset}_seed-{seed}{hemis_lb}_roi-{roi}_test-{test}_desc-ibma_result.png",
            )
            if not op.isfile(map_fn):
                print("Ploting results...", flush=True)
                thresholded_z_map, threshold = threshold_stats_img(
                    z_map,
                    alpha=pval,
                    height_control="fpr",
                    cluster_threshold=minextent,
                    two_sided=True,
                )

                display = plotting.plot_stat_map(
                    thresholded_z_map,
                    bg_img=template_img,
                    colorbar=True,
                    threshold=threshold,
                    annotate=True,
                    draw_cross=False,
                    black_bg=False,
                    symmetric_cbar="auto",
                    dim=0,
                    display_mode="ortho",
                    vmax=None,
                )
                display.savefig(map_fn, dpi=1000)
                display.close()
                display = None


def _main(argv=None):
    option = _get_parser().parse_args(argv)
    kwargs = vars(option)
    main(**kwargs)


if __name__ == "__main__":
    _main()
