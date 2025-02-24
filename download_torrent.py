import libtorrent as lt
import time
import sys

import common

ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})

add_torrent_params = lt.parse_magnet_uri(sys.argv[1])
add_torrent_params.flags = lt.torrent_flags.sequential_download | lt.torrent_flags.default_flags# | lt.torrent_flags.stop_when_ready
add_torrent_params.save_path = sys.argv[2]

h = ses.add_torrent(add_torrent_params)
while not h.has_metadata():
	time.sleep(.1)

info = h.get_torrent_info()

i = 0
for f in info.files():
	priority = 7 if common.fileIsSubtitleFile(f.path) else (4 if common.fileIsVideoFile(f.path) else 0)
	h.file_priority(i, priority)
	print(f"Setting priority {priority} for file: {f.path}")
	i += 1

s = h.status()
print('starting', s.name)

while (not s.is_seeding):
	s = h.status()

	print('\r%.2f%% complete (down: %.1f kB/s up: %.1f kB/s peers: %d) %s' % (
		s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000,
		s.num_peers, s.state), end=' ')

	alerts = ses.pop_alerts()
	for a in alerts:
		if a.category() & lt.alert.category_t.error_notification:
			print(a)

	sys.stdout.flush()
	time.sleep(1)

print(h.status().name, 'torrent finished downloading')
ses.remove_torrent(h)
sys.exit(0)