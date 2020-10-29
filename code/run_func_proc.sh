proj_dir='/gpfs1/home/m/r/mriedel/pace/'
dsets=$(dir $proj_dir/dsets/)

for tmpdset in $dsets; do
    if [ ! -d $proj_dir/dsets/$tmpdset/derivatives/dwidenoise-05.21.2019_fmriprep-1.5.0/ ]; then
        mkdir -p $proj_dir/dsets/$tmpdset/derivatives/dwidenoise-05.21.2019_fmriprep-1.5.0/
    fi

    subs=$(dir $proj_dir/dsets/$tmpdset/)
    for tmpsub in $subs; do
        if [[ $tmpsub == sub-* ]]; then
            if [ ! -d $proj_dir/dsets/$tmpdset/derivatives/dwidenoise-05.21.2019_fmriprep-1.5.0/$tmpsub ]; then
                echo $tmpsub
                #while [ $(squeue -u miriedel | wc -l) -gt 22 ]; do
                #    sleep 30m
                #done
                sbatch -J $tmpdset-$tmpsub-func-proc -e $proj_dir/dsets/$tmpdset/code/errorfiles/$tmpdset-$tmpsub-func-proc -o $proj_dir/dsets/$tmpdset/code/outfiles/$tmpdset-$tmpsub-func-proc -n 4 --qos pq_nbc -p centos7 --account acc_nbc --wrap="python3 $proj_dir/code/func_proc.py -b $proj_dir/dsets/$tmpdset -w /gpfs2/scratch/$USER/$tmpdset-$tmpsub-func-proc --sub $tmpsub --n_procs 4"
            fi
        fi
    done
done
