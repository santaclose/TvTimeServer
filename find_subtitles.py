import os
import sys
import common
import shutil

srtFiles = [x for x in common.filesInFolderRec(".") if common.fileIsSubtitleFile(x)]
videoFiles = [x for x in common.filesInFolderRec(".") if common.fileIsVideoFile(x)]

if len(srtFiles) != len(videoFiles):
	print("Number of srt files doesn't match number of video files")
	sys.exit(1)

srtFileNames = {os.path.basename(x): x for x in srtFiles}
videoFileNames = {os.path.basename(x): x for x in videoFiles}

srtsSorted = common.sortedNicely(srtFileNames.keys())
videosSorted = common.sortedNicely(videoFileNames.keys())

for i in range(len(srtsSorted)):
# 	print(f"{videosSorted[i]} - {srtsSorted[i]}")
# 	print(f"{videoFileNames[videosSorted[i]]} - {srtFileNames[srtsSorted[i]]}")
	targetVideoFilePath = videoFileNames[videosSorted[i]]
	targetSrtFilePath = srtFileNames[srtsSorted[i]]

	newFilePath = os.path.splitext(targetVideoFilePath)[0] + os.path.splitext(targetSrtFilePath)[1]
	print(f"moving {targetSrtFilePath} to {newFilePath}")
	shutil.move(targetSrtFilePath, newFilePath)