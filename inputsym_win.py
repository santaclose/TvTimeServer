import time
import pynput
import pyautogui
import pyperclip

KEY_INTERVAL = 0.015
pkb = pynput.keyboard.Controller()

def getKey(key):
	if len(key) == 1:
		return f'"{key}"'
	return f"pynput.keyboard.Key.{key}"
def keyDown(key):
	time.sleep(KEY_INTERVAL)
	exec(f"pkb.press({getKey(key)})", globals(), locals())
def keyUp(key):
	time.sleep(KEY_INTERVAL)
	exec(f"pkb.release({getKey(key)})", globals(), locals())
def keyCombo(keys):
	for key in keys:
		time.sleep(KEY_INTERVAL)
		exec(f"pkb.press({getKey(key)})", globals(), locals())
	for key in reversed(keys):
		time.sleep(KEY_INTERVAL)
		exec(f"pkb.release({getKey(key)})", globals(), locals())
def keyPress(key):
	if isinstance(key, list):
		keyCombo(key)
		return
	time.sleep(KEY_INTERVAL)
	exec(f"pkb.press({getKey(key)})", globals(), locals())
	exec(f"pkb.release({getKey(key)})", globals(), locals())
def keyWrite(text):
	pyautogui.write(text)
def setClipText(text):
	pyperclip.copy(text)
def getClipText():
	return pyperclip.paste()
