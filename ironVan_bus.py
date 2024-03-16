# INTERFACE
#
# Class:
# - Bus() - call to instantiate bus object
# - ...functions...
# -- 
# - ...variables...
# -- Bus().deviceAddress - dictionary containing key/value pair of {type: addr}
# -- Bus().storedDevices

try:	
	from smbus2 import SMBus, i2c_msg

except:
		pass

import ironVan_log as log

class Device():
	def __init__(self, deviceName: str, deviceType: str, deviceAddr: str):

		self.name = deviceName
		self.type = deviceType
		self.address = deviceAddr
		self.command = None
		self.request = None
		
		# Choose type of device
		
		# --- UTILITIES ---
		if('util' in deviceType):
			# Choose PCB version
			
			if("b100" in deviceType):
				# Choose firmware major version

				if("v0" in deviceType):
					# Define available commands
					
					self.command = {
						'water_pump_auto': [0x00],
						'water_pump_off': [0x01],
						'fan_auto': [0x02],
						'fan_off': [0x03],
						'grey_tank_heater_auto': [0x04],
						'grey_tank_heater_off': [0x05],
						'grey_tank_valve_close': [0x06],
						'grey_tank_valve_open': [0x07]
					}

					# Define available requests
					
					self.request = {
						'device_type':	[0x20, 14],
						'status':  [0x21, 1]
					}
					
		# --- LIGHTING ---
		# Note:  Light system is currently set up for "on/off" functionality sending one byte in the command sequence. For full functionality, send two bytes -> one stating which light to affect (0x00 - 0x03) and the send stating the value of the PWM signal (0 - 255)
		if('ltsy' in deviceType):
		# Choose PCB version
		
			if("b100" in deviceType):
				# Choose firmware major version

				if("v0" in deviceType):
					# Define available commands

					self.command = {
						'ls_1_toggle': [0x00],
						'ls_2_toggle': [0x01],
						'ls_3_toggle': [0x02],
						'ls_4_toggle': [0x03]
					}

					# Define available requests
					
					self.request = {
						'device_type':	[0x20, 14],
						'device_status': [0x21, 4]
					}

class Bus():
	def __init__(self, log):

		# Dictionary -> {'deviceName': Device()}
		self.activeDevices = {}

		# Initialize bus from location -1 on RPi
		try:
			self.bus = SMBus(1)

		except:
			print('No active bus...')
			return

		# Stores {device type: addr}
		deviceAddress = {}
		
		for addr in range(0x03, 0x77):
			try:
				# Request device type from address (addr)

				# Request 14 char DEVICE_TYPE from each address
				msg = self.bus.read_i2c_block_data(addr, 0x20, 14)
				
				deviceType = self.rawMsg2Str(msg)

				# Store device type defined by address if found - stored separate from self.storeDevices to allow for future development of dynamic addressing
				deviceAddress[deviceType] = addr
				
			except:
				continue	

		print("Devices found on bus: ", deviceAddress)
		print("Initializing devices...")

		# Temp code -- should be replaced with subroutine that checks a log document to see if device has previously been stored, then either automatically runs the Device() setup or sends user to a GUI setup page
		self.value = []

		for deviceType in deviceAddress:
			if 'util' in deviceType:
				self.activeDevices['utilities'] = Device('utilities', deviceType, deviceAddress[deviceType])
			elif 'ltsy' in deviceType:
				self.activeDevices['lighting'] = Device('lighting', deviceType, deviceAddress[deviceType])
				
	def sendCommandCLI(self):
		while(True):
			addr = int(input("Address: "))
			cmd = int(input("Command: "))
			self.bus.write_byte_data(addr, 0, cmd)

	def send(self, msgType: str, addr: int, message: int):
		# Channel through which all commands and requests should be sent outside of the initial scan for active devicess
		#
		# Parameters:
		# - msgType - 'request' or 'command'
		# - addr - Device().address
		# - message - Device().command['x_command'] or Device().request('')
		if('command' in msgType):
			#self.bus.write_byte_data(addr, 0, message)
			self.bus.write_i2c_block_data(addr, 0, message)
			return 'command sent'
		
		elif('request' in msgType):
			msg = self.rawMsg2Str(self.bus.read_i2c_block_data(addr, message[0], message[1]))
			return msg
	
	def rawMsg2Str(self, msg):
		# Store the raw message in a list as integers representing ASCII values, then 
		charList = list(msg)
		
		outputStr = ''
		
		for x in charList:
			outputStr += chr(x)
			
		return outputStr
