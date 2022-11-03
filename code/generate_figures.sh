#!/bin/bash
#SBATCH --job-name=rsfc
#SBATCH --time=11:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4gb
#SBATCH --partition=bluemoon
# Outputs ----------------------------------
#SBATCH --output=log/%x/group/%x-img_%j.out   
#SBATCH --error=log/%x/group/%x-img_%j.err  
# ------------------------------------------

pwd; hostname; date
set -e

module load singularity/3.7.1

TEMP_DIR=/gpfs1/home/m/r/mriedel/pace/templates
bg_img="tpl-MNI152NLin2009cAsym_res-01_desc-brain_T1w.nii.gz"
bg_mask="tpl-MNI152NLin2009cAsym_res-01_desc-brain_mask.nii.gz"
HOST_DIR="/gpfs1/home/m/r/mriedel"
PROJECT="pace"
DSETS_DIR="${HOST_DIR}/${PROJECT}/dsets"
CODE_DIR="${HOST_DIR}/${PROJECT}/code"
IMG_DIR="${HOST_DIR}/${PROJECT}/software"
# seed_regions=(vmPFC insula hippocampus striatum amygdala)
# DATAs=(COC100 ATS105 ALC118)
GSRs=('none' '-gsr')
tests=('1SampletTest' '2SampletTest')
# tests=('1SampletTest')
programs=("3dlmer" "3dttest++")
seed_regions=('insula')
DATAs=(ALC)

for DATA in ${DATAs[@]}; do
    BIDS_DIR="${DSETS_DIR}/dset-${DATA}"
    DERIVS_DIR="${BIDS_DIR}/derivatives"
    OUTPUT_DIR="${DERIVS_DIR}/figures"

    mkdir -p ${OUTPUT_DIR}
    for seed_region in ${seed_regions[@]}; do
        if [[ ${seed_region} ==  "vmPFC" ]]; then
            hemispheres=(none)
        else
            # hemispheres=(lh rh)
            hemispheres=(rh)
        fi
        for hemis in ${hemispheres[@]}; do
            if [[ ${hemis} ==  none ]]; then
                hemis_lb=""
            else
                hemis_lb="_hemis-${hemis}"
            fi
            if [[ ${seed_region} ==  "vmPFC" ]]; then
                ROIs=("vmPFC1" "vmPFC2" "vmPFC3" "vmPFC4" "vmPFC5" "vmPFC6")
            elif [[ ${seed_region} ==  "insula" ]]; then
                ROIs=("insulaD${hemis}" "insulaP${hemis}" "insulaV${hemis}")
            elif [[ ${seed_region} ==  "hippocampus" ]]; then
                ROIs=("hippocampus3solF1${hemis}" "hippocampus3solF2${hemis}" "hippocampus3solF3${hemis}")
            elif [[ ${seed_region} ==  "striatum" ]]; then
                ROIs=("striatumMatchCD${hemis}" "striatumMatchCV${hemis}" "striatumMatchDL${hemis}" "striatumMatchD${hemis}" "striatumMatchR${hemis}" "striatumMatchV${hemis}")
            elif [[ ${seed_region} ==  "amygdala" ]]; then
                ROIs=("amygdala1${hemis}" "amygdala2${hemis}" "amygdala3${hemis}")
            elif [[ ${seed_region} ==  "TPJ" ]]; then
                ROIs=("TPJa" "TPJp")
            fi

            for test in ${tests[@]}; do
                for analysis in ${ROIs[@]}; do
                    for gsr in ${GSRs[@]}; do
                        if [[ ${gsr} ==  "none" ]]; then
                            gsr=""
                            gsr_lb="off"
                        else
                            gsr_lb="on"
                        fi
                        if [[ ${seed_region} ==  "vmPFC" ]]; then
                            RSFC_DIR="${DERIVS_DIR}/rsfc${gsr}-${seed_region}_C1-C2-C3-C4-C5-C6"
                            RSFC_DIR_1="${DERIVS_DIR}/rsfc-${seed_region}_C1-C2-C3-C4-C5-C6"
                        elif [[ ${seed_region} ==  "insula" ]]; then
                            RSFC_DIR="${DERIVS_DIR}/rsfc${gsr}-${seed_region}_D${hemis}-P${hemis}-V${hemis}"
                            RSFC_DIR_1="${DERIVS_DIR}/rsfc-${seed_region}_D${hemis}-P${hemis}-V${hemis}"
                        elif [[ ${seed_region} ==  "hippocampus" ]]; then
                            RSFC_DIR="${DERIVS_DIR}/rsfc${gsr}-${seed_region}_3solF1${hemis}-3solF2${hemis}-3solF3${hemis}"
                            RSFC_DIR_1="${DERIVS_DIR}/rsfc-${seed_region}_3solF1${hemis}-3solF2${hemis}-3solF3${hemis}"
                        elif [[ ${seed_region} ==  "striatum" ]]; then
                            RSFC_DIR="${DERIVS_DIR}/rsfc${gsr}-${seed_region}_matchCD${hemis}-matchCV${hemis}-matchDL${hemis}-matchD${hemis}-matchR${hemis}-matchV${hemis}"
                            RSFC_DIR_1="${DERIVS_DIR}/rsfc-${seed_region}_matchCD${hemis}-matchCV${hemis}-matchDL${hemis}-matchD${hemis}-matchR${hemis}-matchV${hemis}"
                        elif [[ ${seed_region} ==  "amygdala" ]]; then
                            RSFC_DIR="${DERIVS_DIR}/rsfc${gsr}-${seed_region}_C1${hemis}-C2${hemis}-C3${hemis}"
                            RSFC_DIR_1="${DERIVS_DIR}/rsfc-${seed_region}_C1${hemis}-C2${hemis}-C3${hemis}"
                        elif [[ ${seed_region} ==  "TPJ" ]]; then
                            RSFC_DIR="${DERIVS_DIR}/rsfc${gsr}-${seed_region}_Ca-Cp"
                        fi
                        analyses_directory=${RSFC_DIR}

                        SHELL_CMD="singularity exec --cleanenv \
                            -B ${analyses_directory}:/data \
                            -B ${OUTPUT_DIR}:/output \
                            -B ${CODE_DIR}:/code \
                            -B ${TEMP_DIR}:/template \
                            ${IMG_DIR}/afni-22.0.20.sif"

                        pvoxel_uncurrected=0.01
                        pval_uncurrected=`${SHELL_CMD} ptoz ${pvoxel_uncurrected} -2`

                        for program in ${programs[@]}; do
                            if [[ ${program} == '3dlmer' ]]; then
                                test_name="1S2StTest"
                            else
                                test_name=${test}
                            fi
                            if [[ ${test} == '1SampletTest' ]]; then
                                if [[ ${program} == '3dlmer' ]]; then
                                    labels=("group_mean_Z")
                                else
                                    labels=("Group_Zscr")
                                fi
                            fi
                            if [[ ${test} == '2SampletTest' ]]; then
                                if [[ ${program} == '3dlmer' ]]; then
                                    labels=("case_vs_control_Z")
                                else
                                    labels=("case-control_Zscr")
                                fi
                            fi
                            for label in ${labels[@]}; do
                                if [[ ${test} == '1SampletTest' ]]; then
                                    pvoxel=0.0001
                                    pval=`${SHELL_CMD} ptoz $pvoxel -2`
                                    if [[ ${program} == '3dlmer' ]]; then
                                        label_count=8
                                    else
                                        label_count=1
                                    fi
                                fi

                                if [[ ${test} == '2SampletTest' ]]; then
                                    pvoxel=0.001
                                    pval=`${SHELL_CMD} ptoz $pvoxel -2`
                                    if [[ ${program} == '3dlmer' ]]; then
                                        label_count=10
                                    else
                                        label_count=1
                                    fi
                                fi

                                echo
                                echo "Generating image for ${analysis}, ${seed_region}, ${hemis}, ${program}, ${test}, ${label_count}: $label, $pval"
                                result_file_img=${analysis}/sub-group_task-rest_desc-${test}${analysis}Pos_result.nii.gz
                                result_neg_file=group-${program}/${analysis}/sub-group_task-rest_desc-${test}${analysis}Neg_result.nii.gz
                                brik_file=group-${program}/${analysis}/sub-group_task-rest_desc-${test_name}${analysis}_briks+tlrc.BRIK
                                stat_file=group-3dttest++/${analysis}/sub-group_task-rest_desc-${test}${analysis}_briks.CSimA.NN2_2sided.1D
                                arg_file=${analyses_directory}/group-3dttest++/${analysis}/sub-group_task-rest_desc-${test}${analysis}_args.txt

                                rm -rf ${analyses_directory}/group-${program}/${result_file_img}
                                if [[ ${program} == '3dttest++' ]] || [[ ${program} == '3dlmer' ]]; then
                                    convert="${SHELL_CMD} 3dAFNItoNIFTI \
                                                            -prefix /data/group-${program}/${result_file_img} \
                                                            /data/${brik_file}'[$label_count]'"
                                    echo Commandline: $convert
                                    eval $convert 
                                fi

                                remove_nans="${SHELL_CMD} fslmaths \
                                                            /data/group-${program}/${result_file_img} \
                                                            -nan \
                                                            /data/group-${program}/${result_file_img}"
                                echo Commandline: ${remove_nans}
                                eval ${remove_nans}

                                effect_size_file=${analysis}/sub-group_task-rest_desc-${test}${analysis}Cohend_result.nii.gz
                                rm -rf ${analyses_directory}/group-${program}/${effect_size_file}
                                if [[ ${test} == '1SampletTest' ]]; then
                                    n_subjects=$(echo "`wc -l < ${arg_file}` - 1" | bc)
                                    equation=$(echo "a/sqrt(${n_subjects})")
                                fi
                                if [[ ${test} == '2SampletTest' ]]; then
                                    n_subjects=$(echo "`wc -l < ${arg_file}` - 2" | bc)
                                    n1_subjects=$(grep -n "-setB case" ${arg_file} | gawk '{print $1}' FS=":")
                                    n1_subjects=$(echo "${n1_subjects} - 2" | bc -l)
                                    n2_subjects=$(echo "${n_subjects} - ${n1_subjects}" | bc -l)
                                    equation=$(echo "a*sqrt((1/${n1_subjects})+(1/${n2_subjects}))")
                                fi
                                cmd="${SHELL_CMD} 3dcalc \
                                                -a /data/group-${program}/${result_file_img} \
                                                -expr '${equation}' \
                                                -prefix /data/group-${program}/${effect_size_file}"
                                echo Commandline: $cmd
                                eval $cmd

                                if [[ ${test} == '1SampletTest' ]]; then
                                    csize=`${SHELL_CMD} 1dcat /data/${stat_file}"{22}[6]"`
                                fi
                                if [[ ${test} == '2SampletTest' ]]; then
                                    csize=`${SHELL_CMD} 1dcat /data/${stat_file}"{16}[6]"`
                                fi
                                echo $csize

                                posthr_pos_file=${analysis}/sub-group_task-rest_desc-${test}${analysis}PosP${pvoxel}_result.nii.gz
                                posthr_pos_clust=${analysis}/sub-group_task-rest_desc-${test}${analysis}PosP${pvoxel}minextent_result.nii.gz
                                posthr_pos_txt=${analysis}/sub-group_task-rest_desc-${test}${analysis}PosP${pvoxel}minextent_result.txt
                                posthr_neg_file=${analysis}/sub-group_task-rest_desc-${test}${analysis}NegP${pvoxel}_result.nii.gz
                                posthr_neg_clust=${analysis}/sub-group_task-rest_desc-${test}${analysis}NegP${pvoxel}minextent_result.nii.gz
                                posthr_neg_txt=${analysis}/sub-group_task-rest_desc-${test}${analysis}NegP${pvoxel}minextent_result.txt
                                posthr_both_file=${analysis}/sub-group_task-rest_desc-${test}${analysis}BothP${pvoxel}_result.nii.gz
                                posthr_both_clust=${analysis}/sub-group_task-rest_desc-${test}${analysis}BothP${pvoxel}minextent_result.nii.gz

                                cmd="${SHELL_CMD} fslmaths \
                                                    /data/group-${program}/${result_file_img} \
                                                    -thr ${pval_uncurrected} \
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
                                                    -thr ${pval_uncurrected} \
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

                            label_count=$((label_count + 1))
                        done 
                    done

                    RSFC_DIR_2=$(echo ${RSFC_DIR_1} | awk -F'/rsfc-' '{print $1"/rsfc-gsr-"$2}')
                    SHELL_CMD="singularity exec --cleanenv \
                            -B ${RSFC_DIR_1}:/data1 \
                            -B ${RSFC_DIR_2}:/data2 \
                            -B ${OUTPUT_DIR}:/output \
                            -B ${CODE_DIR}:/code \
                            -B ${TEMP_DIR}:/template \
                            ${IMG_DIR}/afni-22.0.20.sif"

                    # Plot unthreshold images
                    out1_3dlmer="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dlmer_gsr-off_map-0unthr_img.png"
                    out1_3dttest="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dttest_gsr-off_map-0unthr_img.png"
                    out2_3dlmer="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dlmer_gsr-on_map-0unthr_img.png"
                    out2_3dttest="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dttest_gsr-on_map-0unthr_img.png"
                    cmd="${SHELL_CMD} python /code/generate_figures.py \
                                        --results 
                                            /data1/group-3dlmer/${result_file_img} \
                                            /data1/group-3dttest++/${result_file_img} \
                                            /data2/group-3dlmer/${result_file_img} \
                                            /data2/group-3dttest++/${result_file_img} \
                                        --outputs 
                                            /output/${out1_3dlmer} \
                                            /output/${out1_3dttest} \
                                            /output/${out2_3dlmer} \
                                            /output/${out2_3dttest} \
                                        --map_types 'stat' 'stat' 'stat' 'stat' \
                                        --template_img /template/${bg_img} \
                                        --template_mask /template/${bg_mask}"
                    echo Commandline: $cmd
                    eval $cmd 

                    # Plot uncurrected threshold
                    out1_3dlmer="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dlmer_gsr-off_map-1uncthr_img.png"
                    out1_3dttest="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dttest_gsr-off_map-1uncthr_img.png"
                    out2_3dlmer="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dlmer_gsr-on_map-1uncthr_img.png"
                    out2_3dttest="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dttest_gsr-on_map-1uncthr_img.png"
                    out1_effect_3dlmer="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dlmer_gsr-off_map-4cohen_img.png"
                    out1_effect_3dttest="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dttest_gsr-off_map-4cohen_img.png"
                    out2_effect_3dlmer="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dlmer_gsr-on_map-4cohen_img.png"
                    out2_effect_3dttest="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dttest_gsr-on_map-4cohen_img.png"
                    cmd="${SHELL_CMD} python /code/generate_figures.py \
                                        --results 
                                            /data1/group-3dlmer/${posthr_both_file} \
                                            /data1/group-3dttest++/${posthr_both_file} \
                                            /data2/group-3dlmer/${posthr_both_file} \
                                            /data2/group-3dttest++/${posthr_both_file} \
                                            /data1/group-3dlmer/${effect_size_file} \
                                            /data1/group-3dttest++/${effect_size_file} \
                                            /data2/group-3dlmer/${effect_size_file} \
                                            /data2/group-3dttest++/${effect_size_file} \
                                        --outputs 
                                            /output/${out1_3dlmer} \
                                            /output/${out1_3dttest} \
                                            /output/${out2_3dlmer} \
                                            /output/${out2_3dttest} \
                                            /output/${out1_effect_3dlmer} \
                                            /output/${out1_effect_3dttest} \
                                            /output/${out2_effect_3dlmer} \
                                            /output/${out2_effect_3dttest} \
                                        --map_types 'stat' 'stat' 'stat' 'stat' 'effect' 'effect' 'effect' 'effect' \
                                        --template_img /template/${bg_img} \
                                        --template_mask /template/${bg_mask}"
                    echo Commandline: $cmd
                    eval $cmd 

                    # Plot thresholded and cluster corrected
                    posthr_both_etac=${analysis}/sub-group_task-rest_desc-${test}${analysis}_briks.etac.ETACmask.global.2sid.05perc.nii.gz

                    out1_3dlmer="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dlmer_gsr-off_map-2clusthr_img.png"
                    out1_3dttest="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dttest_gsr-off_map-2clusthr_img.png"
                    out1_etac="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dttest_gsr-off_map-3etac_img.png"
                    out2_3dlmer="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dlmer_gsr-on_map-2clusthr_img.png"
                    out2_3dttest="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dttest_gsr-on_map-2clusthr_img.png"
                    out2_etac="dset-${DATA}_seed-${seed_region}${hemis_lb}_test-${test}_roi-${analysis}_pipe-3dttest_gsr-on_map-3etac_img.png"
                    cmd="${SHELL_CMD} python /code/generate_figures.py \
                                        --results 
                                            /data1/group-3dlmer/${posthr_both_clust} \
                                            /data1/group-3dttest++/${posthr_both_clust} \
                                            /data1/group-3dttest++/${posthr_both_etac} \
                                            /data2/group-3dlmer/${posthr_both_clust} \
                                            /data2/group-3dttest++/${posthr_both_clust} \
                                            /data2/group-3dttest++/${posthr_both_etac} \
                                        --outputs 
                                            /output/${out1_3dlmer} \
                                             /output/${out1_3dttest} \
                                             /output/${out1_etac} \
                                             /output/${out2_3dlmer} \
                                             /output/${out2_3dttest} \
                                             /output/${out2_etac} \
                                        --map_types 'stat' 'stat' 'binary' 'stat' 'stat' 'binary' \
                                        --template_img /template/${bg_img} \
                                        --template_mask /template/${bg_mask}"
                    echo Commandline: $cmd
                    eval $cmd
                done
            done
        done
    done
done
date