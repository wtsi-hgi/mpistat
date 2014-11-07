#!/usr/bin/env python

import base64
import sys
import re

def b64_to_printable(fname) :
	"""
		take a b64 encoded filename and return a cleaned version
		with all unprintable characters replaced by '?'
	"""
	return base64.b64decode(fname).decode('utf8').encode('ascii','replace')

def tidy_path(ignore,path) :
	"""
		remove 'ignore' from the start of path
	"""
	return path[len(ignore):]

class tree_node :
	"""
		represent a file systerm tree node
		each node has a cost accumulator and a dictionary of children
	"""

	def out(self) :
		"""
			walk the tree with a depth first search
		"""
		print self.name, str(self.cost_accumulator)
		for child in self.children :
			self.children[child].out()

	def __init__(self,name,cost):
		"""
			create a new tree_node, only done with directories
		"""
		self.name=name
		self.children = dict()
		self.cost_accumulator=cost

	def add_cost(self,cost) :
		"""
			add the cost to the cost accumulator
		"""
		self.cost_accumulator += cost
	
	def has_child(self,name) :
		"""
			check if the node already has a particular named child
			use to make sure we don't create a child that already exists
		"""
		if name in self.children :
			return True
		else :
			return False

	def get_child(self,name) :
		"""
			return the child tree_node object with the given name
		"""
		return self.children[name]

	def add_child(self,name,child) :
		self.children[name]=child
	

if __name__ == "__main__":

	# sort out command line args
	if len(sys.argv) != 2 :
		print """
			usage : build_tree.py <ignore string>
				<ignore string> : part of the path that we want to ignore when building the tree
				e.g. //lustre/ if we want to the root to be sscratch113
		"""
		sys.exit(1)
	ignore=sys.argv[1]
	
	#create root node
	root=tree_node(ignore,0)

	# read in the raw file
	# for each entry...
	# convert the b64 to a real string and get the cost associated with the file /directory / link
	# explode it to a list using '/' as seperator

	# regular expression to match a line from the raw file
	# we just want to pick out the base64 and the cost for now
	# base64 is the first field, cost is the last field
	re_line=re.compile(r'^([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)$')
	for line in sys.stdin :
		m=re_line.match(line)
		if m :
			# get the cost for this node
			cost=float(m.group(9))
			if cost < 0 :
				cost = 0.0

			# get the inode type
			inode_type=m.group(8)
			
			# get the full path and then explode it to a list of directories
			# with the last entry being the filename / link or last dir in the chain
			fname=tidy_path(ignore,b64_to_printable(m.group(1))).lstrip('/')
			path_list=fname.split('/')
			# loop over the directories in this entries path
			# accumulating the cost at each level
			current=root
			root.add_cost(cost)
			for i,directory in enumerate(path_list[:-1]) :
				if current.has_child(directory) :
					current.add_cost(cost)
					current=current.get_child(directory)
				else :
					name=ignore+'/'.join(path_list[:i+1])
					tmp=tree_node(name,cost)
					current.add_child(directory,tmp)
					current=tmp
					
			# at this point we have processed all but the last entry
			# if the entry is a directory we need to create a new node
			# otherwise we just add the cost to current
			if inode_type ==  'd' :
				tmp=tree_node(ignore+'/'.join(path_list),cost)
				current.add_child(path_list[-1],tmp)
			else :
				current.add_cost(cost)

	root.out()
#	print b64_to_printable("L2x1c3RyZS9zY3JhdGNoMTEzL3RlYW1zL2JhcnJldHQvb3B0aWNhbGxfdGd6X3Rlc3QvaWJkX3JlbDVfb3B0aWNhbGwudGFy")
#	print b64_to_printable("L2x1c3RyZS9zY3JhdGNoMTEzL3Byb2plY3RzL2ludGVyX3ByZWdfZ2VuL3VzZXJzL253MTQvbWV0YS9yYXcvTk9SV0FZX1RSw5hOREVMQUdfSFVOVC50eHQuZ3o=")

