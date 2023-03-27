import argparse
import shutil

import nibabel as nib
import numpy as np
from nilearn import image, plotting
import matplotlib.pyplot as plt


def _get_parser():
    parser = argparse.ArgumentParser(description="Plot result image")
    parser.add_argument(
        "--results",
        dest="results",
        required=True,
        nargs="+",
        help="Path to results images",
    )
    parser.add_argument(
        "--outputs",
        dest="outputs",
        required=True,
        nargs="+",
        help="Path to outputs pngs",
    )
    parser.add_argument(
        "--map_types",
        dest="map_types",
        required=True,
        nargs="+",
        help="Map types",
    )
    parser.add_argument(
        "--template_img",
        dest="template_img",
        required=True,
        help="Path to template_img",
    )
    parser.add_argument(
        "--template_mask",
        dest="template_mask",
        required=True,
        help="Path to template mask",
    )
    return parser


def main(results, outputs, map_types, template_img, template_mask):
    template_mask_img = nib.load(template_mask)
    mask_data = template_mask_img.get_fdata().astype(bool)

    get_cut = True
    display = None
    cut_slices = [0, 0, 0]
    for i, in_image in enumerate(results):
        img = nib.load(in_image)
        data = img.get_fdata()
        new_data = data.copy()
        new_data[new_data > 13] = 13
        new_data[new_data < -13] = -13

        if np.all((new_data == 0)):
            print("\t\tNo significant clusters", flush=True)
            _min = 0
        elif map_types[i] != "binary":
            _min = np.min(np.abs(new_data[np.nonzero(new_data)]))
            if _min < 1:
                _min = 0.5
            print(f"\t\t{_min}", flush=True)

        new_img = nib.Nifti1Image(new_data, img.affine, img.header)

        bg_img_obj = nib.load(template_img)
        if map_types[i] == "binary":
            img_res_obj = image.resample_to_img(new_img, bg_img_obj, interpolation="nearest")
        else:

            # shutil.copyfile(in_image, out_nii_nm)

            img_res_obj = image.resample_to_img(new_img, bg_img_obj)
        data_res = img_res_obj.get_fdata()

        # Threshold after resampling to avoid interpolation artefacts
        if (map_types[i] != "effect") and (map_types[i] != "binary"):
            if _min == 0:
                data_res[data_res != 0] = 0
            else:
                data_res[((0 < data_res) & (data_res < _min))] = 0
                data_res[((-_min > data_res) & (data_res > 0))] = 0

        data_res[data_res > 13] = 13
        data_res[data_res < -13] = -13
        data_res[~mask_data] = 0

        new_img_res = nib.Nifti1Image(data_res, img_res_obj.affine, img_res_obj.header)
        if map_types[i] != "binary":
            out_nii_nm = outputs[i].replace(".png", ".nii.gz").replace("map-4cohen", "map-3cohen")
            nib.save(new_img_res, out_nii_nm)

        if (_min != 0) and get_cut:
            cut_slices = plotting.find_cuts.find_xyz_cut_coords(new_img_res, None, None)
            get_cut = False
        elif (_min == 0) and get_cut:
            cut_slices = plotting.find_cuts.find_xyz_cut_coords(new_img_res, None, None)

        print(cut_slices, flush=True)

        # cmap=color_dict[analysis],
        if map_types[i] == "binary":
            display = plotting.plot_roi(
                new_img_res,
                bg_img=template_img,
                colorbar=True,
                annotate=True,
                draw_cross=False,
                black_bg=False,
                dim=0,
                cut_coords=cut_slices,
                display_mode="ortho",
                vmax=None,
            )
        elif map_types[i] == "effect":
            display = plotting.plot_stat_map(
                new_img_res,
                bg_img=template_img,
                colorbar=True,
                vmax=0.3,
                alpha=0.8,
                cmap="coolwarm",
                annotate=True,
                draw_cross=False,
                black_bg=False,
                symmetric_cbar="auto",
                dim=0,
                cut_coords=cut_slices,
                display_mode="ortho",
            )
        elif _min > 0:
            display = plotting.plot_stat_map(
                new_img_res,
                bg_img=template_img,
                colorbar=True,
                threshold=_min,
                annotate=True,
                draw_cross=False,
                black_bg=False,
                symmetric_cbar="auto",
                dim=0,
                cut_coords=cut_slices,
                display_mode="ortho",
                vmax=None,
            )
        elif _min == 0:
            if display is not None:
                display.close()
                display = None
            display = plotting.plot_stat_map(
                new_img_res,
                bg_img=template_img,
                output_file=None,
                colorbar=False,
                annotate=False,
                draw_cross=False,
                black_bg=False,
                dim=0,
                display_mode="ortho",
                vmax=None,
            )
            # -0.35
            # display = plt.figure()
            # plt.clf()
            # plt.close()
            # ha='center', va='center',
            text_kwargs = dict(ha="center", va="center", fontsize=28, color="r")
            plt.text(-0.5, 0.5, "No Significant Clusters", **text_kwargs)
        display.savefig(outputs[i], dpi=1000)
        display.close()
        display = None


def _main(argv=None):
    option = _get_parser().parse_args(argv)
    kwargs = vars(option)
    main(**kwargs)


if __name__ == "__main__":
    _main()
