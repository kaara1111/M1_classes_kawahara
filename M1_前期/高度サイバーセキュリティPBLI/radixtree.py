# -*- coding: utf-8 -*-
"""
Created on Mon May 29 17:19:30 2023

@author: owner
"""

import radix

rtree = radix.Radix()

f = open("iplist.txt","r")
g = open("search.txt","r")

org = []
print("Making Tree..")
for line in f:
	line = line.replace("\r\n","")
	cols = line.split(':')
	rtree.add(cols[1])
	org.append([cols[0],cols[1]])
print("Tree Completed.\n--------------------")

print("Now Matching..")
for line in g:
	line = line.replace("\r\n","")
	rnode = rtree.search_best(line)
	if(str(rnode) != "None"):
		for row in org:
			if(row[1] == rnode.prefix):
				print(line + "\t:" + row[1] + "\t:" + row[0])
print("Finished.")

f.close()
g.close()