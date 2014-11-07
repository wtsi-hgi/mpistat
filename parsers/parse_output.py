#!/usr/bin/env python

import base64
import re
import sys
import pwd
import grp
import time
"""
    Parse the raw output from the mpistat program and print a summary of the info for each entry
"""
re_line=re.compile(r'^([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)$')

def getGiB(sz) :
	return '%.2fGB' % (sz/(1073741824)

def printDate(epoch) :
	return time.strftime('%Y-%m-%d', time.localtime(epoch))
#	return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch))

for l in sys.stdin :
	m=re_line.match(l[:-1])
	if m :
		uid=int(m.group(3))
		gid=int(m.group(4))
		sz=float(m.group(2))
		atime=int(m.group(7))
		cost=float(m.group(9))
		print base64.b64decode(m.group(1)), pwd.getpwuid(uid)[0], grp.getgrgid(gid)[0], getGiB(sz), '%.2f' % (cost), printDate(atime)
	
