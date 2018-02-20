#!/usr/bin/python3

import spidev
import time
from threading import Thread

class sx127x:
	
	# Crystal oscillator frequency and frequency synth step size in Hz
	fxosc = 32000000
	fstep = fxosc / (2 ** 19)
	
	def __init__(self, bus, device):
		
		# Open and configure the SPI interface to the radio
		self.spi = spidev.SpiDev()
		self.spi.open(bus, device)
		self.spi.max_speed_hz = 10000000
	
	def start_tx(self, pkt_source, frequency, deviation):
		
		# Configure the radio for wenet @ 10kbit/s,
		# enable the transmitter and start the
		# transmit thread.
		
		# Place the radio into FSK and sleep mode
		self.write(0x01, 0x00)
		
		# 10,000 bit/s
		self.write(0x02, int(round(self.fxosc / 10000)), 2)
		
		# Set the deviation
		self.write(0x04, int(round(deviation / self.fstep)), 2)
		
		# Set the centre frequency
		self.write(0x06, int(round(frequency / self.fstep)), 3)
		
		# Set the power output level to 10 dB, / 10 mW
		self.write(0x09, (1 << 7) | (15 - (17 - 10)))
		
		# Turn off the modules packet framing features
		self.write(0x25, 0, 2) # 0 preamble bytes
		self.write(0x27, 0) # Disable sync word
		
		# Configure the radio for an unlimited length packet
		self.write(0x30, 0) # Fixed length packet, no whitening or CRC
		self.write(0x31, (1 << 6)) # Packet mode enabled
		self.write(0x32, 0) # Zero length packet
		
		# Start transmitting when at least 32 bytes are in the FIFO
		self.write(0x35, 32 - 1)
		
		# Setup DIO pins
		# DIO0: PacketSent
		# DIO1: FifoLevel -- This one is used to keep the FIFO topped up
		# DIO2: FifoFull
		# DIO3: FifoEmpty
		# DIO4: TempChange / LowBat
		# DIO5: ClkOut
		
		# Ensure the FIFO is clear
		self.write(0x3F, 1 << 4)
		
		# Enable the transmitter
		self.write(0x01, 0x02) # FSTX (Sets the frequency)
		self.write(0x01, 0x03) # TX
		
		# Enable bit reversing (MSB <> LSB)
		#pkt_source.bit_reverse = True
		
		# Start the transmit thread
		self.transmit_active = True
		self.pkt_source = pkt_source
		self.tx_thread_ref = Thread(target = self.tx_thread)
		self.tx_thread_ref.start()
	
	def stop_tx(self):
		
		# Stop the transmit thread
		self.transmit_active = False
		self.tx_thread_ref.join()
		
		# Place the radio into sleep mode
		self.write(0x01, 0x00)
	
	def tx_thread(self):
		
		print("Transmit thread started")
		
		while self.transmit_active:
			
			# Fetch the next packet
			packet = self.pkt_source.read()
			
			# Transmit the packet in chunks up to 32 bytes long
			for x in range(0, len(packet), 32):
				
				# Wait until the FIFO is ready
				while self.irq() & (1 << 5):
					time.sleep(0.0016) # Noooooo
				
				self.write(0x00, packet[x:x + 32])
		
		print("Transmit thread ending")
	
	def readb(self, register, size = 1):
		
		data = [register] + [0x00] * size
		data = self.spi.xfer(data)
		
		return bytes(data[1:])
	
	def read(self, register, size = 1):
		
		data = self.readb(register, size)
		
		value = 0
		for x in range(0, size):
			value = (value << 8) | data[x]
		
		return value
	
	def write(self, register, value, size = 1):
		
		if type(value) is bytes:
			data = [0x80 | register] + list(value)
		
		else:
			data = [0x80 | register] + [(value >> x) & 0xFF for x in range(0, size * 8, 8)[::-1]]
		
		self.spi.xfer(data)
	
	def irq(self):
		
		return self.read(0x3E, 2)
	
	def dump_irq(self):
		
		irq = self.read(0x3E, 2)
		print('{:016b}'.format(irq))

