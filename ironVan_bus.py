# INTERFACE
#
# Class:
# - Bus() - call to instantiate bus object
# - ...functions...
# -- 
# - ...variables...
# -- Bus().deviceAddress - dictionary containing key/value pair of {type: addr}
# -- Bus().storedDevices
import asyncio
import time

try:	
	from smbus2 import SMBus, i2c_msg

except:
	print('No bus detected...')
	pass

import ironVan_log as log

class Device():
	def __init__(self, deviceName: str, deviceType: str, deviceAddr: str):

		self.name = deviceName
		self.type = deviceType
		self.address = deviceAddr
		self.command = None
		self.request = None

		# {gmtime: [byte_1, byte_2, ...]}
		# # of bytes = # of bytes request in self.request['status']
		self.readout = {}
		
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
						'grey_tank_valve_open': [0x06],
						'grey_tank_valve_close': [0x07]
					}

					# Define available requests
					
					self.request = {
						'device_type':	[0x20, 14],
						'device_status':  [0x21, 1]
					}
					
		# --- LIGHTING ---
		if('ltsy' in deviceType):
		# Choose PCB version
		
			if("b100" in deviceType):
				# Choose firmware major version

				if("v0" in deviceType):
					# Define available commands

					self.command = {
						'ls_1_toggle': [0x01],
						'ls_2_toggle': [0x02],
						'ls_3_toggle': [0x03],
						'ls_4_toggle': [0x04]
					}

					# Define available requests
					
					self.request = {
						'device_type':	[0x20, 14],
						'device_status': [0x21, 4]
					}

		# --- THERMOSTAT ---
		if('temp' in deviceType):
			# Choose PCB version
			
			if("b100" in deviceType):
				# Choose firmware major version

				if("v0" in deviceType):
					# Define available commands
					
					self.command = {
						'fan_low_on': [0x00],
						'fan_low_off': [0x01],
						'fan_high_on': [0x02],
						'fan_high_off': [0x03],
						'ac_on': [0x04],
						'ac_off': [0x05],
						'heat_on': [0x06],
						'heat_off': [0x07]
					}

					# Define available requests
					
					self.request = {
						'device_type':	[0x20, 14],
						'status':  [0x21, 1]
					}

	def updateDevice(self, app, requestTime, response):
		'''
		Called by bus.parseResponse to update:
		- Status objects
		'''
		
		# --- UTILITIES ---
		if('util' in self.type):
			# Choose PCB version
			
			if("b100" in self.type):
				# Choose firmware major version

				if("v0" in self.type):
					'''
					util_b100_v010 has no plottable features - i.e. there is no need for a self.readout.

					util_b100_v010 readout will simply confirm the button position with the state of the device and throw a flag if the device is commanding an action not commanded by the user and vice versa.

					This version of the board has the following pinout:
					 - Digital Pin 9 / PB1 - Grey Tank Valve
					 	- 0 - 'open' / 1 - 'close'
					 - Digital Pin 10 / PB2 - Grey Tank Heat
					 	- 0 - 'auto' / 1 - 'off'
					 - Digital Pin 11 / PB3 - Shower Fan
					 	- 0 - 'auto' / 1 - 'off'
					 - Digital Pin 12 / PB4 - Water Pump
					 	- 0 - 'off' / 1 - 'on'
						 
					PINB is initially read, then isolated to a single nibble -> MSB - PB4 / LSB - PB1
					'''
					#self.readout[requestTime] = response
					#del self.readout[list(self.readout.keys())[0]]
					
					try:
						responseInt = int(response)

						# Isolate PB1 thru PB4
						responseInt = responseInt >> 1
						responseInt = responseInt & 240
					except:
						msg = 'Invalid response '

					# Initialize local variables for tracking
					# Initial state is case '0' (0b0000)
					greyTank = 'close'
					greyHeat = 'auto'
					showerFan = 'auto'
					waterPump = 'off'

					# Check bit status by applying bit mask
					if((1 & responseInt) == 1):
						greyTank = 'open'

					if((2 & responseInt) == 2):
						greyHeat = 'off'

					if((4 & responseInt) == 4):
						showerFan = 'off'

					if((8 & responseInt) == 8):
						waterPump = 'on'

					# -- NEED TO IMPLEMENT ERROR CHECKING --
					# --- Functionality not currently active
					
		# --- LIGHTING ---
		if('ltsy' in self.type):
		# Choose PCB version
		
			if("b100" in self.type):
				# Choose firmware major version

				if("v0" in self.type):
					
					return

		# --- THERMOSTAT ---
		if('temp' in self.type):
			# Choose PCB version
			
			if("b100" in self.type):
				# Choose firmware major version

				if("v0" in self.type):
					
					return

class Bus():
	def __init__(self, log):
		
		# Dictionary -> {'deviceName': Device()}
		self.activeDevices = {}

		# Dictionary -> {'deviceType_time': response}
		self.responseBuffer = {}

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
		
	async def regularScan(self, app):
		'''
		Asynchronous function scheduled by ironVanApp.build() that fills the responseBuffer with time-stamped responses. The responses are parsed and cleared in parseResponses.
		'''
		async with self.activeDevices as devices:
			for device in devices:
				self.responseBuffer[f'{device}_{time.gmtime}'] = await self.send(
					'request',
					devices[device].address,
					devices[device].request['device_status']
				)
	
	async def parseResponses(self, app):
		'''
		Asynchronous function that parses and cleares in device responses acquired in regularScan. parseResponses also checks for an overloaded buffer that would indicate inadequate parsing. In this case, the function will clear the buffer and log the error to the errorLog.
		'''
		if(len(self.responseBuffer) > 100):
			self.responseBuffer.clear()
			# The following console print should be replaced by an error log
			print('Response buffer overloaded and flushed.')
			return
		elif(len(self.responseBuffer) < 1):
			return
		else:
			async for event in self.responseBuffer:
				divider = event.index('_')
				deviceName = event[:divider]
				requestTime = int(event[(divider + 1):])
				self.activeDevices[deviceName].updateDevice(app, requestTime, self.responseBuffer[event])

	def rawMsg2Str(self, msg):
		# Store the raw message in a list as integers representing ASCII values, then 
		charList = list(msg)
		
		outputStr = ''
		
		for x in charList:
			outputStr += chr(x)
			
		return outputStr
