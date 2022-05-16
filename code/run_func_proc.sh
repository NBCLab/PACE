proj_dir='/users/m/r/mriedel/pace'
dsets=$(dir $proj_dir/dsets/)
dsets='dset-COC100 dset-COH125'

for dset in $dsets; do
    if [ ! -d $proj_dir/dsets/$dsets/derivatives/dwidenoise-05.21.2019_fmriprep-1.5.0/ ]; then
        mkdir -p $proj_dir/dsets/$dset/derivatives/dwidenoise-05.21.2019_fmriprep-1.5.0/
    fi
    if [ ! -d $proj_dir/dsets/$dset/code/errorfiles ]; then
        mkdir -p $proj_dir/dsets/$dset/code/errorfiles
    fi
    if [ ! -d $proj_dir/dsets/$dset/code/outfiles ]; then
        mkdir -p $proj_dir/dsets/$dset/code/outfiles
    fi

    subs=$(dir $proj_dir/dsets/$dset/)
    for sub in $subs; do
        if [[ $sub == sub-* ]]; then
          run_ses=0
          sess=$(dir $proj_dir/dsets/$dset/$sub)
          for ses in $sess; do
            if [[ $ses == ses-* ]]; then
              run_ses=1
              break
            fi
          done

          if [ $run_ses -eq 1 ]; then
            for ses in $sess; do
                if [ ! -d $proj_dir/dsets/$dset/derivatives/dwidenoise-05.21.2019_fmriprep-1.5.0/$sub/$ses ]; then
                    echo $sub $ses
                    while [ $(squeue -u mriedel | wc -l) -gt 20 ]; do
                        sleep 30m
                    done
                    sbatch -J $dset-$sub-$ses-func-proc -e $proj_dir/dsets/$dset/code/errorfiles/$dset-$sub-$ses-func-proc -o $proj_dir/dsets/$dset/code/outfiles/$dset-$sub-$ses-func-proc -c 12 -p bigmem --wrap="python3 $proj_dir/code/func_proc.py -b $proj_dir/dsets/$dset -w $proj_dir/scratch/$dset-$sub-$ses-func-proc --sub $sub --ses $ses --n_procs 12"
                fi
            done
          else
            if [ ! -d $proj_dir/dsets/$dset/derivatives/dwidenoise-05.21.2019_fmriprep-1.5.0/$sub ]; then
                echo $sub
                while [ $(squeue -u mriedel | wc -l) -gt 20 ]; do
                    sleep 30m
                done
                sbatch -J $dset-$sub-func-proc -e $proj_dir/dsets/$dset/code/errorfiles/$dset-$sub-func-proc -o $proj_dir/dsets/$dset/code/outfiles/$dset-$sub-func-proc -c 12 -p bigmem --wrap="python3 $proj_dir/code/func_proc.py -b $proj_dir/dsets/$dset -w $proj_dir/scratch/$dset-$sub-func-proc --sub $sub --n_procs 12"
            fi
          fi
        fi
    done
done
