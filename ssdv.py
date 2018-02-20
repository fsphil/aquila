#!/usr/bin/python3

import subprocess

ssdv_exe = '/usr/bin/ssdv'

class encoder:
	
	def __init__(self, callsign = '', quality = 4, fec = True):
		
		self.callsign = callsign
		self.quality  = quality
		self.fec      = fec
		self.image_id = 0
	
	def encode_file(self, filename):
		
		command = [
			ssdv_exe,
			'-e',
			'-c', self.callsign,
			'-i', str(int(self.image_id) & 0xFF),
			'-q', str(int(self.quality)),
			filename
		]
		if self.fec == False: command.append('-n')
		
		try:
			packets = subprocess.check_output(command)
		except:
			return None
		
		packets = [packets[x:x + 256] for x in range(0, len(packets), 256)]
		
		self.image_id += 1
		
		return packets
	
	def encode_jpeg(self, jpeg):
		
		command = [
			ssdv_exe,
			'-e',
			'-c', self.callsign,
			'-i', str(int(self.image_id) & 0xFF),
			'-q', str(int(self.quality))
		]
		if self.fec == False: command.append('-n')
		
		try:
			packets = subprocess.check_output(command, input = jpeg)
		except:
			return None
		
		packets = [packets[x:x + 256] for x in range(0, len(packets), 256)]
		
		self.image_id += 1
		
		return packets

