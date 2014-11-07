#!/usr/bin/env python

import re
import sys
import time
import grp
import pwd
import base64

re_line=re.compile(r'^([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)$')

by_group=dict()
by_user=dict()
by_user_group=dict()
file_types=dict()
now=time.time()
unprintable_files=[]
zero_length_files=dict()

def getUser(uid) :
	user=str(uid)
	try :
		user=pwd.getpwuid(uid)[0]
	except :
		pass
	return user

def getGroup(gid) :
	group=str(gid)
	try :
		group=grp.getgrgid(gid)[0]
	except :
		pass
	return group

def getDays(epoch) :
	days=1.0*(now-epoch)/(24*60*60)
	if days < 0 :
		days=0
	return days

def getGiB(sz) :
	return sz/(1024.0*1024.0*1024.0)

# if the filename contains non printable character,
# it will add it to the unprintable files list
# but will truncate it to just before the 1st unprintable character in the file
def check_filename(fname):
	count=0
	printable=True
	dodgy_chars=[]
	for c in fname :
		ascii=ord(c)
		if ascii < 32 or ascii > 126 :
			printable=False
			dodgy_chars.append(ascii)
		if printable :
			count += 1
	if not printable :
		unprintable_files.append((fname[:count],dodgy_chars))

###################################
# the big loop over all the files #
###################################
costs=[]
for l in sys.stdin :
	m=re_line.match(l[:-1])
	if m :

		# check for filenames with dodgy characters
		check_filename(base64.b64decode(m.group(1)))

		uid=int(m.group(3))
		gid=int(m.group(4))
		sz=float(m.group(2))
		epoch=float(m.group(7))
		cost=float(m.group(9))
		if cost > 0 :
			costs.append(cost)
		tp=m.group(8)
		if tp in file_types :
			file_types[tp]+=1
		else :
			file_types[tp]=1
		if sz == 0 :
			if tp in zero_length_files :
				zero_length_files[tp] += 1
			else :
				zero_length_files[tp] = 1
		# by user stuff
		if uid in by_user :
			tmp=by_user[uid]
			tmp['total_cost']+=cost
			tmp['costs'].append(cost)
		else :
			tmp=dict()
			tmp['total_cost'] = cost
			tmp['costs']=[cost]
			by_user[uid]=tmp
		# by_group stuff
		if gid in by_group :
			tmp=by_group[gid]
			tmp['total_cost'] += cost
			tmp['costs'].append(cost)
		else :
			tmp=dict()
			tmp['total_cost'] = cost
			tmp['costs']=[cost]
			by_group[gid]=tmp
		# by_user_group stuff
		user_group=str(uid)+'_'+str(gid)
		if user_group in by_user_group :
			tmp=by_user_group[user_group]
			tmp['total_cost'] += cost
			tmp['costs'].append(cost)
		else :
			tmp=dict()
			tmp['total_cost'] = cost
			tmp['costs']=[cost]
			by_user_group[user_group]=tmp
# get the list of total cost per group
# and sort it then print it
by_group_list=[]
for g in by_group :
	tmp=dict()
	tmp['grp']  = getGroup(g)
	tmp['cost'] = by_group[g]['total_cost']
	tmp['gid']  = g
	by_group_list.append(tmp)
from operator import itemgetter
by_group_list = sorted(by_group_list, key=itemgetter('cost')) 
by_group_list.reverse()
print
print "top 20 costly groups"
for d in by_group_list[:20] :
	print '%20s\t%10.2f' % (d['grp'],d['cost'])

# get the list of total cost per user
# and sort it then print it
by_user_list=[]
for u in by_user :
	tmp=dict()
	tmp['user']  = getUser(u)
	tmp['cost'] = by_user[u]['total_cost']
	tmp['uid']  = u
	by_user_list.append(tmp)
by_user_list = sorted(by_user_list, key=itemgetter('cost')) 
by_user_list.reverse()
print
print "top 20 costly users"
for d in by_user_list[:20] :
	print '%20s\t%10.2f' % (d['user'],d['cost'])

# get the list of total cost per user / group
# and sort it then print it
by_user_group_list=[]
for ug in by_user_group :
	i=ug.find('_')
	u=int(ug[:i])
	g=int(ug[i+1:])
	tmp=dict()
	tmp['user']  = getUser(u)
	tmp['group'] = getGroup(g)
	tmp['cost'] = by_user_group[ug]['total_cost']
	tmp['uid']  = u
	tmp['gid']  = g
	by_user_group_list.append(tmp)
by_user_group_list = sorted(by_user_group_list, key=itemgetter('cost')) 
by_user_group_list.reverse()
print
print "top 40 costly users breakdown by group"
for d in by_user_group_list[:40] :
	print '%20s\t%s\t%10.2f' % (d['user'],d['group'],d['cost'])

# print number of occurences of each file type
print
print "number of inodes of each type"
print file_types

# zero length files
print
print "Number of zero length inodes by type"
print str(zero_length_files)

# unprintable files
print
print "There are "+str(len(unprintable_files))+" unprintable files : "
for f in unprintable_files :
	print f

# sort the files into bins by size
# want 0, 1-1k, 1k-1m, 1m-1g, 1g-1t, 1t+

# histogram of overall costs
plt.hist(costs,histtype='step', bins=100)
plt.savefig('overall_costs.pdf')
plt.show()

# do histograms for the top 5 most costly groups
import matplotlib.pyplot as plt
for i in by_group_list[:5] :
	g=i['grp']
	gid=i['gid']
	plt.hist(by_group[gid]['costs'],histtype='step', bins=100, normed=True, label=g)
plt.legend(loc='upper right')
plt.title('Cost histograms for 5 most costly groups')
plt.xlabel('cost')
plt.ylabel('relative frequency')

# save it as a png
plt.savefig('group_costs.png')
