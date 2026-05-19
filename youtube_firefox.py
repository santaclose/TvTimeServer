import os
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException

if os.name == "nt":
	import inputsym_win as inputsym
else:
	import inputsym

seleniumDriver = None

def get_default_profile():
	firefox_dir = Path.home() / ".mozilla" / "firefox"
	for profile in firefox_dir.glob("*.default-release"):
		return profile
	firefox_dir = Path.home() / ".config" / "mozilla" / "firefox"
	for profile in firefox_dir.glob("*.default-release"):
		return profile
	raise FileNotFoundError("No Firefox default-release profile found")

def wait_until_load():
	global seleniumDriver
	time.sleep(1.0)
	element = WebDriverWait(seleniumDriver, 20).until(
		EC.presence_of_element_located((By.ID, "movie_player"))
	)
	time.sleep(1.0)

def is_running():
	global seleniumDriver
	return seleniumDriver is not None

def launch(link):
	global seleniumDriver
	if is_running():
		inputsym.simulate(["escape", ["ctrl", "l"], ["ctrl", "a"], "delete", f"type:{link}", "return"])
		wait_until_load()
		control_key('fullscreen')
	else:
		options = Options()
		profile_path = get_default_profile()
		options.add_argument(f"--profile={profile_path}")
		seleniumDriver = webdriver.Firefox(options=options)
		try:
			seleniumDriver.get(link)
			wait_until_load()
			control_key('fullscreen')
		except Exception as e:
			print(f"Selenium error: {e}")

def terminate():
	global seleniumDriver
	if is_running():
		seleniumDriver.quit()
	seleniumDriver = None

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