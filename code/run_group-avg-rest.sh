proj_dir='/users/m/r/mriedel/pace'
dsets=$(dir $proj_dir/dsets/)
deriv='PCC'
dsets='dset-COC100'

for dset in $dsets; do
  sbatch -J group-avg-rest-$deriv -c 12 -e $proj_dir/code/errorfiles/group-avg-rest-$deriv -o $proj_dir/code/outfiles/group-avg-rest-$deriv -p bigmem --wrap="python3 $proj_dir/code/group-avg-rest.py -b $proj_dir --dset $dset --derivative $deriv"
done
