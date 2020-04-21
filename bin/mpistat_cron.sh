#!/bin/bash

# set up a job pair for each lustre volume
# the first kicks off the mpistat job to generate the data for the volume
# the second bsubs a dependent job that will tidy things up once the data generator is done

# environment required
source /usr/local/lsf/conf/profile.lsf
source /lustre/scratch114/teams/hgi/lustre_reports/mpistat/venv-farm5/bin/activate
export MPI_HOME=/software/hgi/pkglocal/openmpi-1.8.8-lsf-9.1.3
export GCC_HOME=/software/hgi/pkglocal/gcc-4.9.1
export LD_LIBRARY_PATH=$GCC_HOME/lib64:$GCC_HOME/lib:$MPI_HOME/lib:$LD_LIBRARY_PATH
export PATH=$MPI_HOME/bin:$GCC_HOME/bin:$PATH
export LSB_DEFAULTGROUP=systest-grp

BASE="/lustre/scratch114/teams/hgi/lustre_reports"
WORKERS=16
REGEX="Job <([0-9]+)> is submitted to queue <normal>."


# suppress output
LOG=/dev/null
exec > $LOG 2>&1 

# keep track of all jobs kicked off
JOBIDS=()

# loop over lustre volumes to process
for VOL in 114 ## TESTING 115 116 117 118 119
do
	# submit the mpistat crawler job
	JOBID1=$($BASE/mpistat/bin/mpistat_submit.sh $BASE/mpistat/logs/%J_$VOL.out $BASE/mpistat/logs/%J_$VOL.err $WORKERS $BASE/mpistat/data/$VOL /lustre/scratch$VOL)
	[[ $JOBID1 =~ $REGEX ]]
	JOBID1="${BASH_REMATCH[1]}"
	JOBIDS+=($JOBID1)
	# submit dependent job to clean up after running the crawler
	JOBID2=$(bsub -o $BASE/mpistat/logs/tidy_%J_$VOL.out -e $BASE/mpistat/logs/tidy_%J_$VOL.err -G systest-grp -q normal -w "done($JOBID1)" $BASE/mpistat/bin/mpistat_tidy.sh $VOL)
	[[ $JOBID2 =~ $REGEX ]]
	JOBID2="${BASH_REMATCH[1]}"
	JOBIDS+=($JOBID2)
done
