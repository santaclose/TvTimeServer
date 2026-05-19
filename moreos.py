import os
import re
import signal
import psutil
import plyer
import subprocess
from pathlib import Path

currentDisplayIsExternal = True

def fix_path(path):
	if os.name == 'nt':
		return path.replace('/', '\\')
	return path

def switch_display():
	if os.name == 'nt':
		global currentDisplayIsExternal
		subprocess.run(["DisplaySwitch.exe", "/internal" if currentDisplayIsExternal else "/external"])
		currentDisplayIsExternal = not currentDisplayIsExternal
	else:
		selectedMonitor = subprocess.check_output("hyprctl monitors -j | jq -r '.[] | select(.focused == true) | .name'", shell=True).decode('utf-8').strip()
		allMonitors = subprocess.check_output("hyprctl monitors all -j | jq -r '.[] | .name'", shell=True).decode('utf-8').strip().split('\n')

		hyprlandConfigPath = Path("~/.config/hypr/hyprland.lua").expanduser()
		hyprlandConfigLines = hyprlandConfigPath.read_text(encoding="utf-8").splitlines()
		hyprlandConfigLinesWithMonitor = dict()
		for i, line in enumerate(hyprlandConfigLines):
			m = re.match(r'hl\.monitor\(\{\s*output\s*=\s*"([^"]+)"', line)
			if m is not None:
				hyprlandConfigLinesWithMonitor[m.group(1)] = i

		for i in range(len(allMonitors)):
			monitor = allMonitors[i]
			if selectedMonitor == monitor:
				nextMonitorIndex = (i + 1) % len(allMonitors)
				hyprlandConfigLines[hyprlandConfigLinesWithMonitor[monitor]] = hyprlandConfigLines[hyprlandConfigLinesWithMonitor[monitor]].replace("true", "true").replace("false", "true")
				hyprlandConfigLines[hyprlandConfigLinesWithMonitor[allMonitors[nextMonitorIndex]]] = hyprlandConfigLines[hyprlandConfigLinesWithMonitor[allMonitors[nextMonitorIndex]]].replace("true", "false").replace("false", "false")
		hyprlandConfigPath.write_text("\n".join(hyprlandConfigLines), encoding="utf-8")
		subprocess.run("hyprctl reload", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def kill_process_with_pid(pid):
	os.kill(pid, signal.SIGKILL)

def kill_process_group(pid):
	children = psutil.Process(pid).children(recursive=True)
	for child in children:
		os.kill(child.pid, signal.SIGKILL)
	os.kill(pid, signal.SIGKILL)
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
