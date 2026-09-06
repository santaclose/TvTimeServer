import os
desktop = os.environ.get("XDG_CURRENT_DESKTOP", "Unknown")
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

if desktop == "Hyprland":
	import inputsym_hypr as inputsym
else:
	import inputsym

seleniumDriver = None

def wait_until_load():
	global seleniumDriver
	time.sleep(4.0)
	element = WebDriverWait(seleniumDriver, 20).until(
		EC.visibility_of_element_located((By.ID, "movie_player"))
	)

def is_running():
	global seleniumDriver
	return seleniumDriver is not None

def launch(link):
	global seleniumDriver
	if is_running():
		inputsym.simulate(["escape", ["ctrl", "l"], ["ctrl", "a"], f"type:{link}", "return"])
		wait_until_load()
		control_key('fullscreen')
	else:
		options = Options()
		options.add_argument(f"--user-data-dir={Path.home() / '.config' / 'google-chrome'}")
		options.add_argument("--profile-directory=Default")
		options.add_argument("--no-sandbox")
		options.add_argument("--disable-dev-shm-usage")
		seleniumDriver = webdriver.Chrome(options=options)
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