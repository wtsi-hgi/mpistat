#!/usr/bin/env python
# Example program to crawl filesystem in parallel and print filenames.
# prints the base64 of the path in case the filename contains
# non-printable characters. also prints info from the lstat call :
# path, size, uid, gid, atime, mtime, ctime, type (f,d etc.),
# inode number and number of hard links
from __future__ import print_function
from mpi4py import MPI
from ParallelWalk import ParallelWalk
import os
import sys
import stat
import mpistat_common
import base64
from hgi_rules import hgi_rules


class mpistat(ParallelWalk):
    """
    Subclassing the ParallelWalk class to override the ProcessItems
    method.
    """

    def ProcessItem(self):
        """
        Process an item from the work queue.
        Expects items in the queue to be full path of the inode to
        call lstat on.
        """

        # debug : write size of queue
        # mpistat_common.LOG("node %d : queue size : %d" %
        #                   (self.rank, len(self.items)))

        # pop item from the queue
        path = self.items.pop()

        # lstat it
        try:
            s = self._lstat(path)
        except (IOError, OSError) as e:
            mpistat_common.ERR("Failed to lstat '%s' : %s" %
                               (path, os.strerror(e.errno)))
            return

        # apply hgi rules regarding files in lustre (if applicable)
        # if the rules change the gid then we get that value returned
        # returns -1 if nothing changed
        # so if rules return +ve number then we need to modify the lstat gid
        gid = s.st_gid
        try:
            gid = hgi_rules(path, s)
        except:
            mpistat_common.ERR("Failed to run hgi_rules on '%s' : %s "
                               % (path, sys.exc_info()[0]))

        # if it's a directory, get list of files contained within it
        # and add them to the work queue
        children = list()
        if stat.S_ISDIR(s.st_mode):
            for item in os.listdir(path):
                self.items.append(path + '/' + item)
                try:
                    children.append(item)
                except:
                    mpistat_common.ERR("Failed to add child '%s' to '%s': %s"
                                       % (item, path, sys.exc_info()[0]))
        sz = s.st_size
        self.results += sz
        u = s.st_uid
        g = gid
        a = s.st_atime
        m = s.st_mtime
        c = s.st_ctime
        t = mpistat_common.file_type(s.st_mode)
        i = s.st_ino
        n = s.st_nlink
        d = s.st_dev
        out = '%s\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%d\t%d\t%s\n' %\
              (base64.b64encode(path), sz, u, g, a, m, c, t, i, n, d)
        try:
            self.output_file.write(out)
        except Exception, err:
            mpistat_common.ERR("Failed to write stat line for %s : %s"
                               % (path, str(err)))

    def _lstat(self, path):
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
    if len(sys.argv) < 3:
        mpistat_common.ERR(
            "usage : mpistat <ouptup dir> <dir1> [<dir2> <dir3>...<dirN>]")
        sys.exit(1)

    # get full path for each argument passed in
    # check they are directories which we can open
    # construct seeds list of valid starting points
    seeds = sys.argv[2:]
    mpistat_common.LOG("got seeds %s" % (seeds))

    # get the MPI communicator
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    workers = comm.size

    # start log message
    mpistat_common.LOG("starting mpi worker %d of %d" % (rank, workers))

    # init the crawler
    results = 0
    crawler = mpistat(comm, results)

    # assign some instance variables that are used
    num = '%02d' % (rank)
    output_file = open(sys.argv[1] + '/' + num + '.out', 'w')
    crawler.output_file = output_file

    # start processing loop
    results = crawler.Execute(seeds)

    # report results if this is the rank 0 worker
    if rank == 0:
        mpistat_common.LOG("Total size of files found was %.2f TiB" %
                           (sum(results) / (1024.0*1024.0*1024.0*1024.0)))
