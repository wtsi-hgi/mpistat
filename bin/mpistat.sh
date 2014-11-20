#!/bin/bash

# run the parallel stat program
# pass in the following arguments :

# 1) where to put stdout
# 2) where to put stderr
# 3) number of processes
# 4) directory to start in
# 5) directory to put output data files in - creates files 0.out, 1.out etc. in this dir, one for each rank
# this avoids issues with concurrent write overlaps

# add some argument checking here rather than let the python deal with it when the job has started...

# bsub the job
bsub -q normal -o $1 -e $2 -R"span[ptile=1] select[mem>4000] rusage[mem=4000]" -M4000 -n$3 mpirun /software/pdu/pstat.py $4 $5

