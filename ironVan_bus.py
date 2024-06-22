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

from kivymd.uix.label import MDLabel

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

			self.command = {
				'water_pump_auto': [0x00],
				'water_pump_off': [0x01],
				'shower_fan_auto': [0x02],
				'shower_fan_off': [0x03],
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
			
			# Choose PCB version
			
			if("b100" in deviceType):
				# Choose firmware major version

				if("v0" in deviceType):
					# Define available commands
					
					self.command = {
						'water_pump_auto': [0x00],
						'water_pump_off': [0x01],
						'shower_fan_auto': [0x02],
						'shower_fan_off': [0x03],
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
		
			# if("b100" in deviceType):
			# 	# Choose firmware major version

			# 	if("v0" in deviceType):
			# 		# Define available commands
	 		# 		# Note:  The 'ls_n_toggle' commands are appended with a 1 byte value from either -- the toggle button (0 or current slider value) -- or -- app.lightingAdjust() (slider value)

			# 		self.command = {
			# 			'ls_1_toggle': [0x01],
			# 			'ls_2_toggle': [0x02],
			# 			'ls_3_toggle': [0x03],
			# 			'ls_4_toggle': [0x04]
			# 		}

			# 		# Define available requests
					
			# 		self.request = {
			# 			'device_type':	[0x20, 14],
			# 			'device_status': [0x21, 4]
			# 		}

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
						'device_status':  [0x21, 1]
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
						responseInt = responseInt & 0b1111
					except:
						print(f'Invalid response from {self.name} device')
						return

					# Initialize local variables for tracking
					# Initial state is case '0' (0b0000)
					greyValve = 'tank_valve_close'
					greyHeat = 'tank_heat_auto'
					showerFan = 'shower_fan_auto'
					waterPump = 'water_pump_off'

					# Check bit status by applying bit mask
					if((1 & responseInt) == 1):
						greyValve = 'tank_valve_open'

					if((2 & responseInt) == 2):
						greyHeat = 'tank_heat_off'

					if((4 & responseInt) == 4):
						showerFan = 'shower_fan_off'

					if((8 & responseInt) == 8):
						waterPump = 'water_pump_auto'

					print(f'Error check for {self}:')
					print(waterPump, '  ', app.root.ids['ws_pump_switch'].value)
					print(showerFan, '  ', app.root.ids['shower_fan_switch'].value)
					print(greyHeat, '  ', app.root.ids['tank_heater_switch'].value)
					print(greyValve, '  ', app.root.ids['tank_valve_switch'].value)

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
						self.repairSwitch(app, 'fix',
											'ws_pump_switch',
						  					'water_pump_auto',
											'water_pump_off')
						
						self.repairSwitch(app, 'fix',
											'shower_fan_switch',
						  					'shower_fan_auto',
											'shower_fan_off')
						
						self.repairSwitch(app, 'fix',
											'tank_heater_switch',
						  					'tank_heat_auto',
											'tank_heat_off')
						
						self.repairSwitch(app, 'fix',
											'tank_valve_switch',
						  					'tank_valve_open',
											'tank_valve_close')

						# Revert GUI to match the device settings and alert user
						if(self.errorCount == 10):
							self.errorCount = 0

							app.generalError_dialog(
								f'Communication issue with {self.name} device detected. All buttons have been reverted to match state of device.'
							)
					else:
						self.errorCount = 0
					
		# --- LIGHTING ---
		if('ltsy' in self.type):
		# Choose PCB version
		
			if("b100" in self.type):
				# Choose firmware major version

				if("v0" in self.type):
					
					return

		# # --- THERMOSTAT ---
		# if('temp' in self.type):
		# 	# Choose PCB version
			
		# 	if("b100" in self.type):
		# 		# Choose firmware major version

		# 		if("v0" in self.type):
		# 			'''
		# 			temp_b100_v010 has no plottable features - i.e. there is no need for a self.readout.

		# 			temp_b100_v010 readout will simply confirm the button position with the state of the device and throw a flag if the device is commanding an action not commanded by the user and vice versa.

		# 			This version of the board has the following pinout:
		# 			 - Digital Pin 9 / PB1 - Heat pump
		# 			 	- 0 - 'off' / 1 - 'on'
		# 			 - Digital Pin 10 / PB2 - AC pump
		# 			 	- 0 - 'off' / 1 - 'on'
		# 			 - Digital Pin 11 / PB3 - Fan (high)
		# 			 	- 0 - 'off' / 1 - 'on'
		# 			 - Digital Pin 12 / PB4 - Fan (low)
		# 			 	- 0 - 'off' / 1 - 'on'
						 
		# 			PINB is initially read, then isolated to a single nibble -> MSB - PB4 / LSB - PB1
		# 			'''
		# 			#self.readout[requestTime] = response
		# 			#del self.readout[list(self.readout.keys())[0]]
					
					try:
						responseInt = int(response)

						# Isolate PB1 thru PB4
						responseInt = responseInt >> 1
						responseInt = responseInt & 0b1111
					except:
						print(f'Invalid response from {self.name} device')
						return

					# Initialize local variables for tracking
					# Initial state is case '0' (0b0000)
					heatPump = 'heat_off'
					airCon = 'ac_off'
					highFan = 'fan_high_off'
					lowFan = 'fan_low_off'

					# Check bit status by applying bit mask
					if((1 & responseInt) == 1):
						heatPump = 'heat_on'

					if((2 & responseInt) == 2):
						airCon = 'ac_on'

					if((4 & responseInt) == 4):
						highFan = 'fan_high_on'

					if((8 & responseInt) == 8):
						lowFan = 'fan_low_on'

					print(f'Error check for {self}:')
					print(lowFan, '  ', app.root.ids['env_fan_quick_switch'].value)
					print(highFan, '  ', app.root.ids[
					'env_cool_quick_switch'].value, '//', app.root.ids['env_heat_quick_switch'].value)
					print(airCon, '  ', app.root.ids['env_cool_quick_switch'].value)
					print(heatPump, '  ', app.root.ids['env_heat_quick_switch'].value)

					# Error check function
	 				# Note: As button functionality is added for other switches in this device, add to the statements below. Any errors should result in an increment in the error count.
					if(
						app.root.ids['env_fan_quick_switch'].value != lowFan or
						app.root.ids['env_cool_quick_switch'].value != airCon or
						('on' in app.root.ids['env_cool_quick_switch'].value and not 'on' in highFan) or
						app.root.ids['env_heat_quick_switch'].value != heatPump or
						('on' in app.root.ids['env_heat_quick_switch'].value and not 'on' in highFan)
					):
						print('Thermostat error caught')
						# Increment error count
						self.errorCount += 1

						# Attempt to fix issues 10x before throwing error - these lines will toggle the current value of each switch and then trigger an on_state function activation
						self.repairSwitch(app, 'fix',
											'env_fan_quick_switch',
						  					'fan_low_on',
											'fan_low_off')
						
						self.repairSwitch(app, 'fix',
											'env_cool_quick_switch',
						  					'ac_on',
											'ac_off')
						
						self.repairSwitch(app, 'fix',
											'env_heat_quick_switch',
						  					'heat_on',
											'heat_off')

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

	def repairSwitch(self, app, solution: str, switchID: str, loState: str, hiState: str):
		print('Original state: ', app.root.ids[switchID].value)
		match solution:
			case 'fix':
				app.root.ids[switchID].value = hiState if app.root.ids[switchID] == loState else loState
				print('New state: ', app.root.ids[switchID].value)
				app.root.ids[switchID].on_state(app.root.ids[switchID], 'override')

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
			self.bus = ''
			print('No active bus...')
			return

		# Stores {device type: addr}
		deviceAddress = {}
		
		for addr in range(0x08, 0x0F):
			try:
				# Request device type from address (addr)

				# Request 14 char DEVICE_TYPE from each address
				deviceType = self.send('request', addr, [0x20, 14])

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
		
		if('command' in msgType):
			#self.bus.write_byte_data(addr, 0, message)
			self.bus.write_i2c_block_data(addr, 0, message)
			return 'command sent'
		
		elif('request' in msgType):
			print('Requesting...')
			msg = self.rawMsg2Str(self.bus.read_i2c_block_data(addr, message[0], message[1]))
			print('Success - ', msg)
			return msg
		
	def regularScan(self, app):
		'''
		Individual thread started in ironVanApp.build() to continuously ping devices for status updates.
		'''
		activeError = False
		while(self.bus != ''):
			time.sleep(5)
			try:
				for device in self.activeDevices.keys():
					print(self.activeDevices)
					print(self.activeDevices[device].address)
					print(self.activeDevices[device].request)
					key = f"{device}_{time.strftime('%Y-%m-%d_%H:%M:%S', time.gmtime())}"
					self.responseBuffer[key] = self.send(
						'request',
						self.activeDevices[device].address,
						self.activeDevices[device].request['device_status']
					)
					print("responseBuffer = " self.responseBuffer[key])
					success = self.write2MessageBuffer(app, key, f"{self.responseBuffer[key]}", 'normal')
					print("success = ", success)
					if(success == False):
						print(f'Timeout occured on messageBuffer - {key}')

					if(activeError == True):
						success = self.write2MessageBuffer(app, key, f"{device} reacquired at {time.strftime('%Y-%m-%d_%H:%M:%S', time.gmtime())}. Current device status: {self.responseBuffer[key]}", 'normal')
						print("1: ", success)
						if(success == False):
							print(f'Timeout occured on messageBuffer - {key}')
				
				activeError = False

			except:
				success = self.write2MessageBuffer(app, key, f"Communication lost with: {key} at {time.strftime('%Y-%m-%d_%H:%M:%S', time.gmtime())}. Attempting to reacquire device...", 'error')
				print("2: ", success)
				if(success == False):
					print(f'Timeout occured on messageBuffer - {key}')
				activeError = True
	
	async def parseResponses(self, app):
		'''
		Asynchronous function that parses and cleares in device responses acquired in regularScan. parseResponses also checks for an overloaded buffer that would indicate inadequate parsing. In this case, the function will clear the buffer and log the error to the errorLog.
		'''
		if(len(self.responseBuffer) > 100):
			self.responseBuffer.clear()
			app.messageBuffer[f'parser_{time.gmtime}'] = ['Parser overflow. Clearing buffer...', 'error']
			return
		elif(len(self.responseBuffer) < 1):
			return
		else:
			async for event in self.responseBuffer:
				divider = event.index('_')
				deviceName = event[:divider]
				requestTime = int(event[(divider + 1):])
				self.activeDevices[deviceName].updateDevice(app, requestTime, self.responseBuffer[event])

	def write2MessageBuffer(self, app, key: str, msg: str, msgType: str):
		'''
		Writes msg to the messageBuffer. Use of this function is required to protect the messageBuffer from changing sizes while being parsed.

		Returns True if the message was added successfully and False if a timeout occured
		'''
		print("Start: ", app.messageBuffer)
		timeoutStart = time.time()
		while(app.messageBufferLock == True):
			if(time.time() >= timeoutStart + 10):
				return False
			else:
				continue
		app.messageBuffer[key] = [f"Communication lost with: {key} at {time.strftime('%Y-%m-%d_%H:%M:%S', time.gmtime())}. Attempting to reacquire device...", 'error']

		print("Finish: ", app.messageBuffer)

		return True

	def rawMsg2Str(self, msg):
		# Store the raw message in a list as integers representing ASCII values, then 
		charList = list(msg)
		
		outputStr = ''
		
		for x in charList:
			if(x <= 31):
				outputStr += str(x)
			else:
				outputStr += chr(x)
			
		return outputStr