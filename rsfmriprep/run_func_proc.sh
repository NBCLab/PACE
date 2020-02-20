projdir='/home/data/nbc/Laird_PACE'
dsets=$(dir $projdir/dsets)

for dset in $dsets; do
  if [ ! -d $projdir/dsets/$dset/derivatives/dwidenoise-05.21.2019_fmriprep-1.5.0/ ]; then
      mkdir -p $projdir/dsets/$dset/derivatives/dwidenoise-05.21.2019_fmriprep-1.5.0/
  fi

  subs=$(dir $projdir/dsets/$dset)
  for sub in $subs; do
      if [[ $sub == sub-* ]]; then
          if [ ! -d $proj_dir/dsets/$dset/derivatives/dwidenoise-05.21.2019_fmriprep-1.5.0/$sub ]; then
            echo $sub
            while [ $(squeue -u $USER | wc -l) -gt 40 ]; do
                sleep 30m
            done
            sbatch -J $sub-func-proc \
              -e $projdir/code/errorfiles/$dset-$sub-func-proc \
              -o $projdir/code/outfiles/$dset-$sub-func-proc \
              -c 4 \
              --qos pq_nbc \
              -p centos7 \
              --account iacc_nbc \
              --wrap="python3 $projdir/code/func_proc.py -b $projdir/dsets/$dset -w /scratch/$USER/$sub-func-proc --sub $sub --n_procs 4"
          fi
      fi
  done

done
