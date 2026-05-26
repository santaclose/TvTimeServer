import os
desktop = os.environ.get("XDG_CURRENT_DESKTOP", "Unknown")
import sys
import subprocess

import moreos
if desktop == "Hyprland":
	import inputsym_hypr as inputsym
else:
	import inputsym

process = None

def is_running():
	global process
	return process is not None

def launch(file_path):
	global process
	if is_running():
		moreos.kill_process_group(process.pid)
	process = subprocess.Popen(["vlc", "--fullscreen", "--sub-autodetect-fuzzy=1"] + [moreos.fix_path(file_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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