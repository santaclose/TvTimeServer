import os
import signal
import psutil
import plyer
import subprocess

currentDisplayIsExternal = True

def switch_display():
	global currentDisplayIsExternal
	if os.name == 'nt':
		subprocess.run(["DisplaySwitch.exe", "/internal" if currentDisplayIsExternal else "/external"])
	currentDisplayIsExternal = not currentDisplayIsExternal

def get_process_name_set():
	out = set()
	for proc in psutil.process_iter():
		out.add(proc.name().lower())
	return out

def kill_processes_with_name(process_name):
	try:
		for proc in psutil.process_iter():
			if process_name.lower() in proc.name().lower():
				proc.kill()
	except Exception as e:
		return False
	return True

def kill_process_with_pid(pid):
	os.kill(pid, signal.SIGTERM)

def is_process_running(process_name):
	for proc in psutil.process_iter():
		if process_name.lower() in proc.name().lower():
			return True
	return False

def show_notification(title, message):
	try:
		plyer.notification.notify(
			title = title,
			message = message,
			app_icon = None,
			timeout = 10,
		)
	except Exception as e:
		subprocess.Popen(["zenity", "--notification", "--window-icon=info", f'--text={message}'])
