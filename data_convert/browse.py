#!/usr/bin/python
import datetime

fopen = open('data/browse_sample_txt.txt')

# user download app set
browse = {}

browseAppSet = set()

lineNum = 0

for line in fopen:

	appId = int(line.split("\t")[0])

	# time format convert
	timeStr = line.split("\t")[1]
	dt = datetime.datetime.strptime(timeStr, "%Y-%m-%d %H:%M:%S")

	userId = line.split("\t")[3][:-2]

	lineNum += 1

	if userId not in browse:
		browse[userId] = {}
		browse[userId][appId] = dt
	else:
		if appId not in browse[userId]:
			browse[userId][appId] = dt
			continue
		if dt < browse[userId][appId]:
			browse[userId][appId] = dt

	browseAppSet.add(appId)

	if lineNum % 10000 == 0:
		print '\r browse %d lines read' % lineNum

fopen.close()
