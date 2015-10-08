#!/bin/bash

export LD_LIBRARY_PATH=/software/hgi/pkglocal/libcircle/lib:/software/hgi/pkglocal/mpich-3.1.4-lsf-9.1/lib:/software/hgi/pkglocal/gcc-4.9.1/lib64:/software/hgi/pkglocal/gcc-4.9.1/lib:

mpirun $HOME/git/mpistat/bin/mpistat $HOME $HOME/logs

