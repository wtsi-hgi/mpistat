#!/bin/bash

# submit parallel stat collector program
# pass in the following arguments :

# 1) where to put stdout
# 2) where to put stderr
# 3) number of processes
# 4) directory to put output data files in - creates files 0.out, 1.out etc. in this dir, one for each rank
#    this avoids issues with concurrent write overlaps
# 5+) directory to start in
#
# should add some argument checking here rather than let the python deal with it when the job has started...
MPISTAT_HOME=/lustre/scratch114/teams/hgi/lustre_reports/mpistat
# cd to the script directory
cd "$( dirname "${BASH_SOURCE[0]}" )"
# bsub the job
bsub -q normal -G systest-grp -o $1 -e $2 -R"span[ptile=1] select[mem>4000] rusage[mem=4000]" -M4000 -n$3 $MPISTAT_HOME/bin/mpistat_wrapper.sh $4 ${@:5}

