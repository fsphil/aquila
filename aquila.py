#!/usr/bin/python3

import ssdv
import signal
from sx127x import sx127x
from wenet import wenet

from io import BytesIO
from time import sleep
from picamera import PiCamera

callsign = 'AQUILA'
frequency = 434500000
bitrate = 12500

def picam_grab_jpeg(resolution):
	
	with PiCamera() as c:
		s = BytesIO()
		c.resolution = resolution
		
		c.start_preview()
		sleep(2) # Camera warmup (do I need this?)
		
		c.capture(s, 'jpeg')
		
		s.seek(0)
		jpeg = s.read()
		s.close()
	
	return jpeg

# ------------------------------------------

# Setup the radio
packets = wenet()
radio = sx127x(0, 1)
radio.start_tx(packets, frequency, bitrate)

# Setup the SSDV encoder
s = ssdv.encoder(callsign, quality = 4, fec = False)

running = True

def signal_handler(sig, frame):
	global running
	running = False

signal.signal(signal.SIGINT, signal_handler)

# Transmit images forever
while running:
	
	jpeg = picam_grab_jpeg((1440, 960))
	pkts = s.encode_jpeg(jpeg)
	
	for pkt in pkts:
		packets.write('ssdv', pkt)
		if not running:
			break

radio.stop_tx()

