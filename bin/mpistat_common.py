#!/usr/bin/env python
from __future__ import print_function
import sys
import time
import datetime
import errno
import stat

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

def file_type(mode) :
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

