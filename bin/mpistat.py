#!/usr/bin/env python
# Example program to crawl filesystem in parallel and print filenames.
# prints the base64 of the path in case the filename contains
# non-printable characters. also prints info from the lstat call :
# path, size, uid, gid, atime, mtime, ctime, type (f,d etc.),
# inode number and number of hard links
from __future__ import print_function
from mpi4py import MPI
from ParallelWalk import ParallelWalk
from Inodes import Inode
import os
import pwd
import sys
import stat
import time
import datetime
import errno
import riak
import mpistat_config

def ERR(*objs):
    timestamp=datetime.datetime.fromtimestamp(
        time.time()).strftime('[%Y-%m-%d %H:%M:%S]')
    print(timestamp, *objs, file=sys.stderr)
    sys.stderr.flush()

def LOG(*objs):
    timestamp=datetime.datetime.fromtimestamp(
        time.time()).strftime('[%Y-%m-%d %H:%M:%S]')
    print(timestamp, *objs)
    sys.stdout.flush()
    
class mpistat(ParallelWalk):
    """
    Subclassing the ParallelWalk class to override the ProcessItems
    method.
    """
    
    def ProcessItem(self):
        """
        Process an item from the work queue.
        Expects items in the queue to be full path of the inode to call lstat on.
        """ 
    
        # pop item from the queue
        path = self.items.pop()

        # lstat it
        try :
            s=self._lstat(path)
        except (IOError, OSError) as e :
            ERR("Failed to lstat '%s' : %s" % (path, os.strerror(e.errno)))
            return
            
        # if it's a directory, get list of files contained within it
        # and add them to the work queue
        type = self._file_type(s.st_mode)
	children=None
        if type == 'd' :	
            children=os.listdir(path)
            for child in children :
                self.items.append(path+'/'+child)

        # register the information in riak
        # may look at adding in the aggregation up the tree here also
        # but that will involve needing locks on the aggregate variables
        # to avoid data races. locks can easily be handled in riak with
        # a strongly consisten bucket. Can also look at doing the aggregation
        # at the end with some kind of map reduce function instead
        Inode(
            client   = self.riak_client,
            path     = path,
            size     = str(s.st_size),
            uid      = str(s.st_uid),
            gid      = str(s.st_gid),
            type     = type,
            atime    = str(s.st_atime),
            mtime    = str(s.st_mtime),
            ctime    = str(s.st_ctime),
            children = children
        )

    def _file_type(self,mode) :
        """
        Turn the stat mode into it's standard representational character
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
        
    def _lstat(self,path):
        """
        lstat can sometimes by interrupted and return EINTR
        so wrap the call in a try block
        """
        while True:
            try:
                return os.lstat(path)
            except IOError, error:
                if error.errno != 4:
                    raise

if __name__ == "__main__":

    # check we have enough arguments
    if len(sys.argv) < 2 :
        ERR("usage : mpistat <dir1> [<dir2> <dir3>...<dirN>]")
        sys.exit(1)

    # get full path for each argument passed in
    # check they are directories which we can open
    # construct seeds list of valid starting points
    seeds=sys.argv[1:]
 
    # get the MPI communicator 
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    workers = comm.size

    # start log message
    LOG("starting mpi worker %d of %d" %(rank,workers))

    # init the crawler
    results = 0
    crawler = mpistat(comm, results)
    
    # get a riak client
    crawler.riak_client = riak.RiakClient(nodes=mpistat_config.riak_nodes)

    # start processing loop
    r=crawler.Execute(seeds)

    # report results if this is the rank 0 worker
    if rank == 0 :
        LOG("Total size of files found was %.2f TiB" % ( sum(r) / (1024.0*1024.0*1024.0*1024.0) ))
