# environment required
source /usr/local/lsf/conf/profile.lsf
source /lustre/scratch114/teams/hgi/lustre_reports/mpistat/venv-farm5/bin/activate
export MPI_HOME=/software/hgi/pkglocal/openmpi-1.8.8-lsf-9.1.3
export GCC_HOME=/software/hgi/pkglocal/gcc-4.9.1
export LD_LIBRARY_PATH=$GCC_HOME/lib64:$GCC_HOME/lib:$MPI_HOME/lib:$LD_LIBRARY_PATH
export PATH=$MPI_HOME/bin:$GCC_HOME/bin:$PATH

mpirun --allow-run-as-root python /lustre/scratch114/teams/hgi/lustre_reports/mpistat/bin/mpistat.py $@

