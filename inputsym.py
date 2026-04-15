import time
import pyperclip
import subprocess

def keyPress(key):
	if isinstance(key, list):
		command = ["hyprctl", "dispatch", "sendshortcut", f"{key[0]},", f"{key[1]},", "activewindow"]
		subprocess.run(command, stdout=subprocess.DEVNULL)
	else:
		command = ["hyprctl", "dispatch", "sendshortcut", ",", f"{key},", "activewindow"]
		subprocess.run(command, stdout=subprocess.DEVNULL)

def keyWrite(text):
	temp = getClipText()
	setClipText(text)
	time.sleep(0.1)
	command = ["hyprctl", "dispatch", "sendshortcut", "ctrl,", "v,", "activewindow"]
	subprocess.run(command, stdout=subprocess.DEVNULL)
	time.sleep(0.1)
	setClipText(temp)

def setClipText(text):
	pyperclip.copy(text)
def getClipText():
	return pyperclip.paste()
