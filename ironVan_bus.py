from smbus2 import SMBus, i2c_msg

import ironVan_log as log

class Bus:
	def __init__(self):
		# Initialize bus from location -1 on RPi
		self.bus = SMBus(1)

		# Stores {device address: type}
		self.devices = {};
		
		for addr in range(0x08, 0x09):
			try:
				# Request device type from address (addr)

				# ???  Update to block data to accept 14 characters  ???
				msg = i2c_msg.read(addr, 14)
				self.bus.i2c_rdwr(msg)
				
				deviceType = self.asciiList2Str(msg)

				# ???  Fix dictionary syntax ???
				self.devices[addr] = deviceType

				print(self.devices)
				
			except:
				continue	
				
	def sendCommandCLI(self):
		while(True):
			addr = int(input("Address: "))
			cmd = int(input("Command: "))
			self.bus.write_byte_data(addr, 0, cmd)

	def sendCommand(self, deviceType: str, cmd):
		# Search self.devices for a device that contains the deviceType keyword. Valid keywords include:
		#	- util - utilities device (1 per bus)
		#	- ltsy - lighting system device (1 per bus)
		#	- temp - thermostat device (1 per bus)

		return
	
	def asciiList2Str(self, msg):
		print(1)
		asciiTable = {
			0: "NUL",
			1: "SOH",
			48: "0",
			49: "1",
			95: "_",
			98: "b",
			105: "i",
			108: "l",
			116: "t",
			117: "u",
			118: "v"
		}
		print(2)
		charList = list(msg)
		print(3)
		outputStr = ''
		print(4)
		for x in charList:
			outputStr += asciiTable[x]
		print(5)
		return outputStr