import os
import time
import fcntl
import struct
import threading

# Virtual mouse through /dev/uinput (Hyprland has no dispatcher for clicking)

UI_SET_EVBIT = 0x40045564
UI_SET_KEYBIT = 0x40045565
UI_SET_RELBIT = 0x40045566
UI_DEV_CREATE = 0x5501

EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
SYN_REPORT = 0
REL_X = 0x00
REL_Y = 0x01
REL_WHEEL = 0x08

BUTTONS = {
	"left": 0x110,
	"right": 0x111,
	"middle": 0x112,
}

device = None
lock = threading.Lock()

def getDevice():
	global device
	if device is not None:
		return device
	fd = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)
	fcntl.ioctl(fd, UI_SET_EVBIT, EV_KEY)
	fcntl.ioctl(fd, UI_SET_EVBIT, EV_REL)
	for button in BUTTONS.values():
		fcntl.ioctl(fd, UI_SET_KEYBIT, button)
	for axis in (REL_X, REL_Y, REL_WHEEL):
		fcntl.ioctl(fd, UI_SET_RELBIT, axis)
	# struct uinput_user_dev: name[80], input_id (bustype, vendor, product, version), ff_effects_max, abs arrays
	userDev = struct.pack("80sHHHHi", b"tvtime-mouse", 0x06, 0x1234, 0x5678, 1, 0) + bytes(4 * 64 * 4)
	os.write(fd, userDev)
	fcntl.ioctl(fd, UI_DEV_CREATE)
	time.sleep(0.3) # give the compositor time to pick up the new device
	device = fd
	return device

def emit(fd, type, code, value):
	os.write(fd, struct.pack("llHHi", 0, 0, type, code, value))

def move(dx, dy):
	with lock:
		fd = getDevice()
		emit(fd, EV_REL, REL_X, dx)
		emit(fd, EV_REL, REL_Y, dy)
		emit(fd, EV_SYN, SYN_REPORT, 0)

def click(button="left"):
	with lock:
		fd = getDevice()
		emit(fd, EV_KEY, BUTTONS[button], 1)
		emit(fd, EV_SYN, SYN_REPORT, 0)
		time.sleep(0.01)
		emit(fd, EV_KEY, BUTTONS[button], 0)
		emit(fd, EV_SYN, SYN_REPORT, 0)
