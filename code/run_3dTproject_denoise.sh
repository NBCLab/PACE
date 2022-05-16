proj_dir='/users/m/r/mriedel/pace'
dsets=$(dir $proj_dir/dsets/)
dsets='dset-COC100 dset-COH125'

#muschelli et al., 2014
deriv=3dTproject_denoise_acompcor_csfwm+12mo+0.35mm

for dset in $dsets; do
    if [ ! -d $proj_dir/dsets/$dset/derivatives/$deriv/ ]; then
        mkdir -p $proj_dir/dsets/$dset/derivatives/$deriv/
    fi

    subs=$(dir $proj_dir/dsets/$dset/derivatives/dwidenoise-05.21.2019_fmriprep-1.5.0/)

    for sub in $subs; do
        if [[ $sub == sub-* ]]; then

            run_ses=0
            sess=$(dir $proj_dir/dsets/$dset/derivatives/dwidenoise-05.21.2019_fmriprep-1.5.0/$sub/)
            for ses in $sess; do
              if [[ $ses == ses-* ]]; then
                run_ses=1
                break
              fi
            done

            if [ $run_ses -eq 1 ]; then
              for ses in $sess; do
                  if [[ $ses == ses-* ]]; then
                      if [ ! -d $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$ses ]; then
                          echo $sub $ses
                          sbatch -J $dset-$sub-$ses-3dtproject-denoise -e $proj_dir/code/errorfiles/$dset-$sub-$ses-3dtproject-denoise -o $proj_dir/code/outfiles/$dset-$sub-$ses-3dtproject-denoise -c 4 --wrap="python3 $proj_dir/code/3dTproject_denoise.py -b $proj_dir/dsets/$dset -w $proj_dir/scratch/$dset-$sub-$ses-3dTproject-denoise --sub $sub --ses $ses --deriv $deriv"
                      fi
                  fi
              done
            else
              if [ ! -d $proj_dir/dsets/$dset/derivatives/$deriv/$sub ]; then
                  echo $sub
                  sbatch -J $dset-$sub-3dtproject-denoise -e $proj_dir/code/errorfiles/$dset-$sub-3dtproject-denoise -o $proj_dir/code/outfiles/$dset-$sub-3dtproject-denoise -c 4 --wrap="python3 $proj_dir/code/3dTproject_denoise.py -b $proj_dir/dsets/$dset -w $proj_dir/scratch/$dset-$sub-3dTproject-denoise --sub $sub --deriv $deriv"
              fi
            fi
        fi
    done
done
