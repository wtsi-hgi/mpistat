#!/usr/bin/env python
# Example program to crawl filesystem in parallel and print filenames.
# prints the base64 of the path in case the filename contains
# non-printable characters. also prints info from the lstat call :
# path, size, uid, gid, atime, mtime, ctime, type (f,d etc.),
# inode number and number of hard links
from mpi4py import MPI
from ParallelWalk import ParallelWalk
import os
import pwd
import sys
import stat
import time
import base64

class pstat(ParallelWalk):
    """
    Subclassing the ParallelWalk class to override the ProcessFile
    and ProcessDir methods. Need to modify this once we have the
    function signatures updated to pass in the lstat info if it has it.
    It uses the results mechanism to return the total size in the
    results.
    """
    _file_type_dict={
        stat.S_IFSOCK : 's',
        stat.S_IFLNK : 'l',
        stat.S_IFREG : 'f',
        stat.S_IFBLK : 'b',
        stat.S_IFDIR : 'd',
        stat.S_IFCHR : 'c',
        stat.S_IFIFO : 'F'
    }

    def stat_line(self, path, s) :
        """
        print out the stat information into a tab seperated file.
        One file produced for each mpi rank. They all need to be
        catted together once the job is done. For speed, we don't
        try to resolve the uid and gid here, that can be done at
        the parse stage.
        """
        try :
            sz=s.st_size
            self.results += sz
            u=s.st_uid
            g=s.st_gid
            a=s.st_atime
            m=s.st_mtime
            c=s.st_ctime
            i=s.st_ino
            n=s.st_nlink
            t='X' # default t to 'X', override in next section if needed
            if s.st_mode in pstat._file_type_dict :
                t=pstat._file_type_dict[s.st_mode]
            out='%s\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%d\t%d\n' % \
                (base64.b64encode(path),sz,u,g,a,m,c,t,i,n)
            self.output_file.write(out)
        except Exception, err :
            sys.stderr.write('ERROR: %s\n' % str(err))

    def ProcessFile(self, path, s):
        if s is None :
            s=self._lstat(path)
        self.stat_line(path, s)

    def ProcessDir(self, path, s) :
        self.ProcessFile(path, s)

if __name__ == "__main__":
    if len(sys.argv) != 3 :
        print "usage : printfile <start dir> <output dir>"
        sys.exit(1)

    start_dir=sys.argv[1]
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    workers = comm.size

    # create the output file for this rank
    num='%02d' % (rank)
    output_file=open(sys.argv[2]+'/'+num+'.out','w')

    # start the crawler
    crawler = pstat(comm, results=0)

    # assign some instance variables that are used
    # would be better to somehow specify these in a subclassed
    # constructor
    crawler.output_file=output_file
    r=crawler.Execute(start_dir)

    # report results if this is the rank 0 worker
    if rank == 0 :
        print "Total size was %.2f TiB" % ( sum(r) / (1024.0*1024.0*1024.0*1024.0) )
