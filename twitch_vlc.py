import os
import sys
import subprocess

import moreos
if os.name == "nt":
	import inputsym_win as inputsym
else:
	import inputsym

process = None

def is_running():
	global process
	return process is not None

def launch(link):
	global process
	if is_running():
		moreos.kill_process_group(process.pid)
	process = subprocess.Popen([sys.executable,  "-m", "streamlink", "--twitch-low-latency", link, "720p,480p,best", "--player-args", "--fullscreen"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def terminate():
	global process
	if is_running():
		moreos.kill_process_group(process.pid)

controlKeys = {
	"pause": "space",
	"forward": "right",
	"rewind": "left",
	"volumeup": "up",
	"volumedown": "down",
	"fullscreen": "f",
	"mute": "m",
	"captions": "v",
	"increasespeed": "bracketright",
	"decreasespeed": "bracketleft",
}
def control_key(control):
	inputsym.keyPress(controlKeys[control])