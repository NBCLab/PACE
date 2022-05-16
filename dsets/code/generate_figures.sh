#!/bin/bash
#SBATCH --job-name=rsfc
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1gb
#SBATCH --partition=short
# Outputs ----------------------------------
#SBATCH --output=log/%x/group/%x-img_%j.out   
#SBATCH --error=log/%x/group/%x-img_%j.err  
# ------------------------------------------

pwd; hostname; date
set -e

module load singularity/3.7.1

TEMP_DIR=/gpfs1/home/m/r/mriedel/pace/templates
bg_img="tpl-MNI152NLin2009cAsym_res-01_desc-brain_T1w.nii.gz"
HOST_DIR="/gpfs1/home/m/r/mriedel"
PROJECT="pace"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
CODE_DIR="${DSETS_DIR}/code"
IMG_DIR="${HOST_DIR}/${PROJECT}/software"
# seed_regions=(vmPFC insula hippocampus striatum amygdala TPJ)
# hemispheres=(lh rh)
# DATAs=(COC100 ATS105 ALC118)
seed_regions=(insula)
tests=('1SampletTest' '2SampletTest')
programs=("3dmema" "3dttest++")


DATAs=(COC100)
for DATA in ${DATAs[@]}; do
    BIDS_DIR="${DSETS_DIR}/dset-${DATA}"
    DERIVS_DIR="${BIDS_DIR}/derivatives"
    for seed_region in ${seed_regions[@]}; do
        if [[ ${seed_region} ==  "vmPFC" ]]; then
            hemispheres=(none)
        else
            # hemispheres=(lh rh)
            hemispheres=(lh)
        fi
        for hemis in ${hemispheres[@]}; do
            if [[ ${seed_region} ==  "vmPFC" ]]; then
                ROIs=("vmPFC1" "vmPFC2" "vmPFC3" "vmPFC4" "vmPFC5" "vmPFC6")
                RSFC_DIR="${DERIVS_DIR}/rsfc-${seed_region}_C1-C2-C3-C4-C5-C6"
            elif [[ ${seed_region} ==  "insula" ]]; then
                ROIs=("insulaD${hemis}" "insulaP${hemis}" "insulaV${hemis}")
                RSFC_DIR="${DERIVS_DIR}/rsfc-${seed_region}_D${hemis}-P${hemis}-V${hemis}"
            elif [[ ${seed_region} ==  "hippocampus" ]]; then
                ROIs=("hippocampus3solF1${hemis}" "hippocampus3solF2${hemis}" "hippocampus3solF3${hemis}")
                RSFC_DIR="${DERIVS_DIR}/rsfc-${seed_region}_3solF1${hemis}-3solF2${hemis}-3solF3${hemis}"
            elif [[ ${seed_region} ==  "striatum" ]]; then
                ROIs=("striatumMatchCD${hemis}" "striatumMatchCV${hemis}" "striatumMatchDL${hemis}" "striatumMatchD${hemis}" "striatumMatchR${hemis}" "striatumMatchV${hemis}")
                RSFC_DIR="${DERIVS_DIR}/rsfc-${seed_region}_matchCD${hemis}-matchCV${hemis}-matchDL${hemis}-matchD${hemis}-matchR${hemis}-matchV${hemis}"
            elif [[ ${seed_region} ==  "amygdala" ]]; then
                ROIs=("amygdala1${hemis}" "amygdala2${hemis}" "amygdala3${hemis}")
                RSFC_DIR="${DERIVS_DIR}/rsfc-${seed_region}_C1${hemis}-C2${hemis}-C3${hemis}"
            elif [[ ${seed_region} ==  "TPJ" ]]; then
                ROIs=("TPJa" "TPJp")
                RSFC_DIR="${DERIVS_DIR}/rsfc-${seed_region}_Ca-Cp"
            fi
            analyses_directory=${RSFC_DIR}

            IMG_DIR="/gpfs1/home/m/r/mriedel/pace/software"
            SHELL_CMD="singularity exec --cleanenv \
                -B ${analyses_directory}:/data \
                -B ${CODE_DIR}:/code \
                -B ${TEMP_DIR}:/template \
                ${IMG_DIR}/afni-22.0.20.sif"

            for test in ${tests[@]}; do
                for analysis in ${ROIs[@]}; do
                    if [[ ${test} == '1SampletTest' ]]; then
                        labels=("Group_Zscr")
                    fi
                    if [[ ${test} == '2SampletTest' ]]; then
                        abels=("nonUser-User_Zscr")
                    fi
                    for label in ${labels[@]}; do
                        for program in ${programs[@]}; do
                            if [[ ${test} == '1SampletTest' ]]; then
                                pvoxel=0.0001
                                pval=`${SHELL_CMD} ptoz $pvoxel -2`
                                label_count=1
                            fi

                            if [[ ${test} == '2SampletTest' ]]; then
                                pvoxel=0.001
                                pval=`${SHELL_CMD} ptoz $pvoxel -2`
                                if [[ ${program} == '3dmema' ]]; then
                                    label_count=5
                                else
                                    label_count=1
                                fi
                            fi

                            echo "Generating image for ${analysis}, ${seed_region}, ${hemis}, ${test}, $label, $pval"
                            result_file_img=${analysis}/sub-group_task-rest_desc-${test}${analysis}Pos_result.nii.gz
                            result_neg_file=group-${program}/${analysis}/sub-group_task-rest_desc-${test}${analysis}Neg_result.nii.gz
                            brik_file=group-${program}/${analysis}/sub-group_task-rest_desc-${test}${analysis}_briks+tlrc.BRIK
                            stat_file=group-3dttest++/${analysis}/sub-group_task-rest_desc-${test}${analysis}_briks.CSimA.NN2_2sided.1D

                            rm -rf ${analyses_directory}/group-${program}/${result_file_img}
                            if [[ ${program} == '3dttest++' ]]; then
                            convert="${SHELL_CMD} 3dAFNItoNIFTI \
                                                    -prefix /data/group-${program}/${result_file_img} \
                                                    /data/${brik_file}'[$label_count]'"
                            echo Commandline: $convert
                            eval $convert 
                            fi
                            if [[ ${program} == '3dmema' ]]; then
                                arg_file=${analyses_directory}/group-${program}/${analysis}/sub-group_task-rest_desc-${test}${analysis}_args.txt
                                cov_file=${analyses_directory}/group-${program}/${analysis}/sub-group_task-rest_desc-1SampletTest${analysis}_cov.txt
                                n_subjects=$(echo "`wc -l < ${arg_file}` - 1" | bc)
                                n_covariate=$(echo "`head -1 ${cov_file} | wc -w` - 1" | bc)
                                if [[ ${test} == '1SampletTest' ]]; then
                                    DOF=$(echo "${n_subjects} - ${n_covariate} - 1" | bc -l)
                                fi
                                if [[ ${test} == '2SampletTest' ]]; then
                                    DOF=$(echo "${n_subjects} - ${n_covariate} - 2" | bc -l)
                                fi
                                cmd="${SHELL_CMD} 3dcalc \
                                                -a /data/${brik_file}'[$label_count]' \
                                                -expr 'fitt_t2z(a,${DOF})' \
                                                -prefix /data/group-${program}/${result_file_img}"
                                echo Commandline: $cmd
                                eval $cmd
                            fi

                            if [[ ${test} == '1SampletTest' ]]; then
                                csize=`${SHELL_CMD} 1dcat /data/${stat_file}"{22}[6]"`
                            fi
                            if [[ ${test} == '2SampletTest' ]]; then
                                csize=`${SHELL_CMD} 1dcat /data/${stat_file}"{16}[6]"`
                            fi
                            echo $csize

                            posthr_pos_file=${analysis}/sub-group_task-rest_desc-${test}${analysis}PosP${pvoxel}_result.nii.gz
                            posthr_pos_clust=${analysis}/sub-group_task-rest_desc-${test}${analysis}PosP${pvoxel}minextent${csize}_result.nii.gz
                            posthr_pos_txt=${analysis}/sub-group_task-rest_desc-${test}${analysis}PosP${pvoxel}minextent${csize}_result.txt
                            posthr_neg_file=${analysis}/sub-group_task-rest_desc-${test}${analysis}NegP${pvoxel}_result.nii.gz
                            posthr_neg_clust=${analysis}/sub-group_task-rest_desc-${test}${analysis}NegP${pvoxel}minextent${csize}_result.nii.gz
                            posthr_neg_txt=${analysis}/sub-group_task-rest_desc-${test}${analysis}NegP${pvoxel}minextent${csize}_result.txt
                            posthr_both_file=${analysis}/sub-group_task-rest_desc-${test}${analysis}BothP${pvoxel}_result.nii.gz
                            posthr_both_clust=${analysis}/sub-group_task-rest_desc-${test}${analysis}BothP${pvoxel}minextent${csize}_result.nii.gz

                            cmd="${SHELL_CMD} fslmaths \
                                                /data/group-${program}/${result_file_img} \
                                                -thr $pval
                                                /data/group-${program}/${posthr_pos_file}"
                            echo Commandline: $cmd
                            eval $cmd

                            cmd="${SHELL_CMD} cluster \
                                                --in=/data/group-${program}/${result_file_img} \
                                                --thresh=$pval \
                                                --connectivity=6 \
                                                --no_table \
                                                --minextent=$csize \
                                                --othresh=/data/group-${program}/${posthr_pos_clust}"
                            echo Commandline: $cmd
                            # > /data/group-${program}/${posthr_pos_txt}
                            eval $cmd

                            cmd="${SHELL_CMD} fslmaths \
                                                /data/group-${program}/${result_file_img} \
                                                -mul -1 /data/${result_neg_file}"
                            echo Commandline: $cmd
                            eval $cmd 


                            cmd="${SHELL_CMD} fslmaths \
                                                /data/${result_neg_file} \
                                                -thr $pval
                                                /data/group-${program}/${posthr_neg_file}"
                            echo Commandline: $cmd
                            eval $cmd

                            cmd="${SHELL_CMD} cluster \
                                                --in=/data/${result_neg_file} \
                                                --thresh=$pval \
                                                --connectivity=6 \
                                                --no_table \
                                                --minextent=$csize \
                                                --othresh=/data/group-${program}/${posthr_neg_clust}"
                            echo Commandline: $cmd
                            # > /data/group-${program}/${posthr_neg_txt}
                            eval $cmd 

                            cmd="${SHELL_CMD} fslmaths \
                                                /data/group-${program}/${posthr_pos_file} \
                                                -sub /data/group-${program}/${posthr_neg_file} \
                                                /data/group-${program}/${posthr_both_file}"
                            echo Commandline: $cmd
                            eval $cmd 

                            cmd="${SHELL_CMD} fslmaths \
                                                /data/group-${program}/${posthr_pos_clust} \
                                                -sub /data/group-${program}/${posthr_neg_clust} \
                                                /data/group-${program}/${posthr_both_clust}"
                            echo Commandline: $cmd
                            eval $cmd 
                        done
                        
                        # Plot image
                        out_3dmema=group-3dmema/${analysis}/1-${test}${analysis}_unthreshold_result-3dmema.png
                        out_3dttest=group-3dttest++/${analysis}/1-${test}${analysis}_unthreshold_result-3dttest.png
                        cmd="${SHELL_CMD} python /code/generate_figures.py \
                                            --result_3dmema /data/group-3dmema/${result_file_img} \
                                            --result_3dttest /data/group-3dttest++/${result_file_img} \
                                            --template_img /template/${bg_img} \
                                            --out_3dmema /data/${out_3dmema} \
                                            --out_3dttest /data/${out_3dttest}"
                        echo Commandline: $cmd
                        eval $cmd 
                            
                        out_3dmema=group-3dmema/${analysis}/2-${test}${analysis}_threshold_result-3dmema.png
                        out_3dttest=group-3dttest++/${analysis}/2-${test}${analysis}_threshold_result-3dttest.png
                        cmd="${SHELL_CMD} python /code/generate_figures.py \
                                            --result_3dmema /data/group-3dmema/${posthr_both_file} \
                                            --result_3dttest /data/group-3dttest++/${posthr_both_file} \
                                            --template_img /template/${bg_img} \
                                            --out_3dmema /data/${out_3dmema} \
                                            --out_3dttest /data/${out_3dttest}"
                        echo Commandline: $cmd
                        eval $cmd 

                        out_3dmema=group-3dmema/${analysis}/3-${test}${analysis}_threshold+cluster_result-3dmema.png
                        out_3dttest=group-3dttest++/${analysis}/3-${test}${analysis}_threshold+cluster_result-3dttest.png
                        cmd="${SHELL_CMD} python /code/generate_figures.py \
                                            --result_3dmema /data/group-3dmema/${posthr_both_clust} \
                                            --result_3dttest /data/group-3dttest++/${posthr_both_clust} \
                                            --template_img /template/${bg_img} \
                                            --out_3dmema /data/${out_3dmema} \
                                            --out_3dttest /data/${out_3dttest}"
                        echo Commandline: $cmd
                        eval $cmd 

                        label_count=$((label_count + 1))
                    done
                done
            done
        done
    done
done
date