#!/usr/bin/python
import datetime

fopen = open('data/download_sample_txt.txt')

# user download app set 
download = {}

downloadAppSet = set()

lineNum = 0

for line in fopen:

	appId = int(line.split("\t")[0])

	# time format convert
	timeStr = line.split("\t")[1]
	dt = datetime.datetime.strptime(timeStr, "%Y-%m-%d %H:%M:%S")

	userId = line.split("\t")[4][:-2]

	if userId not in download:
		download[userId] = {}
		download[userId][appId] = dt
	else:
		if appId not in download[userId]:
			download[userId][appId]=dt
			continue
		if dt < download[userId][appId]:
			download[userId][appId] = dt

	downloadAppSet.add(appId)

	lineNum += 1

	if lineNum % 10000 == 0:
		print 'download %d lines read' % lineNum

fopen.close()
