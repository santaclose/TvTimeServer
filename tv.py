import common
import moreos

import youtube_firefox
import twitch_vlc
import file_vlc
import custom

import subprocess
import threading
import json
import sys
import os

import flask

BASE_PATH = os.path.dirname(__file__)
VIDEO_FOLDER = f"{BASE_PATH}/downloads"
os.makedirs(VIDEO_FOLDER, exist_ok=True)
CUSTOM_FILE_PATH = f"{BASE_PATH}/custom_commands.json"
INDENT_JSON_RESPONSES='\t'

currentMode = None

app = flask.Flask(__name__)


@app.route('/')
def index():
	return 'tv time', 200


@app.route('/update/')
def update_endpoint():
	try:
		command = ['git', 'pull', 'origin', 'master']
		print(f"running: {' '.join(command)}")
		print(subprocess.check_output(command).decode('utf-8'))
	except Exception as error:
		print("git pull command failed")
	try:
		command = ["uv", "pip", "install", "-r", "requirements.txt", "--python", "3.11.1"]
		print(f"running: {' '.join(command)}")
		print(subprocess.check_output(command).decode('utf-8'))
	except Exception as error:
		print("pip install command failed")
	subprocess.Popen(["bash", "run.bash"])
	moreos.kill_process_with_pid(os.getpid())
	return "", 200


@app.route('/switch_display')
def switch_display():
	moreos.switch_display()
	return "", 200


def download_torrent_thread(magnet):
	os.chdir(VIDEO_FOLDER)
	try:
		# print(f"Calling python3 download_torrent.py {magnet}")
		subprocess.check_call([sys.executable, f"{BASE_PATH}/download_torrent.py", magnet, VIDEO_FOLDER])
		print(f"Torrent download succeeded")
	except Exception as e:
		print(f"Torrent download failed: {e}\nMagnet was: {magnet}")
	os.chdir(BASE_PATH)

@app.route('/download/torrent/')
def download_torrent_endpoint():
	magnet = flask.request.args.get('magnet')
	x = threading.Thread(target=download_torrent_thread, args=(magnet,))
	x.start()
	return "", 200


def open_link_thread(link):
	global currentMode
	if "youtu" in link:
		wantedMode = "youtube_firefox"
	elif "twitch" in link:
		wantedMode = "twitch_vlc"
	if currentMode is not None and wantedMode != currentMode:
		exec(f"{currentMode}.terminate()")
	currentMode = wantedMode
	exec(f"{currentMode}.launch('{link}')")

@app.route('/link/')
def link_endpoint():
	link = flask.request.args.get('url')
	x = threading.Thread(target=open_link_thread, args=(link,))
	x.start()
	return "", 200


def open_file_thread(file_path):
	global currentMode
	wantedMode = "file_vlc"
	if currentMode is not None and wantedMode != currentMode:
		exec(f"{currentMode}.terminate()")
	currentMode = wantedMode
	exec(f"{currentMode}.launch('{file_path}')")


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


def custom_object_for_client(customObject):
	clientObject = []
	for k in customObject.keys():
		if isinstance(customObject[k], dict):
			if 'cmd' in customObject[k].keys():
				clientObject.append(k)
			else:
				clientObject.append({k: custom_object_for_client(customObject[k])})
		else:
			clientObject.append(k)
	return clientObject

@app.route('/custom/', methods=['GET', 'POST', 'DELETE'])
def custom_endpoint():
	if flask.request.method == 'GET':
		if not os.path.isfile(CUSTOM_FILE_PATH):
			return json.dumps([]), 200
		with open(CUSTOM_FILE_PATH, 'r') as file:
			return json.dumps(custom_object_for_client(json.loads(file.read()))), 200
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
	global currentMode
	path = flask.request.args.get('path')
	if not os.path.isfile(CUSTOM_FILE_PATH):
		return "", 400
	with open(CUSTOM_FILE_PATH, 'r') as file:
		jsonObject = json.loads(file.read())
	pathItems = path.split('/')
	for pathItem in pathItems:
		if pathItem not in jsonObject.keys():
			return "", 400
		jsonObject = jsonObject[pathItem]

	wantedMode = "custom"
	if currentMode is not None and wantedMode != currentMode:
		exec(f"{currentMode}.terminate()")
	currentMode = wantedMode
	exec(f"{currentMode}.launch({repr(jsonObject)})")
	return "", 200


@app.route('/clear/')
def clear_endpoint():
	global currentMode
	if currentMode is None:
		return "", 400
	exec(f"{currentMode}.terminate()")
	currentMode = None
	return "", 200


@app.route('/pause/')
def pause_endpoint():
	if currentMode is None or currentMode == "custom":
		return "", 400
	exec(f"{currentMode}.control_key('pause')")
	return "", 200


@app.route('/forward/')
def forward_endpoint():
	if currentMode is None or currentMode == "custom":
		return "", 400
	exec(f"{currentMode}.control_key('forward')")
	return "", 200


@app.route('/rewind/')
def rewind_endpoint():
	if currentMode is None or currentMode == "custom":
		return "", 400
	exec(f"{currentMode}.control_key('rewind')")
	return "", 200


@app.route('/volumeup/')
def volumeup_endpoint():
	if currentMode is None or currentMode == "custom":
		return "", 400
	exec(f"{currentMode}.control_key('volumeup')")
	return "", 200


@app.route('/volumedown/')
def volumedown_endpoint():
	if currentMode is None or currentMode == "custom":
		return "", 400
	exec(f"{currentMode}.control_key('volumedown')")
	return "", 200


@app.route('/fullscreen/')
def fullscreen_endpoint():
	if currentMode is None or currentMode == "custom":
		return "", 400
	exec(f"{currentMode}.control_key('fullscreen')")
	return "", 200


@app.route('/mute/')
def mute_endpoint():
	if currentMode is None or currentMode == "custom":
		return "", 400
	exec(f"{currentMode}.control_key('mute')")
	return "", 200


@app.route('/captions/')
def captions_endpoint():
	if currentMode is None or currentMode == "custom":
		return "", 400
	exec(f"{currentMode}.control_key('captions')")
	return "", 200


@app.route('/increasespeed/')
def increasespeed_endpoint():
	if currentMode is None or currentMode == "custom":
		return "", 400
	exec(f"{currentMode}.control_key('increasespeed')")
	return "", 200


@app.route('/decreasespeed/')
def decreasespeed_endpoint():
	if currentMode is None or currentMode == "custom":
		return "", 400
	exec(f"{currentMode}.control_key('decreasespeed')")
	return "", 200



# app.run(host='0.0.0.0', port=8081)
if __name__ == "__main__":
	from waitress import serve
	import socket
	print(f"serving at: {socket.gethostbyname(socket.gethostname())}")
	serve(app, host='0.0.0.0', port=8081)