#!/bin/bash

# this is meant to be run after an mpistat data collection run has finished
# it will be a dependent job of the collector job

# get the volume parameter
# and sort out some other useful vars
VOL=$1
BASE=/lustre/scratch114/teams/hgi/lustre_reports/mpistat
DATE=`date +%Y%m%d`

# cat the scratch data files to a gzipped output file with a name based on the
# current date
cat $BASE/data/$VOL/* | gzip > $BASE/data/${DATE}_${VOL}.dat.gz

# TO DO:
# run a report generator against it

# ensure a fifo for the psql copy exists
touch $BASE/psql_pipe
rm $BASE/psql_pipe
mkfifo $BASE/psql_pipe

# and dump the data into the daily postgresql db


