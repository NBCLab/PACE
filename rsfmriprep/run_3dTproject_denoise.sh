projdir='/home/data/nbc/Laird_PACE'
deriv=denoise_3dTproject-acompcor+12mo+FD0.3mm

dsets=$(dir $projdir/dsets)

for dset in $dsets; do

  if [ ! -d $projdir/$dsets/dset/derivatives/$deriv/ ]; then
      mkdir -p $projdir/$dsets/dset/derivatives/$deriv/
  fi

  subs=$(dir $projdir/$dsets/dset/derivatives/dwidenoise-05.21.2019_fmriprep-1.5.0/)

  for sub in $subs; do
      if [[ $sub == sub-* ]]; then
          if [ ! -d $projdir/$dsets/dset/derivatives/$deriv/$sub ]; then
            echo $sub
            while [ $(squeue -u $USER | wc -l) -gt 40 ]; do
                sleep 30m
            done
            sbatch -J $sub-3dtproject-denoise \
              -e $projdir/code/errorfiles/$dset-$sub-denoise \
              -o $projdir/code/outfiles/$dset-$sub-denoise \
              -c 1 \
              --qos pq_nbc \
              -p investor \
              --account iacc_nbc \
              --wrap="python3 $projdir/code/3dTproject_denoise.py -b $proj_dir/dset -w /scratch/$USER/$sub-3dTproject-denoise --sub $sub --deriv $deriv"
          fi
      fi
  done
