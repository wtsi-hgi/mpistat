mpistat
=======

Parallel file tree walker. This is file-system agnostic.
I have copied the bin/ParallelWalk.py module from guycoates's wtsi-ssg/pcp parallel walker library as opposed to linking to the repo. This is because his repo is in flux at the moment and I made some changes to try to eliminate the possibility of doing more than 1 lstat per inode. Once the pcp repo has all the latest changes and has been modified to use the parallel walk module, I can remove this and go back to using it from Guy's repo.
