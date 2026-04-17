sudo pacman -Sy
sudo pacman -S zenity python-uv vlc vlc-plugins-all firefox

uv venv --python 3.11.1
source .venv/bin/activate
uv pip install -r requirements.txt --python 3.11.1