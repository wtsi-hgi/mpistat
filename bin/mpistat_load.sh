#!/bin/bash
export LD_LIBRARY_PATH=/software/python-2.7.8/lib:$LD_LIBRARY_PATH
export PATH=/software/python-2.7.8/bin:$PATH
python /lustre/scratch114/teams/hgi/lustre_reports/mpistat/bin/mpistat_load.py
