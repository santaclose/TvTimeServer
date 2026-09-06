import os
desktop = os.environ.get("XDG_CURRENT_DESKTOP", "Unknown")
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException

if desktop == "Hyprland":
	import inputsym_hypr as inputsym
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
		options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0")
		# 2. Relax tracking and media restrictions that break caption syncing
		options.set_preference("privacy.trackingprotection.enabled", False)
		options.set_preference("media.autoplay.default", 0)
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