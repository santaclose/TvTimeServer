import re
import os
import shutil
import requests
import subprocess

BASE_PATH = os.path.dirname(__file__)
ARCH = "amd64"
# ARCH = "arm64"

def get_command():
	if os.name == 'nt':
		return f"{BASE_PATH}/freetube/FreeTube.exe"
	else:
		return "freetube"

def update_if_needed():
	tagsHtml = requests.get("https://github.com/FreeTubeApp/FreeTube/tags").content.decode('utf-8')
	latestVersion = re.findall(r'<a.*href="/FreeTubeApp/FreeTube/releases/tag/([^"]+)"', tagsHtml)[0]
	# latestVersion will be something like: "v0.23.8-beta"

	currentVersion = 'Unknown'
	if os.path.isfile(f"{BASE_PATH}/freetube_version.txt"):
		with open(f"{BASE_PATH}/freetube_version.txt", 'r') as file:
			currentVersion = file.read()
	if latestVersion == currentVersion:
		print(f"Using latest freetube version: {latestVersion}")
		return

	if currentVersion == "Unknown":
		print(f"Installing freetube version: {latestVersion}")
	else:
		print(f"Updating freetube from {currentVersion} to {latestVersion}")
		if os.name == 'nt':
			shutil.rmtree(f'{BASE_PATH}/freetube')

	urlPartA = latestVersion
	urlPartB = latestVersion[1:].replace('-', '_')
	if os.name == 'nt':
		targetUrl = f"https://github.com/FreeTubeApp/FreeTube/releases/download/{urlPartA}/freetube-{urlPartB}-win-{ARCH.replace('amd', 'x')}-portable.zip"
		subprocess.run(["curl", targetUrl, "--output", f"{BASE_PATH}/freetube.zip", "-L"])
		subprocess.run(["powershell", "-Command", f'Expand-Archive "{BASE_PATH}/freetube.zip" -DestinationPath "{BASE_PATH}/freetube"'])
		os.remove(f"{BASE_PATH}/freetube.zip")

	else:
		targetUrl = f"https://github.com/FreeTubeApp/FreeTube/releases/download/{urlPartA}/freetube_{urlPartB}_{ARCH}.deb"

		assert(subprocess.run(["wget", targetUrl]).returncode == 0)
		with open("password.txt", 'r') as file:
			assert(subprocess.run(["sudo", "-S", "dpkg", "-i", f"freetube_{urlPartB}_{ARCH}.deb"], stdin=file).returncode == 0)

		assert(subprocess.run(['rm', f"freetube_{urlPartB}_{ARCH}.deb"]).returncode == 0)

	with open("freetube_version.txt", 'w') as file:
		file.write(latestVersion)


if __name__ == "__main__":
	update_if_needed()