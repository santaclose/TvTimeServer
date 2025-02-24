import os
import re
import time

VIDEO_FILE_EXTENSIONS = [".mkv", ".webm", ".flv", ".vob", ".ogg", ".ogv", ".drc", ".mng", ".avi", ".mov", ".qt", ".wmv", ".yuv", ".rm", ".rmvb", ".asf", ".amv", ".mp4", ".m4v", ".mp", ".svi", ".3gp", ".flv", ".f4v"]
SUBTITLE_FILE_EXTENSIONS = [".srt"]

def fileIsVideoFile(filePath):
	return any([filePath.endswith(x) for x in VIDEO_FILE_EXTENSIONS])
def fileIsSubtitleFile(filePath):
	return any([filePath.endswith(x) for x in SUBTITLE_FILE_EXTENSIONS])
def fileDaysSinceLastAccess(filePath):
	return (time.time() - os.stat(filePath).st_atime) / 3600 / 24
def fixPathOS(path):
	if os.name == 'nt':
		return path.replace('/', '\\')
	return path

def filesInFolderRec(folder):
	return [os.path.join(dp, f).replace('\\', '/') for dp, dn, filenames in os.walk(folder) for f in filenames]
def filesInFolder(folder):
	return [os.path.join(folder, f).replace('\\', '/') for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
def foldersInFolder(folder):
	return [os.path.join(folder, f).replace('\\', '/') for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
def sortedNicely(l):
	convert = lambda text: int(text) if text.isdigit() else text
	alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
	return sorted(l, key = alphanum_key)
