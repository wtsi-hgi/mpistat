#!/bin/bash

set -euf -o pipefail 

# this is meant to be run after an mpistat data collection run has finished
# it will be a dependent job of the collector job

# get the volume parameter
# and sort out some other useful vars
VOL=$1
BASE=/lustre/scratch114/teams/hgi/lustre_reports/mpistat
DATE=`date +%Y%m%d`

# cat the scratch data files to a gzipped output file with a name based on the
# current date
DATA_FILE=$BASE/data/${DATE}_${VOL}.dat
if [[ -e ${DATA_FILE}.gz ]]
then
    echo "Data file ${DATA_FILE} already exists, refusing to clobber."
else
    set +f
    shopt -s failglob
    cat $BASE/data/$VOL/*.out > ${DATA_FILE}
    gzip ${DATA_FILE}
    rm $BASE/data/$VOL/*.out
fi

# TO DO:
# run a report generator against it

