proj_dir='/users/m/r/mriedel/pace/'
dsets=$(dir $proj_dir/dsets/)

for dset in $dsets; do
    if [ ! -d $proj_dir/dsets/$dsets/derivatives/mriqc_0.15.1/ ]; then
        mkdir -p $proj_dir/dsets/$dset/derivatives/mriqc_0.15.1/
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
                if [ ! -d $proj_dir/dsets/$dset/derivatives/mriqc_0.15.1/$sub/$ses ]; then
                    echo $sub $ses
                    while [ $(squeue -u mriedel | wc -l) -gt 20 ]; do
                        sleep 30m
                    done
                    sbatch -J $dset-$sub-$ses-mriqc -e $proj_dir/dsets/$dset/code/errorfiles/$dset-$sub-$ses-mriqc -o $proj_dir/dsets/$dset/code/outfiles/$dset-$sub-$ses-mriqc -n 6 -p bigmem --wrap="python3 $proj_dir/code/mriqc.py -b $proj_dir/dsets/$dset -w $proj_dir/scratch/$dset-$sub-$ses-mriqc --sub $sub --ses $ses --n_procs 6"
                fi
            done
          else
            if [ ! -d $proj_dir/dsets/$dset/derivatives/mriqc_0.15.1/$sub ]; then
                echo $sub
                while [ $(squeue -u mriedel | wc -l) -gt 20 ]; do
                    sleep 30m
                done
                sbatch -J $dset-$sub-mriqc -e $proj_dir/dsets/$dset/code/errorfiles/$dset-$sub-mriqc -o $proj_dir/dsets/$dset/code/outfiles/$dset-$sub-mriqc -n 6 -p bigmem --wrap="python3 $proj_dir/code/mriqc.py -b $proj_dir/dsets/$dset -w $proj_dir/scratch/$dset-$sub-mriqc --sub $sub --n_procs 6"
            fi
          fi
        fi
    done
done
