#!/usr/bin/python

fopen = open('data/app_tag.txt')

tagAppSet = set()
tagDic = {}

lineNum = 0

for line in fopen:

	appId = int(line.split("\t")[0])
	tagId = int(line.split("\t")[1][:-1])

	tagAppSet.add(appId)

	if not (tagId == 0):
		tagDic.setdefault(appId, set())
		tagDic[appId].add(tagId)

	lineNum += 1
	if lineNum % 10000 == 0:
		print ' tag %d lines read' % lineNum

fopen.close()
