#!/usr/bin/python3

# Wenet packet and queue handler.
#
# Copyright (C) 2018  Mark Jessop <vk5qi@rfhead.net>
# Released under GNU GPL v3 or later
#
# Modified by Philip Heron <phil@sanslogic.co.uk>
#

import struct
import queue
import wenet_ext

class wenet:
	
	def __init__(self, fec = True, reverse_bits = True):
		
		self.fec = fec
		self.reverse_bits = reverse_bits
		self.counter = 0
		self.queues = {
			'ssdv': queue.Queue(16),
			'telemetry': queue.Queue(16),
		}
		
		self.idle_packet = self.frame_packet(b'\x56' * 256)
	
	def frame_packet(self, data):
		
		prefix  = b'\x55' * 16
		prefix += struct.pack('>I', 0x3F34B54C) # Low self-correlation syncword
		
		packet  = data + struct.pack('<H', wenet_ext.crc16(data))
		
		if self.fec:
			packet += wenet_ext.ldpc_encode(packet)
		
		packet = prefix + packet
		
		if self.reverse_bits:
			packet = wenet_ext.reverse_bits(packet)
		
		return packet
	
	def read(self):
		
		# Test queues in order of priority for available packets
		for id in ('telemetry', 'ssdv'):
			try:
				return self.queues[id].get_nowait()
			
			except queue.Empty:
				pass
		
		# The queues are empty, return an idle packet
		return self.idle_packet
	
	def write(self, id, data):
		
		data = self.frame_packet(data)
		self.queues[id].put(data, block = True, timeout = 1)
		self.counter += 1

