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
		self.errorCount = 0

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
						'tank_heater_auto': [0x04],
						'tank_heater_off': [0x05],
						'tank_valve_open': [0x06],
						'tank_valve_close': [0x07]
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
	 				# Note:  The 'ls_n_toggle' commands are appended with a 1 byte value from either -- the toggle button (0 or current slider value) -- or -- app.lightingAdjust() (slider value)

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

		# --- LIGHT SWITCH & THERMOMETER ---
		if('ltsw' in deviceType):
		# Choose PCB version
		
			if("b100" in deviceType):
				# Choose firmware major version

				if("v0" in deviceType):
					# Define available commands

					self.command = {
					}

					# Define available requests
					
					self.request = {
						'device_type':	[0x20, 14],
						'device_status': [0x21, 4]
					}

					match self.address:
						case 0x0B:
							# Kitchen & Dining Room
							self.pairedLightSWIDs = ['ls_1', 'ls_3']
						case 0x0C:
							# Bedroom
							self.pairedLightSWIDs = ['ls_2']
						case 0x0D:
							# Bathroom
							self.pairedLightSWIDs = ['ls_4']
						case _:
							self.pairedLightSWIDs = []

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
					 	- 0 - 'close' / 1 - 'open'
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
						print(f'Invalid response from {self.name} device')

					# Initialize local variables for tracking
					# Initial state is case '0' (0b0000)
					greyValve = 'tank_valve_close'
					greyHeat = 'tank_heat_auto'
					showerFan = 'fan_auto'
					waterPump = 'water_pump_off'

					# Check bit status by applying bit mask
					if((1 & responseInt) == 1):
						greyValve = 'tank_valve_open'

					if((2 & responseInt) == 2):
						greyHeat = 'tank_heat_off'

					if((4 & responseInt) == 4):
						showerFan = 'fan_off'

					if((8 & responseInt) == 8):
						waterPump = 'water_pump_auto'

					# Error check function
	 				# Note: As button functionality is added for other switches in this device, add to the statements below. Any errors should result in an increment in the error count.
					if(
						app.root.ids['ws_pump_switch'].value != waterPump or
						app.root.ids['shower_fan_switch'].value != showerFan or
						app.root.ids['tank_heater_switch'].value != greyHeat or
						app.root.ids['tank_valve_switch'].value != greyValve
					):
						# Increment error count
						self.errorCount += 1

						# Attempt to fix issues 10x before throwing error - these lines will toggle the current value of each switch and then trigger an on_state function activation
						app.root.ids['ws_pump_switch'].value = 'water_pump_auto' if app.root.ids['ws_pump_switch'] == 'water_pump_off' else 'water_pump_off'
						app.root.ids['ws_pump_switch'].state = 'normal'

						app.root.ids['shower_fan_switch'].value = 'shower_fan_auto' if app.root.ids['shower_fan_switch'] == 'shower_fan_off' else 'shower_fan_off'
						app.root.ids['shower_fan_switch'].state = 'normal'

						app.root.ids['tank_heater_switch'].value = 'tank_heater_auto' if app.root.ids['tank_heater_switch'] == 'tank_heater_off' else 'tank_heater_off'
						app.root.ids['tank_heater_switch'].state = 'normal'

						app.root.ids['tank_valve_switch'].value = 'tank_valve_open' if app.root.ids['tank_valve_switch'] == 'tank_valve_close' else 'tank_valve_close'
						app.root.ids['tank_valve_switch'].state = 'normal'

						# Revert GUI to match the device settings and alert user
						if(self.errorCount == 10):
							self.errorCount = 0

							# Change the switch position to match the detected state of the board. The value will be switched to the opposite of the value of the board, then a state change will call the 'toggle' functionality of the button and cause it to switch states.
							app.root.ids['ws_pump_switch'].value = 'water_pump_auto' if waterPump == 'water_pump_off' else 'water_pump_auto'
							app.root.ids['ws_pump_switch'].state = 'normal'

							app.root.ids['shower_fan_switch'].value = 'shower_fan_auto' if showerFan == 'shower_fan_off' else 'shower_fan_off'
							app.root.ids['shower_fan_switch'].state = 'normal'

							app.root.ids['tank_heater_switch'].value = 'tank_heater_auto' if greyHeat == 'tank_heater_off' else 'tank_heater_off'
							app.root.ids['tank_heater_switch'].state = 'normal'

							app.root.ids['tank_valve_switch'].value = 'tank_valve_open' if greyValve == 'tank_valve_close' else 'tank_valve_close'
							app.root.ids['tank_valve_switch'].state = 'normal'

							app.generalError_dialog(
								f'Communication issue with {self.name} device detected. All buttons have been reverted to match state of device.'
							)
					else:
						self.errorCount = 0

					print(waterPump, showerFan, greyHeat, greyValve)
					
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
					'''
					temp_b100_v010 has no plottable features - i.e. there is no need for a self.readout.

					temp_b100_v010 readout will simply confirm the button position with the state of the device and throw a flag if the device is commanding an action not commanded by the user and vice versa.

					This version of the board has the following pinout:
					 - Digital Pin 9 / PB1 - Heat pump
					 	- 0 - 'off' / 1 - 'on'
					 - Digital Pin 10 / PB2 - AC pump
					 	- 0 - 'off' / 1 - 'on'
					 - Digital Pin 11 / PB3 - Fan (high)
					 	- 0 - 'off' / 1 - 'on'
					 - Digital Pin 12 / PB4 - Fan (low)
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
						print(f'Invalid response from {self.name} device')

					# Initialize local variables for tracking
					# Initial state is case '0' (0b0000)
					greyValve = 'tank_valve_close'
					greyHeat = 'tank_heat_auto'
					showerFan = 'fan_auto'
					waterPump = 'water_pump_off'

					# Check bit status by applying bit mask
					if((1 & responseInt) == 1):
						greyValve = 'tank_valve_open'

					if((2 & responseInt) == 2):
						greyHeat = 'tank_heat_off'

					if((4 & responseInt) == 4):
						showerFan = 'fan_off'

					if((8 & responseInt) == 8):
						waterPump = 'water_pump_auto'

					# Error check function
	 				# Note: As button functionality is added for other switches in this device, add to the statements below. Any errors should result in an increment in the error count.
					if(
						app.root.ids['ws_pump_switch'].value != waterPump
					):
						# Increment error count
						self.errorCount += 1

						# Attempt to fix issues 10x before throwing error (this line will change the GUI state of the toggle and trigger the 'on_state' function)
						app.root.ids['ws_pump_switch'].state = 'down' if waterPump == 'water_pump_auto' else 'normal'

						# Revert GUI to match the device settings and alert user
						if(self.errorCount == 10):
							self.errorCount = 0
							app.root.ids['ws_pump_switch'].state = 'down' if waterPump == 'water_pump_auto' else 'normal'

							app.generalError_dialog(
								f'Communication issue with {self.name} device detected. All buttons have been reverted to match state of device.'
							)
					else:
						self.errorCount = 0

		# --- LIGHT SWITCH & THERMOMETER ---
		if('ltsw' in self.type):
		# Choose PCB version
		
			if("b100" in self.type):
				# Choose firmware major version

				if("v0" in self.type):
				
					'''
					ltsw_b100_v010 has one plottable feature - the temperature output. self.readout will store this value.

					ltsw_b100_v010 readout will also send current light status. The makeup of the data exchange are below.

					response = [byte_1, byte_2, byte_3, byte_4]
						- byte_1:	lightOn -- 0 - off / 1 - on / else - maintain current state
						- byte_2:	lightChange - # of pulses generated since last transmission // a signed char value (2's complement) where a negative value should cause a decrease in light intensity and a positive value should cause an increase in light intensity
						- byte_3:	thermometerOutput (MSB)
									x x x x x x bit_9 bit_8
						- byte_4:	thermometerOutput (LSB)
									bit_7 bit_6 bit_5 bit_4 bit_3 bit_2 bit_1 bit_0
					'''
					
					lightOn = None
					lightChange = None
					thermometerOutput = None

					try:
						lightOn = int(response[0])
						lightChange = self.twosComplement2Int(response[1])
						thermometerOutput = (response[2] << 8) + response[3]

					except:
						print(f'Invalid response from {self.name} device')

					# Check and change status
					if(lightOn != None):
						for id in self.pairedLightSWIDs:
							app.root.ids[f'{id}_switch'].state = 'down' if lightOn == 1 else 'normal'

					if(lightChange != None):
						for id in self.pairedLightSWIDs:

							prevValue = int(app.root.ids[f'{id}_switch'].value)
							newValue = prevValue + lightChange
							app.root.ids[f'{id}_switch'].value = newValue

							app.lightingAdjust('', newValue, f'{id}_slider')

					if(thermometerOutput != None):
						# Fills readout with kelvin values
						self.readout[requestTime] = -0.0962*thermometerOutput + 344.25
						del self.readout[list(self.readout.keys())[0]]

						self.errorCount = 0

					else:
						self.errorCount += 1

						# Revert GUI to match the device settings and alert user
						if(self.errorCount == 10):
							self.errorCount = 0
							app.generalError_dialog(
								f'Communication issue with {self.name} device detected. Light switch and thermostat functionality may be limited.'
							)
						
	
	def twosComplement2Int(self, value):
		'''
		Convert a signed char value (8-bit, 2's complement value) to int
		'''
		if(value >= 128 and value <= 255):
			value -= 1
			value = value ^ 0b11111111
			return -int(value)
		elif(value >= 0 and value <= 127):
			return int(value)
		else:
			raise ArithmeticError('Argument must be a signed char (8-bit) value.')

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
			elif 'ltsw' in deviceType:
				self.activeDevices[f'light_switch_{deviceAddress[deviceType]}']
			elif 'temp' in deviceType:
				self.activeDevices['thermostat'] = Device('thermostat', deviceType, deviceAddress[deviceType])

		print(self.activeDevices)

	def send(self, msgType: str, addr: int, message: int):
		# Channel through which all commands and requests should be sent outside of the initial scan for active devicess
		#
		# Parameters:
		# - msgType - 'request' or 'command'
		# - addr - Device().address
		# - message - Device().command['x_command'] or Device().request('')
		print(f'Command sent: {addr} // {message}')
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