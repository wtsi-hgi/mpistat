#!/bin/bash

# run the parallel stat program
# pass in the following arguments :

# 1) where to put stdout
# 2) where to put stderr
# 3) number of processes
# 4) directory to start in
# 5) directory to put output data files in - creates files 0.out, 1.out etc. in this dir, one for each rank
#    this avoids issues with concurrent write overlaps
# 6) a prefix to print on each line. used to put the lustre volume # on the line so that the output can be COPY'd straight into postgresql
# add some argument checking here rather than let the python deal with it when the job has started...

# cd to the script directory
cd "$( dirname "${BASH_SOURCE[0]}" )"

# bsub the job
bsub -q normal -G systest-grp -o $1 -e $2 -R"span[ptile=1] select[mem>4000] rusage[mem=4000]" -M4000 -n$3 mpirun ./mpistat.py $4 $5 $6

