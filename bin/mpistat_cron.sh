#!/bin/bash

# set up a job pair for each lustre volume
# the first kicks off the mpistat job to generate the data for the volume
# the second bsubs a dependent job that will tidy things up once the data generator is done

# environment required
export PYTHONPATH=/software/openmpi-1.6.4/mpi4py/lib/python2.7/site-packages/:$PYTHONPATH
export MPI_HOME=/software/openmpi-1.6.4
export LD_LIBRARY_PATH=$MPI_HOME/lib:/software/python-2.7.3/lib:$LD_LIBRARY_PATH
export PATH=$MPI_HOME/bin:/software/python-2.7.3/bin:$PATH
export MANPATH=$MPI_HOME/share/man:$MANPATH
export LSB_DEFAULTGROUP=systest-grp
source /usr/local/lsf/conf/profile.lsf

BASE="/lustre/scratch114/teams/hgi/lustre_reports"
WORKERS=64
REGEX="Job <([0-9]+)> is submitted to queue <normal>."


# suppress output
LOG=/dev/null
exec > $LOG 2>&1 

# loop over lustre volumes to process
for VOL in 113 114
do
	# submit the mpistat crawler job
	JOBID=$($BASE/mpistat/bin/mpistat.sh $BASE/mpistat/logs/$VOL.out $BASE/mpistat/logs/$VOL.err $WORKERS /lustre/scratch$VOL $BASE/mpistat/data/$VOL $VOL)
	[[ $JOBID =~ $REGEX ]]
	JOBID="${BASH_REMATCH[1]}"

	# submit dependent job to clean up after running the crawler
	bsub -o $BASE/mpistat/logs -e $BASE/mpistat/logs -G systest-grp -q normal -w "done($JOBID)" $BASE/mpistat/bin/mpistat_tidy.sh $VOL
done

