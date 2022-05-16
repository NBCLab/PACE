dsets='nida'

for tmpdset in $dsets; do
    subs=$(dir /home/data/nbc/Laird_PACE/pilot/pace_mega-analysis_pilot/dsets/$tmpdset/)
    for tmpsub in $subs; do
        if [[ $tmpsub == sub-* ]]; then
            if [[ $tmpdset == "nida" ]]; then
                ses=$(dir /home/data/nbc/Laird_PACE/pilot/pace_mega-analysis_pilot/dsets/$tmpdset/$tmpsub)
                for tmpses in $ses; do
                    rsrun=$(dir /home/data/nbc/Laird_PACE/pilot/pace_mega-analysis_pilot/dsets/$tmpdset/$tmpsub/$tmpses/func/*.nii.gz)
                    for tmprsrun in $rsrun; do
                        tmprsrun=${tmprsrun##*/}
                        tmprsrun=${tmprsrun%%.*}
                        if [ ! -e /home/data/nbc/Laird_PACE/pilot/pace_mega-analysis_pilot/dsets/$tmpdset/$tmpsub/$tmpses/func/$tmprsrun.json ]; then
                            tr=$(3dinfo -tr /home/data/nbc/Laird_PACE/pilot/pace_mega-analysis_pilot/dsets/$tmpdset/$tmpsub/$tmpses/func/$tmprsrun.nii.gz)
                            printf '{\n\t"RepetitionTime": %s\n}' "$tr" > /home/data/nbc/Laird_PACE/pilot/pace_mega-analysis_pilot/dsets/$tmpdset/$tmpsub/$tmpses/func/$tmprsrun.json
                        fi
                    done
                done
            else
                rsrun=$(dir /home/data/nbc/Laird_PACE/pilot/pace_mega-analysis_pilot/dsets/$tmpdset/$tmpsub/func/*.nii.gz)
                for tmprsrun in $rsrun; do
                    tmprsrun=${tmprsrun##*/}
                    tmprsrun=${tmprsrun%%.*}
                    if [ ! -e /home/data/nbc/Laird_PACE/pilot/pace_mega-analysis_pilot/dsets/$tmpdset/$tmpsub/func/$tmprsrun.json ]; then
                        tr=$(3dinfo -tr /home/data/nbc/Laird_PACE/pilot/pace_mega-analysis_pilot/dsets/$tmpdset/$tmpsub/func/$tmprsrun.nii.gz)
                        printf '{\n\t"RepetitionTime": %s\n}' "$tr" > /home/data/nbc/Laird_PACE/pilot/pace_mega-analysis_pilot/dsets/$tmpdset/$tmpsub/func/$tmprsrun.json
                    fi
                done
            fi
        fi
    done
done
                
