import time
import pyperclip
import subprocess

def keyPress(key):
	if isinstance(key, list):
		lua_args = f'hl.dsp.send_shortcut({{ mods = "{key[0]}", key = "{key[1]}", window = "activewindow" }})'
	else:
		lua_args = f'hl.dsp.send_shortcut({{ key = "{key}", window = "activewindow" }})'
	command = ["hyprctl", "dispatch", lua_args]
	subprocess.run(command, stdout=subprocess.DEVNULL)

def keyWrite(text):
	temp = getClipText()
	setClipText(text)
	time.sleep(0.1)
	lua_args = 'hl.dsp.send_shortcut({ mods = "CONTROL", key = "V", window = "activewindow" })'
	command = ["hyprctl", "dispatch", lua_args]
	subprocess.run(command, stdout=subprocess.DEVNULL)
	time.sleep(0.1)
	setClipText(temp)

def setClipText(text):
	pyperclip.copy(text)
def getClipText():
	return pyperclip.paste()

def simulate(actionList):
	typePrefix = "type:"
	for action in actionList:
		if isinstance(action, str) and action.startswith(typePrefix):
			keyWrite(action[len(typePrefix):])
		else:
			keyPress(action)
		time.sleep(0.17)