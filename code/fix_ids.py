import argparse
import json
import os.path as op
from glob import glob
import pathlib
import os
import shutil

import pandas as pd


# participants.tsv
dsets_dirs = "/gpfs1/home/m/r/mriedel/pace/dsets"

# studies = ["ALC", "ATS", "CANN", "COC", "COH", "OPI"]
# studies = ["ALC"]
# studies = ["ATS", "CANN", "COC", "COH", "OPI"]
studies = ["NIC123"]

for study in studies:
    df = pd.DataFrame()
    pt_id_lst = []
    new_id_lst = []
    site_lst = []

    dset_dirs = sorted(glob(op.join(dsets_dirs, f"dset-{study}1*")))
    for dset_dir in dset_dirs:
        print(dset_dir)
        dset_id = dset_dir.split("/")[-1].split("-")[1]
        # old_files = sorted(glob(op.join(dset_dir, "**", "sub-*")))
        os.chdir(dset_dir)
        files_str = sorted(glob("**/sub-*", recursive=True))
        for file_str in files_str:
            # print(file_str)
            pt_base_id, _ = op.splitext(file_str)
            pt_id = op.basename(pt_base_id).split("_")[0].split("-")[1]

            if pt_id != "group":
                # Armonize IDs
                if dset_id == "ALC108":
                    temp_id = pt_id[1:]
                elif dset_id == "ALC118":
                    temp_id = "0" + pt_id
                elif dset_id == "ALC123":
                    temp_id = "0" + pt_id
                elif dset_id == "ALC128":
                    temp_id = pt_id.upper()
                elif dset_id == "ALC134":
                    temp_id = pt_id[:-2]
                elif dset_id == "ATS105":
                    temp_id = pt_id[3:]
                elif dset_id == "ATS107":
                    temp_id = pt_id
                elif dset_id == "CANN116":
                    temp_id = "00" + pt_id
                elif dset_id == "CANN117":
                    temp_id = "000" + pt_id
                elif dset_id == "CANN122":
                    temp_id = pt_id[:4] + pt_id[-2:]
                elif dset_id == "COC100":
                    temp_id = "0" + pt_id
                elif dset_id == "COC106":
                    temp_id = "0" + pt_id
                elif dset_id == "COC126":
                    temp_id = pt_id[1:]
                elif dset_id == "COH125":
                    temp_id = pt_id
                elif dset_id == "OPI105":
                    temp_id = "0" + pt_id
                elif dset_id == "OPI107":
                    temp_id = pt_id
                elif dset_id == "OPI110":
                    temp_id = "0" + pt_id
                elif dset_id == "NIC123":
                    temp_id = "0" + pt_id

                new_id = dset_id + temp_id
                pt_id_tpl = tuple(pt_id_lst)
                new_id_tpl = tuple(new_id_lst)
                if not new_id.startswith(new_id_tpl):
                    pt_id_lst.append(pt_id)
                    site_lst.append(dset_id)
                    new_id_lst.append(new_id)

                new_str = file_str.replace(f"sub-{pt_id}", f"sub-{new_id}")
                # assert len(new_id) == 10

                initial_path = op.join(dset_dir, file_str)
                if op.isfile(initial_path):
                    print(initial_path, flush=True)
                    final_path = op.join(dsets_dirs, f"dset-{study}", new_str)
            
                    final_dir = os.path.dirname(final_path)
                    if op.exists(final_dir):
                        pass
                    else:
                        os.makedirs(final_dir)
                
                    if not op.isfile(final_path):
                        shutil.copyfile(initial_path, final_path)
                        print(final_path, flush=True)
                    print("", flush=True)

                elif len(file_str.split("/")) > 1:
                    if file_str.split("/")[-2] == "freesurfer":
                        initial_fs_dir = op.join(dset_dir, file_str)
                        print(initial_fs_dir, flush=True)

                        final_fs_dir = op.join(dsets_dirs, f"dset-{study}", new_str)
                        if op.exists(final_fs_dir):
                            pass
                        else:
                            print(final_fs_dir, flush=True)
                            shutil.copytree(initial_fs_dir, final_fs_dir)
                        print("", flush=True)


    df["participant_id"] = new_id_lst
    df["original_id"] = pt_id_lst
    df["site"] = site_lst

    print(df)
    assert len(new_id_lst) == len(pt_id_lst)
    assert len(new_id_lst) == len(site_lst)

    df.to_csv(op.join(dsets_dirs, f"dset-{study}", "participants.tsv"), index=False, sep="\t")
