import subprocess
import pyperclip
import threading
import flask
import time
import json
import sys
import os
import re
BASE_PATH = os.path.dirname(__file__)

import birthday_reminder
import freetube_handler
import inputsym
import common
import moreos

app = flask.Flask(__name__)

BROWSER_PROCESS_NAME = "chrome"
BROWSER_LAUNCH_COMMAND = ["google-chrome", "--disable-session-crashed-bubble"]

VIDEO_FOLDER = f"{BASE_PATH}/downloads"
if not os.path.exists(VIDEO_FOLDER):
	os.makedirs(VIDEO_FOLDER)
VIDEO_FILE_EXTENSIONS = [".mkv", ".webm", ".flv", ".vob", ".ogg", ".ogv", ".drc", ".mng", ".avi", ".mov", ".qt", ".wmv", ".yuv", ".rm", ".rmvb", ".asf", ".amv", ".mp4", ".m4v", ".mp", ".svi", ".3gp", ".flv", ".f4v"]
VIDEO_PLAYER_PROCESS_NAME = "vlc"
VIDEO_PLAYER_LAUNCH_COMMAND = ["vlc", "--fullscreen", "--sub-autodetect-fuzzy=1"]

YOUTUBE_PLAYER_PROCESS_NAME = "freetube"
YOUTUBE_PLAYER_LAUNCH_COMMAND = [freetube_handler.get_command()]
# YOUTUBE_PLAYER_GO_TO_BAR_SHORTCUT = "ctrl+l"
YOUTUBE_PLAYER_GO_TO_BAR_SHORTCUT = ["ctrl", "l"]
YOUTUBE_PLAYER_OPEN_WAIT_TIME = 2
YOUTUBE_PLAYER_WEBSITE_LOAD_WAIT_TIME = 3

CUSTOM_FILE_PATH = f"{BASE_PATH}/custom_commands.json"

BROWSER_OPEN_WAIT_TIME = 5
BROWSER_WEBSITE_LOAD_WAIT_TIME = 4
BROWSER_GO_TO_BAR_SHORTCUT = "ctrl+l"

INDENT_JSON_RESPONSES='\t'

SHORTCUTS_BY_MODE = {
	"vlc": {
		"pause": "space",
		"forward": "right",
		"rewind": "left",
		"volumeup": "up",
		"volumedown": "down",
		"fullscreen": "f",
		"mute": "m",
		"captions": "v",
		"increasespeed": "]",
		"decreasespeed": "[",
	},
	"youtube": {
		"pause": "space",
		"forward": "right",
		"rewind": "left",
		"volumeup": "up",
		"volumedown": "down",
		"fullscreen": "f",
		"mute": "m",
		"captions": "c",
		"increasespeed": "p",
		"decreasespeed": "o",
	},
	"twitch": {
		"pause": "space",
		"forward": "Right",
		"rewind": "Left",
		"volumeup": "Up",
		"volumedown": "Down",
		"fullscreen": "f",
		"mute": "m",
		"captions": "alt+r",
		"increasespeed": "]",
		"decreasespeed": "[",
	},
	"custom": {
		"pause": "enter",
		"forward": "right",
		"rewind": "left",
		"volumeup": "up",
		"volumedown": "down",
		"mute": "esc",
		"increasespeed": "tab",
	}
}

currentMode = None
processSetBeforeCustom = None

def clear():
	global currentMode
	if currentMode == 'custom':
		for x in moreos.get_process_name_set().difference(processSetBeforeCustom):
			moreos.kill_processes_with_name(x)
	moreos.kill_processes_with_name(VIDEO_PLAYER_PROCESS_NAME)
	moreos.kill_processes_with_name(YOUTUBE_PLAYER_PROCESS_NAME)
	currentMode = None

def download_torrent_thread(magnet):
	os.chdir(VIDEO_FOLDER)
	try:
		# print(f"Calling python3 download_torrent.py {magnet}")
		subprocess.check_call([sys.executable, f"{BASE_PATH}/download_torrent.py", magnet, VIDEO_FOLDER])
		print(f"Torrent download succeeded")
	except:
		print(f"Torrent download failed for torrent {magnet}")
	os.chdir(BASE_PATH)

def open_link_thread(link):
	global currentMode
	birthday_reminder.remind()
	if "youtu" in link:
		currentMode = 'youtube'
		if moreos.is_process_running(YOUTUBE_PLAYER_PROCESS_NAME): # reuse process if possible
			inputsym.keyPress("esc")
			inputsym.keyPress(YOUTUBE_PLAYER_GO_TO_BAR_SHORTCUT)
			time.sleep(0.1)
			inputsym.keyPress(["ctrl", "a"])
			inputsym.keyPress("delete")
			inputsym.keyWrite(link)
			inputsym.keyPress("enter")
			time.sleep(YOUTUBE_PLAYER_WEBSITE_LOAD_WAIT_TIME)
			inputsym.keyPress(SHORTCUTS_BY_MODE['youtube']["fullscreen"])
		else:
			clear()
			currentMode = 'youtube'
			freetube_handler.update_if_needed()
			process = subprocess.Popen(YOUTUBE_PLAYER_LAUNCH_COMMAND + [link])
			time.sleep(YOUTUBE_PLAYER_OPEN_WAIT_TIME + YOUTUBE_PLAYER_WEBSITE_LOAD_WAIT_TIME)
			inputsym.keyPress(SHORTCUTS_BY_MODE['youtube']["fullscreen"])
			# open_link_thread(link)
	elif "twitch" in link:
		clear()
		currentMode = 'vlc'
		subprocess.run([sys.executable,  "-m", "streamlink", "--twitch-low-latency", link, "720p,480p,best", "--player-args", "--fullscreen"])

def open_file_thread(filePath):
	print(f"opening path {filePath}")
	global currentMode
	birthday_reminder.remind()
	clear()
	currentMode = 'vlc'
	print(f"--sub-autodetect-path={os.path.dirname(filePath)}")
	stamp = time.time()
	os.utime(filePath, (stamp, stamp))
	print(VIDEO_PLAYER_LAUNCH_COMMAND + [filePath])
	process = subprocess.Popen(VIDEO_PLAYER_LAUNCH_COMMAND + [common.fixPathOS(filePath)])
# 	process = subprocess.Popen(VIDEO_PLAYER_LAUNCH_COMMAND + [f"--sub-autodetect-path={os.path.dirname(filePath)}", filePath])

def open_spotify_thread():
	global currentMode
	birthday_reminder.remind()
	clear()
	currentMode = 'spotify'
	spotifyEnv = os.environ.copy()
	for k in SPOTIFY_ENVIRONMENT.keys():
		spotifyEnv[k] = SPOTIFY_ENVIRONMENT[k]
	process = subprocess.Popen(SPOTIFY_LAUNCH_COMMAND, env=spotifyEnv)


@app.route('/')
def index():
	return 'tv time', 200

@app.route('/update/')
def update_endpoint():
	print(subprocess.check_output(['git', 'pull', 'origin', 'master']))
	subprocess.Popen([sys.executable, 'tv.py'])
	moreos.kill_process_with_pid(os.getpid())
	return "", 200

@app.route('/download/torrent/')
def download_torrent_endpoint():
	magnet = flask.request.args.get('magnet')
	x = threading.Thread(target=download_torrent_thread, args=(magnet,))
	x.start()
	return "", 200

@app.route('/link/')
def link_endpoint():
	link = flask.request.args.get('url')
	x = threading.Thread(target=open_link_thread, args=(link,))
	x.start()
	return "", 200

@app.route('/file/', methods=['POST'])
def file_endpoint():
	path = flask.request.json["path"] if "path" in flask.request.json.keys() else None
	if path is None:
		path = VIDEO_FOLDER
	if common.fileIsVideoFile(path):
		x = threading.Thread(target=open_file_thread, args=(path,))
		x.start()
		return "", 200
	else:
		output = [('d', x, common.fileDaysSinceLastAccess(x)) for x in common.sortedNicely(common.foldersInFolder(path))]
		output.extend([('f', x, common.fileDaysSinceLastAccess(x)) for x in common.sortedNicely(common.filesInFolder(path)) if common.fileIsVideoFile(x)])
		return json.dumps(output, indent=INDENT_JSON_RESPONSES)


@app.route('/custom/', methods=['GET', 'POST', 'DELETE'])
def custom_endpoint():
	if flask.request.method == 'GET':
		if not os.path.isfile(CUSTOM_FILE_PATH):
			return json.dumps([]), 200
		with open(CUSTOM_FILE_PATH, 'r') as file:
			return json.dumps([x for x in json.loads(file.read())]), 200
	elif flask.request.method == 'POST':
		if "command" not in flask.request.json.keys() or "name" not in flask.request.json.keys():
			return "", 400
		if not os.path.isfile(CUSTOM_FILE_PATH):
			jsonObject = {}
		else:
			with open(CUSTOM_FILE_PATH, 'r') as file:
				jsonObject = json.loads(file.read())
		if flask.request.json["name"] in jsonObject.keys():
			return "", 400
		jsonObject[flask.request.json["name"]] = flask.request.json["command"]
		with open(CUSTOM_FILE_PATH, 'w') as file:
			file.write(json.dumps(jsonObject, indent='\t'))
		return "", 200
	elif flask.request.method == 'DELETE':
		if "name" not in flask.request.json.keys():
			return "", 400
		if not os.path.isfile(CUSTOM_FILE_PATH):
			return "", 400
		with open(CUSTOM_FILE_PATH, 'r') as file:
			jsonObject = json.loads(file.read())
		if flask.request.json["name"] not in jsonObject.keys():
			return "", 400
		del jsonObject[flask.request.json["name"]]
		with open(CUSTOM_FILE_PATH, 'w') as file:
			file.write(json.dumps(jsonObject, indent='\t'))
		return "", 200

@app.route('/customrun/')
def customrun_endpoint():
	birthday_reminder.remind()
	clear()
	global processSetBeforeCustom
	global currentMode
	name = flask.request.args.get('name')
	if not os.path.isfile(CUSTOM_FILE_PATH):
		return "", 400
	with open(CUSTOM_FILE_PATH, 'r') as file:
		jsonObject = json.loads(file.read())
	if name not in jsonObject.keys():
		return "", 400
	processSetBeforeCustom = moreos.get_process_name_set()
	currentMode = 'custom'
	return "", 200

@app.route('/clear/')
def clear_endpoint():
	if currentMode is None:
		return "", 400
	clear()
	return "", 200


@app.route('/pause/')
def pause_endpoint():
	if currentMode is None:
		return "", 400
	inputsym.keyPress(SHORTCUTS_BY_MODE[currentMode]["pause"])
	return "", 200

@app.route('/forward/')
def forward_endpoint():
	if currentMode is None:
		return "", 400
	inputsym.keyPress(SHORTCUTS_BY_MODE[currentMode]["forward"])
	return "", 200

@app.route('/rewind/')
def back_endpoint():
	if currentMode is None:
		return "", 400
	inputsym.keyPress(SHORTCUTS_BY_MODE[currentMode]["rewind"])
	return "", 200

@app.route('/volumeup/')
def volume_up_endpoint():
	if currentMode is None:
		return "", 400
	inputsym.keyPress(SHORTCUTS_BY_MODE[currentMode]["volumeup"])
	return "", 200

@app.route('/volumedown/')
def volume_down_endpoint():
	if currentMode is None:
		return "", 400
	inputsym.keyPress(SHORTCUTS_BY_MODE[currentMode]["volumedown"])
	return "", 200

@app.route('/fullscreen/')
def fullscreen_endpoint():
	if currentMode is None:
		return "", 400
	inputsym.keyPress(SHORTCUTS_BY_MODE[currentMode]["fullscreen"])
	return "", 200

@app.route('/mute/')
def mute_endpoint():
	if currentMode is None:
		return "", 400
	inputsym.keyPress(SHORTCUTS_BY_MODE[currentMode]["mute"])
	return "", 200

@app.route('/captions/')
def captions_endpoint():
	if currentMode is None:
		return "", 400
	inputsym.keyPress(SHORTCUTS_BY_MODE[currentMode]["captions"])
	return "", 200

@app.route('/increasespeed/')
def increasespeed_endpoint():
	if currentMode is None:
		return "", 400
	inputsym.keyPress(SHORTCUTS_BY_MODE[currentMode]["increasespeed"])
	return "", 200

@app.route('/decreasespeed/')
def decreasespeed_endpoint():
	if currentMode is None:
		return "", 400
	inputsym.keyPress(SHORTCUTS_BY_MODE[currentMode]["decreasespeed"])
	return "", 200

app.run(host='0.0.0.0', port=8081)
