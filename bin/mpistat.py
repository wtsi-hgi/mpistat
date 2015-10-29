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
import riak
import mpistat_config
import mpistat_common
from hgi_rules import hgi_rules
import time

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
            mpistat_common.ERR("Failed to lstat '%s' : %s" % (path, os.strerror(e.errno)))
            return

        # apply hgi rules regarding files in lustre (if applicable)
        # if the rules change the gid then we get that value returned
        # returns -1 if nothing changed
        # so if rules return +ve number then we need to modify the lstat gid
        try :
            gid=hgi_rules(path, s)
        except :
            mpistat_common.ERR("Failed to run hgi_rules on '%s' : %s " % (path, sys.exc_info()[0]))

        # if it's a directory, get list of files contained within it
        # and add them to the work queue
	children=list()
        if stat.S_ISDIR(s.st_mode) :
            for item in os.listdir(path) :
                self.items.append(path+'/'+item)
		try :
                    children.append(unicode(item, 'utf-8'))
                except :
                    mpistat_common.ERR("Failed to add child '%s' : %s " % (item, sys.exc_info()[0]))

        # register the information in riak
        # may look at adding in the aggregation up the tree here also
        # but that will involve needing locks on the aggregate variables
        # to avoid data races. locks can easily be handled in riak with
        # a strongly consisten bucket. Can also look at doing the aggregation
        # at the end with some kind of map reduce function instead
	# seem to get riak timeouts occasionally so try a fw times before giving up
	try :
            obj={
                'path'     : unicode(path, 'utf-8'),
                'size'     : s.st_size,
                'uid'      : s.st_uid,
                'gid'      : gid,
                'type'     : mpistat_common.file_type(s.st_mode),
                'atime'    : s.st_atime,
                'mtime'    : s.st_mtime,
                'ctime'    : s.st_ctime,
                'children' : children
            }
            riakClient=mpistat_common.get_riak_client()
            bucket=riakClient.bucket('inodes')
            newInode=bucket.new(obj['path'], data=obj)
            newInode.store()
        except :
            mpistat_common.ERR("Failed to store riak object '%s' : %s " % (path, sys.exc_info()[0]))

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
        mpistat_common.ERR("usage : mpistat <dir1> [<dir2> <dir3>...<dirN>]")
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
    mpistat_common.LOG("starting mpi worker %d of %d" %(rank,workers))

    # init the crawler
    results = 0
    crawler = mpistat(comm, results)

    # start processing loop
    r=crawler.Execute(seeds)

    # report results if this is the rank 0 worker
    if rank == 0 :
        mpistat_common.LOG("Total size of files found was %.2f TiB" % ( sum(r) / (1024.0*1024.0*1024.0*1024.0) ))
