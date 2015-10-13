export LD_LIBRARY_PATH=/lustre/scratch114/teams/hgi/mpistat_dev/venv/lib:/software/hgi/pkglocal/openmpi-1.10.0-lsf-9.1.1.1/lib:/software/hgi/pkglocal/gcc-4.9.1/lib:/usr/local/lsf/9.1/linux2.6-glibc2.3-x86_64/lib:/software/hgi/pkglocal/mpi4py-git-1.3.1-714-g4398970-openmpi-1.10.0-lsf-9.1.1.1-python-2.7.10-ucs4/lib/python2.7/site-packages:/software/hgi/pkglocal/openssl-1.0.1j/lib

export PYTHONPATH=/software/hgi/pkglocal/mpi4py-git-1.3.1-714-g4398970-openmpi-1.10.0-lsf-9.1.1.1-python-2.7.10-ucs4/lib/python2.7/site-packages

cd /lustre/scratch114/teams/hgi/mpistat_dev/bin

/software/hgi/pkglocal/openmpi-1.10.0-lsf-9.1.1.1/bin/mpirun --wait-for-server --server-wait-time 30 --mca oob_tcp_listen_mode listen_thread --allow-run-as-root /lustre/scratch114/teams/hgi/mpistat_dev/venv/bin/python  /lustre/scratch114/teams/hgi/mpistat_dev/bin/mpistat.py $@ 
