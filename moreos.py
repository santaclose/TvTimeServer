import os
import signal
import psutil
import plyer
import subprocess

currentDisplayIsExternal = True

def switch_display():
	if os.name == 'nt':
		global currentDisplayIsExternal
		subprocess.run(["DisplaySwitch.exe", "/internal" if currentDisplayIsExternal else "/external"])
		currentDisplayIsExternal = not currentDisplayIsExternal
	else:
		selectedMonitor = subprocess.check_output("hyprctl monitors -j | jq -r '.[] | select(.focused == true) | .name'", shell=True).decode('utf-8').strip()
		allMonitors = subprocess.check_output("hyprctl monitors all -j | jq -r '.[] | .name'", shell=True).decode('utf-8').strip().split('\n')
		for i in range(len(allMonitors)):
			monitor = allMonitors[i]
			if selectedMonitor == monitor:
				nextMonitorIndex = (i + 1) % len(allMonitors)
				subprocess.run(f"hyprctl keyword monitor {monitor},disable", shell=True)
				subprocess.run(f"hyprctl keyword monitor {allMonitors[nextMonitorIndex]},enable", shell=True)

def kill_process_with_pid(pid):
	os.kill(pid, signal.SIGTERM)

def kill_process_group(pid):
	children = psutil.Process(pid).children(recursive=True)
	for child in children:
		child.kill()
	os.kill(pid, signal.SIGTERM)
	return len(children)

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
