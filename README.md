mpistat
=======
Efficiently walk a tree in parallel across many nodes using MPI. Based on http://conferences.computer.org/sc/2012/papers/1000a015.pdf. Also see http://jlafon.io/parallel-file-treewalk.html.

There is a C version using libcircle (https://github.com/hpc/libcircle) which is the C implementation used by the authors of the original article.

The python version uses Guy Coates's interpretation (https://github.com/wtsi-ssg/pwalk) of the algorithm discussed in the paper.

There is no significant difference in the time taken by the C and python versions due to the time being dominated by the lstat syscall.
