from browse import *
from download import *
from tag import *

download_new = open('save/download_new.txt', 'w')
browse_new = open('save/browse_new.txt', 'w')
tag_new = open('save/tag_new.txt', 'w')

newAppId = 0
newUserId = 0
newTagId = 0

downloadAppSum = 0
downloadUserSum = 0

browseAppSum = 0
browseUserSum = 0

appSet = downloadAppSet.union(browseAppSet).intersection(tagAppSet)

finalUserDic = {}
finalAppDic = {}
finalTagDic = {}

for userId, userDic in download.items():

	intersection = appSet.intersection(download[userId].keys())

	if (len(intersection) >= 20) and (len(intersection) <= 100):

		if userId not in finalUserDic:
			finalUserDic[userId] = newUserId
			newUserId += 1
			downloadUserSum += 1

		for appId, time in userDic.items():
			if appId in appSet:
				if appId not in finalAppDic:
					# new App Id
					finalAppDic[appId] = newAppId
					newAppId += 1
					downloadAppSum += 1
				download_new.write('%s\t%d\t%d\n' % (time, finalUserDic[userId], finalAppDic[appId]))

download_new.close()

for userId, userDic in browse.items():
	if userId in finalUserDic.keys():
		for appId, time in userDic.items():
			if appId in appSet:
				if appId not in finalAppDic:
					# new App Id
					finalAppDic[appId] = newAppId
					newAppId += 1
					browseAppSum += 1
				browse_new.write('%s\t%d\t%d\n' % (time, finalUserDic[userId], finalAppDic[appId]))

browse_new.close()

i = 0

for appId, tagSet in tagDic.items():
	if appId in finalAppDic.keys():
		for tagId in tagSet:
			if tagId not in finalTagDic:
				finalTagDic[tagId] = newTagId
				newTagId += 1
			tag_new.write('%d\t%d\n' % (finalAppDic[appId], finalTagDic[tagId]))
	i += 1
	if i % 10000 == 0:
		print 'total %d apps %d finished' % (len(tagDic.keys()), i)

tag_new.close()

statistic = open('save/statistic.txt', 'w')

statistic.write('total: %d users, %d apps\n' % (newUserId, newAppId))
statistic.write('download_txt: %d users, %d apps\n' % (downloadUserSum, downloadAppSum))
statistic.write('tags: %d tags' % newTagId)

statistic.close()
