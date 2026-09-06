import os
desktop = os.environ.get("XDG_CURRENT_DESKTOP", "Unknown")
import time
import moreos
import subprocess

if desktop == "Hyprland":
	import inputsym_hypr as inputsym
else:
	import inputsym

process = None
LOADING_TIME = 5.0
LAUNCH_TIME = 5.0

def wait_until_load():
	time.sleep(LOADING_TIME)

def is_running():
	global process
	return process is not None

def launch(link):
	global process
	if is_running():
		inputsym.simulate(["escape", ["ctrl", "l"], ["ctrl", "a"], f"type:{link}", "return"])
		wait_until_load()
		control_key('fullscreen')
	else:
		process = subprocess.Popen(["firefox", link])
		time.sleep(LAUNCH_TIME)
		wait_until_load()
		control_key('fullscreen')

def terminate():
	global process
	if is_running():
		moreos.kill_process_group(process.pid)
	process = None

controlKeys = {
	"pause": "k",
	"forward": "right",
	"rewind": "left",
	"volumeup": "up",
	"volumedown": "down",
	"fullscreen": "f",
	"mute": "m",
	"captions": "c",
	"increasespeed": ["shift", "period"],
	"decreasespeed": ["shift", "comma"]
}
def control_key(control):
	inputsym.keyPress(controlKeys[control])