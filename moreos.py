import os
import signal
import psutil
import plyer
import subprocess

def kill_processes_with_name(process_name):
	for proc in psutil.process_iter():
		if process_name.lower() in proc.name().lower():
			proc.kill()

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
