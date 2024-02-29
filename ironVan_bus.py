# INTERFACE
#
# Class:
# - Bus() - call to instantiate bus object
# - ...functions...
# -- 
# - ...variables...
# -- Bus().deviceAddress - dictionary containing key/value pair of {type: addr}
# -- Bus().storedDevices

from smbus2 import SMBus, i2c_msg

import ironVan_log as log

class Device():
	def __init__(self, deviceType: str):
		# Choose type of device
		
		# --- UTILTIES ---
		if('util' in deviceType):
			# Choose PCB version
			
			if("b100" in deviceType):
				# Choose firmware major version

				if("v0" in deviceType):
					# Define available commands
					
					self.command = {
						'water_pump_on': 0x00,
						'water_pump_off': 0x01,
						'fan_auto': 0x02,
						'fan_off': 0x03,
						'grey_tank_heater_auto': 0x04,
						'grey_tank_heater_off': 0x05,
						'grey_tank_valve_close': 0x06,
						'grey_tank_valve_open': 0x07
						
					# Define available requests
					
					self.request = {
						'device_type':	[0x20, 14]
						'status':  [0x21, 1]
					}
					
			# --- LIGHTING ---

class Bus():
	def __init__(self):
		# Initialize bus from location -1 on RPi
		self.bus = SMBus(1)

		# Stores {device type: addr}
		self.deviceAddress = {}
		
		for addr in range(0x03, 0x77):
			try:
				# Request device type from address (addr)

				# Request 14 char DEVICE_TYPE from each address
				msg = self.bus.read_i2c_block_data(addr, 0x20, 14)
				
				deviceType = self.rawMsg2Str(msg)

				# Store device type defined by address if found - stored separate from self.storeDevices to allow for future development of dynamic addressing
				self.deviceAddress[deviceType] = addr
				
			except:
				continue	

		print("Devices found on bus: ", self.deviceAddress)
		print("Initializing devices...")

		# Temp code -- should be replaced with subroutine that checks a log document to see if device has previously been stored, then either automatically runs the Device() setup or sends user to a GUI setup page
		self.storedDevices = {}
		self.value = []

		for deviceType in self.deviceAddress:
			deviceName = input(f"A device of type {deviceType} was found at address {self.deviceAddress[deviceType]}. What would you like to name this device? ... ")

			self.storedDevices[deviceName] = Device(deviceType)
		
		print(self.storedDevices['Utilities'].command)
				
	def sendCommandCLI(self):
		while(True):
			addr = int(input("Address: "))
			cmd = int(input("Command: "))
			self.bus.write_byte_data(addr, 0, cmd)

	def send(self, deviceMessage):
		# deviceMessage is a nested object that contains attributes from the Device() class. The final attribute should be .request['request'] or .command['command']
		
		if('command' in deviceMessage):
			# Needs to look up the address
			self.write_byte_data()
			return
		elif('command' in deviceMessage):
			msg = rawMsg2Str(self.read_i2c_block_data())
	
	def rawMsg2Str(self, msg):
		# Store the raw message in a list as integers representing ASCII values, then 
		charList = list(msg)
		
		outputStr = ''
		
		for x in charList:
			outputStr += chr(x)
			
		return outputStr
	
	## --- Device Specific Commands -> Routed from self.sendCommand() --- ##

