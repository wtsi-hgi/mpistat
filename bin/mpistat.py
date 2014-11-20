#!/usr/bin/env python
# Example program to crawl filesystem in parallel and print filenames.
# prints the base64 of the path in case the filename contains non-printable characters
# also prints info from the lstat call : path, size, uid, gid, atime, mtime, ctime, type (f,d etc.) and a cost
# cost is dependent on the amount of time a file has not been accessed for and it's size
# ordering by cost suggests files we should try to clean up
from mpi4py import MPI
from lib.parallelwalk  import ParallelWalk

import os
import pwd
import grp
import sys
import stat
import time
import base64
cost_tb_year=150.00
now=int(time.time())

def cost(sz,now,camtime) :
    """
        Calculate a cost for a file based on the passed in time on the inode [cam]time value and the size
    """
    # size in TiB	(magic numner is bytes in a TiB)
    tib=1.0*sz/107374182
    # years since the last [cam]time (magic number is seconds in a (non-leap) year )
    yrs=1.0*(now-camtime)/31536000
    return tb*yrs*cost_tb_year

def safelstat(path):
    """
        lstat can sometimes by interrupted and return EINTR so wrap the call in a try block
    """
    while True:
        try:
            return os.lstat(path)
        except IOError, error:
            if error.errno != 4:
                raise

def file_type(mode) :
    """
        Turn the stat mode into it's standard representational character
        need to replace this with a constant dictionary within the class once
        we have things fully set up in github
    """
    if stat.S_ISREG(mode) :
        return 'f'
    elif stat.S_ISDIR(mode) :
        return 'd'
    elif stat.S_ISLNK(mode) :
        return 'l'
    elif stat.S_ISSOCK(mode) :
        return 's'
    elif stat.S_ISBLK(mode) :
        return 'b'
    elif stat.S_ISCHR(mode) :
        return 'c'
    elif stat.S_ISFIFO(mode) :
        return 'F'
    else :
        return 'X'

class pstat(ParallelWalk):
    """
        Subclassing the ParallelWalk class to override the ProcessFile and ProcessDir methods.
        Need to modify this once we have the function signatures updated to pass in the lstat info
        if it has it.
        It uses the results mechanism to return the total size in the results. Need to make results a
        tuple and return the total cost (based on ctime) and the total waste (based on atime) as well
    """

    def stat_line(self, path) :
        """
            print out the stat information into a tab seperated file. one file produced for each mpi rank.
            they all need to be catted together once the job is done. For speed, we don't try to resolve the
            uid and gid here, that can be done at the parse stage.
        """
        try :
            s=safestat(path)
            sz=s.st_size
            self.results += sz
            u=s.st_uid
            g=s.st_gid
            a=s.st_atime
            m=s.st_mtime
            c=s.st_ctime
            t=file_type(s.st_mode)
            out='%s\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%.9f\n' % (base64.b64encode(path),sz,u,g,a,m,c,t,cost(sz,a))
            output_file.write(out)
        except :
            pass

    def ProcessFile(self, path):
        self.stat_line(path)

    def ProcessDir(self, path) :
        self.stat_line(path)

# need to add the 'main' idiom here

if __name__ == "__main__":
    if len(sys.argv) != 3 :
        print "usage : printfile <start dir> <output dir>"
        sys.exit(1)

    start_dir=sys.argv[1]
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    workers = comm.size

    # create the output file for this rank
    # and set the cost per terabyte per year
    num='%02d' % (rank)
    output_file=open(sys.argv[2]+'/'+num+'.out','w')

    # start the crawler
    crawler = pstat(comm, results=0)
    crawler.output_file=output_file
    crawler.cost_tb_year=150.00
    r=crawler.Execute(start_dir)

    # report results if this is the rank 0 worker
    if rank == 0 :
        print "Total size was %.2f TiB" % ( sum(r) / (1024.0*1024.0*1024.0*1024.0) )
