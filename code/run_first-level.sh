rois='PCC' #'RDLPFC PCC RFI'
proj_dir='/users/m/r/mriedel/pace'
dsets=$(dir $proj_dir/dsets/)
dsets='dset-COC100'

#muschelli et al., 2014
deriv=3dTproject_denoise_acompcor_csfwm+12mo+0.35mm

for roi in $rois; do
  for dset in $dsets; do
      subs=$(dir $proj_dir/dsets/$dset/derivatives/$deriv/)

      for sub in $subs; do
          if [[ $sub == sub-* ]]; then

              while [ $(squeue -u mriedel | wc -l) -gt 20 ]; do
                  sleep 1m
              done

              run_ses=0
              sess=$(dir $proj_dir/dsets/$dset/derivatives/$deriv/$sub/)
              for ses in $sess; do
                if [[ $ses == ses-* ]]; then
                  run_ses=1
                  break
                fi
              done

              if [ $run_ses -eq 1 ]; then
                for ses in $sess; do
                    if [[ $ses == ses-* ]]; then
                      echo $sub $ses

                      mkdir -p $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/
                      runs=$(dir $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$ses/*_space-MNI152NLin2009cAsym_desc-preproc_bold-clean.nii.gz)

                      for run in $runs; do
                          run=${run##*/}
                          run=${run%%.*}

                          if [ ! -e $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.feat/thresh_zstat2.nii.gz ]; then
                            if [ -d $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.feat ]; then
                                rm -r $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.feat
                            fi

                            dx=$(3dinfo -di $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$ses/$run.nii.gz)
                            dx=${dx//-}
                            dy=$(3dinfo -dj $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$ses/$run.nii.gz)
                            dy=${dy//-}
                            dz=$(3dinfo -dk $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$ses/$run.nii.gz)
                            dz=${dz//-}

                            if [ ! -e $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.nii.gz ]; then
                              3dresample -master $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$ses/$run.nii.gz -input $proj_dir/code/rois/mni152nlin2009casym/$roi.nii.gz -prefix $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.nii
                              gzip $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.nii
                            fi
                            
                            fslmeants -i $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$ses/$run -m $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.nii -o $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.txt

                            cp $proj_dir/code/first-level-template.fsf $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.fsf

                            sed -i -e '33s:.*:set fmri(outputdir) "'$proj_dir'/dsets/'$dset'/derivatives/'$roi'/'$sub'/'$ses'/'$run'-'$roi'":' $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.fsf
                            tr=$(3dinfo -tr $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$ses/$run.nii.gz)
                            sed -i -e '36s:.*:set fmri(tr) '$tr':' $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.fsf
                            npts=$(3dinfo -nt $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$ses/$run.nii.gz)
                            sed -i -e '39s:.*:set fmri(npts) '$npts':' $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.fsf
                            sed -i -e '276s:.*:set feat_files(1) "'$proj_dir'/dsets/'$dset'/derivatives/'$deriv'/'$sub'/'$ses'/'$run'":' $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.fsf
                            sed -i -e '314s:.*:set fmri(custom1) "'$proj_dir'/dsets/'$dset'/derivatives/'$roi'/'$sub'/'$ses'/'$run'-'$roi'.txt":' $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.fsf

                            sbatch -J $dset-$sub-$ses-$run-$roi -c 4 -e $proj_dir/code/errorfiles/$dset-$sub-$ses-$run-$roi -o $proj_dir/code/outfiles/$dset-$sub-$ses-$run-$roi -p bigmem --wrap="feat $proj_dir/dsets/$dset/derivatives/$roi/$sub/$ses/$run-$roi.fsf"
                          fi
                      done
                    fi
                done
              else
                echo $sub

                mkdir -p $proj_dir/dsets/$dset/derivatives/$roi/$sub/
                runs=$(dir $proj_dir/dsets/$dset/derivatives/$deriv/$sub/*_space-MNI152NLin2009cAsym_desc-preproc_bold-clean.nii.gz)

                for run in $runs; do
                    run=${run##*/}
                    run=${run%%.*}

                    if [ ! -d $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.feat/thresh_zstat2.nii.gz ]; then
                      if [ -d $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.feat ]; then
                        rm -r $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.feat
                      fi

                      dx=$(3dinfo -di $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$run.nii.gz)
                      dx=${dx//-}
                      dy=$(3dinfo -dj $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$run.nii.gz)
                      dy=${dy//-}
                      dz=$(3dinfo -dk $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$run.nii.gz)
                      dz=${dz//-}

                      if [ ! -e $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.nii.gz ]; then
                        3dresample -master $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$run.nii.gz -input $proj_dir/code/rois/mni152nlin2009casym/$roi.nii.gz -prefix $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.nii
                        gzip $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.nii
                      fi

                      fslmeants -i $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$run -m $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.nii -o $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.txt

                      cp $proj_dir/code/first-level-template.fsf $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.fsf

                      sed -i -e '33s:.*:set fmri(outputdir) "'$proj_dir'/dsets/'$dset'/derivatives/'$roi'/'$sub'/'$run'-'$roi'":' $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.fsf
                      tr=$(3dinfo -tr $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$run.nii.gz)
                      sed -i -e '36s:.*:set fmri(tr) '$tr':' $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.fsf
                      npts=$(3dinfo -nt $proj_dir/dsets/$dset/derivatives/$deriv/$sub/$run.nii.gz)
                      sed -i -e '39s:.*:set fmri(npts) '$npts':' $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.fsf
                      sed -i -e '276s:.*:set feat_files(1) "'$proj_dir'/dsets/'$dset'/derivatives/'$deriv'/'$sub'/'$run'":' $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.fsf
                      sed -i -e '314s:.*:set fmri(custom1) "'$proj_dir'/dsets/'$dset'/derivatives/'$roi'/'$sub'/'$run'-'$roi'.txt":' $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.fsf

                      sbatch -J $dset-$sub-$run-$roi -c 4 -e $proj_dir/code/errorfiles/$dset-$sub-$run-$roi -o $proj_dir/code/outfiles/$dset-$sub-$run-$roi -p bigmem --wrap="feat $proj_dir/dsets/$dset/derivatives/$roi/$sub/$run-$roi.fsf"
                    fi
                done
              fi
          fi
      done
  done
done
