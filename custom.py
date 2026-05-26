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

def launch(json_object):
	global process
	if is_running():
		moreos.kill_process_group(process.pid)
	if isinstance(json_object, str):
		process = subprocess.Popen(json_object, shell=True)
	elif isinstance(json_object, dict):
		process = subprocess.Popen(json_object["cmd"], cwd=json_object["cwd"], shell=True)

def terminate():
	global process
	if is_running():
		moreos.kill_process_group(process.pid)

def control_key(control):
	print(f"control {control} not bound")