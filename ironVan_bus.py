from smbus2 import SMBus, i2c_msg

import ironVan_log as log

class Bus:
	def __init__(self):
		# Initialize bus from location -1 on RPi
		self.bus = SMBus(1)

		# Stores {device address: type}
		self.devices = {}
		
		for addr in range(0x03, 0x77):
			try:
				# Request device type from address (addr)

				# Request 14 char DEVICE_TYPE from each device
				msg = self.bus.read_i2c_block_data(addr, 0x20, 14)
				
				deviceType = self.rawMsg2Str(msg)

				# Store device type defined by address
				self.devices[addr] = deviceType
				
			except:
				continue	

		print("Devices found on bus: ", self.devices)
				
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
	
	def rawMsg2Str(self, msg):
		# Store the raw message in a list as integers representing ASCII values, then 
		charList = list(msg)
		
		outputStr = ''
		
		for x in charList:
			outputStr += chr(x)
			
		return outputStr