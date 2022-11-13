import os.path as op
from glob import glob

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

out_dir = op.abspath("/gpfs1/home/m/r/mriedel/pace/results")

# dsets = ["ALC", "ATS", "CANN", "COC"]
# seeds = ["vmPFC", "insula", "hippocampus", "striatum", "amygdala"]
tests = ["1SampletTest", "2SampletTest"]
dsets = ["COC"]
seeds = ["amygdala"]
# tests = ["1SampletTest"]
roi_dict = {
    "vmPFC1": "vmPFC: Cluster 1",
    "vmPFC2": "vmPFC: Cluster 2",
    "vmPFC3": "vmPFC: Cluster 3",
    "vmPFC4": "vmPFC: Cluster 4",
    "vmPFC5": "vmPFC: Cluster 5",
    "vmPFC6": "vmPFC: Cluster 6",
    "insulaDlh": "Left Insula: Dorsal Anterior",
    "insulaPlh": "Left Insula: Posterior",
    "insulaVlh": "Left Insula: Ventral Anterior",
    "insulaDrh": "Right Insula: Dorsal Anterior",
    "insulaPrh": "Right Insula: Posterior",
    "insulaVrh": "Right Insula: Ventral Anterior",
    "hippocampus3solF1lh": "Left Hippocampus: Anterior",
    "hippocampus3solF2lh": "Left Hippocampus: Intermediate",
    "hippocampus3solF3lh": "Left Hippocampus: Posterior",
    "hippocampus3solF1rh": "Right Hippocampus: Anterior",
    "hippocampus3solF2rh": "Right Hippocampus: Intermediate",
    "hippocampus3solF3rh": "Right Hippocampus: Posterior",
    "striatumMatchCDlh": "Left Striatum: Caudal (Dorsal Part)",
    "striatumMatchCVlh": "Left Striatum: Caudal (Ventral Part)",
    "striatumMatchDLlh": "Left Striatum: Dorsolateral",
    "striatumMatchDlh": "Left Striatum: Dorsal",
    "striatumMatchRlh": "Left Striatum: Rostral",
    "striatumMatchVlh": "Left Striatum: Ventral",
    "striatumMatchCDrh": "Right Striatum: Caudal (Dorsal Part)",
    "striatumMatchCVrh": "Right Striatum: Caudal (Ventral Part)",
    "striatumMatchDLrh": "Right Striatum: Dorsolateral",
    "striatumMatchDrh": "Right Striatum: Dorsal",
    "striatumMatchRrh": "Right Striatum: Rostral",
    "striatumMatchVrh": "Right Striatum: Ventral",
    "amygdala1lh": "Left Amygdala: Cluster 1",
    "amygdala2lh": "Left Amygdala: Cluster 2",
    "amygdala3lh": "Left Amygdala: Cluster 3",
    "amygdala1rh": "Right Amygdala: Cluster 1",
    "amygdala2rh": "Right Amygdala: Cluster 2",
    "amygdala3rh": "Right Amygdala: Cluster 3",
}

for dset in dsets:
    img_dir = op.abspath(f"/gpfs1/home/m/r/mriedel/pace/dsets/dset-{dset}/derivatives/figures")
    for seed in seeds:
        if seed == "vmPFC":
            hemispheres = [""]
        else:
            hemispheres = ["lh", "rh"]
        for hemis in hemispheres:
            if hemis == "":
                hemis_lb = ""
            elif hemis == "lh":
                hemis_lb = "_hemis-lh"
            elif hemis == "rh":
                hemis_lb = "_hemis-rh"
            if seed == "vmPFC":
                rois = ["vmPFC1", "vmPFC2", "vmPFC3", "vmPFC4", "vmPFC5", "vmPFC6"]
            elif seed == "insula":
                rois = [f"insulaD{hemis}", f"insulaP{hemis}", f"insulaV{hemis}"]
            elif seed == "hippocampus":
                rois = [
                    f"hippocampus3solF1{hemis}",
                    f"hippocampus3solF2{hemis}",
                    f"hippocampus3solF3{hemis}",
                ]
            elif seed == "striatum":
                rois = [
                    f"striatumMatchCD{hemis}",
                    f"striatumMatchCV{hemis}",
                    f"striatumMatchDL{hemis}",
                    f"striatumMatchD{hemis}",
                    f"striatumMatchR{hemis}",
                    f"striatumMatchV{hemis}",
                ]
            elif seed == "amygdala":
                rois = [f"amygdala1{hemis}", f"amygdala2{hemis}", f"amygdala3{hemis}"]

            for test in tests:
                for roi in rois:
                    uncthr_lst = sorted(
                        glob(
                            op.join(
                                img_dir,
                                f"dset-{dset}_seed-{seed}{hemis_lb}_test-{test}_roi-{roi}_*map-1uncthr_*",
                            )
                        )
                    )
                    clusthr_lst = sorted(
                        glob(
                            op.join(
                                img_dir,
                                f"dset-{dset}_seed-{seed}{hemis_lb}_test-{test}_roi-{roi}_*map-2clusthr_*",
                            )
                        )
                    )
                    cohen_lst = sorted(
                        glob(
                            op.join(
                                img_dir,
                                f"dset-{dset}_seed-{seed}{hemis_lb}_test-{test}_roi-{roi}_*map-4cohen_*",
                            )
                        )
                    )

                    figure = plt.figure(figsize=(23, 15))
                    figure.subplots_adjust(
                        left=None,
                        bottom=None,
                        right=None,
                        top=None,
                        wspace=0,
                        hspace=0,
                    )
                    gs = GridSpec(6, 3, figure=figure)
                    for image_i in range(len(uncthr_lst)):
                        uncthr_img = mpimg.imread(uncthr_lst[image_i])
                        clusthr_img = mpimg.imread(clusthr_lst[image_i])
                        cohen_img = mpimg.imread(cohen_lst[image_i])

                        ax1 = figure.add_subplot(gs[image_i, 0], aspect="equal")
                        ax1.imshow(uncthr_img)

                        ax2 = figure.add_subplot(gs[image_i, 1], aspect="equal")
                        ax2.imshow(clusthr_img)
                        ax2.set_axis_off()

                        ax3 = figure.add_subplot(gs[image_i, 2], aspect="equal")
                        ax3.imshow(cohen_img)
                        ax3.set_axis_off()

                        if image_i == 0:
                            ax1.set_title("Uncorrected p < 0.01")
                            if test == "1SampletTest":
                                ax2.set_title("pFWE-corrected < 0.05, pvoxel-wise = 0.0001")
                            elif test == "2SampletTest":
                                ax2.set_title("pFWE-corrected < 0.05, pvoxel-wise = 0.001")
                            ax3.set_title("Effect Size: Cohen's d")

                        if hemis == "":
                            prog_idx = 4
                        else:
                            prog_idx = 5
                        prog_label = uncthr_lst[image_i].split("_")[prog_idx].split("-")[1]
                        gsr_label = uncthr_lst[image_i].split("_")[prog_idx + 1].split("-")[1]
                        gsr_lb = ""
                        if gsr_label == "on":
                            gsr_lb = " GSR"

                        axis_label = f"{prog_label}{gsr_lb}"
                        ax1.set_ylabel(axis_label)
                        ax1.set_yticklabels([])
                        ax1.set_xticklabels([])
                        ax1.tick_params(left=False)
                        ax1.tick_params(bottom=False)
                        ax1.set_frame_on(False)

                    if test == "1SampletTest":
                        title = f"Group Average (One-Sample T-Test). {roi_dict[roi]}"
                    elif test == "2SampletTest":
                        title = f"Two-Group Difference (Two-Sample Unpaired T-Test: Control-Case). {roi_dict[roi]}"
                    figure.suptitle(title, fontsize=22)
                    print(op.join(out_dir, f"{dset}-{test}-{roi}.png"), flush=True)
                    plt.savefig(op.join(out_dir, f"{dset}-{test}-{roi}.png"), bbox_inches="tight")
                    plt.close()
