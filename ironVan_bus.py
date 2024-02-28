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

class Device:
	def __init__(self, deviceType: str):
		if('util' in deviceType):
			self.status = super.utilComm(deviceType, 'request_status')

class Bus:
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

				# Store device type defined by address if found
				self.deviceAddress[deviceType] = addr
				
			except:
				continue	

		print("Devices found on bus: ", self.deviceAddress)
		print("Initializing devices...")

		for deviceType in self.deviceAddress:
			deviceName = input(f"A device of type {deviceType} was found at address {self.deviceAddress[deviceType]}. What would you like to name this device? ... ")
			self.storedDevices[deviceName] = super.Devices()
		
		print(self.storedDevices)
				
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

		if("util" in deviceType):
			self.utilComm(deviceType, cmd)

		return
	
	def rawMsg2Str(self, msg):
		# Store the raw message in a list as integers representing ASCII values, then 
		charList = list(msg)
		
		outputStr = ''
		
		for x in charList:
			outputStr += chr(x)
			
		return outputStr
	
	## --- Device Specific Commands -> Routed from self.sendCommand() --- ##

	def utilComm(self, deviceType: str, cmd):

		# Structure first deliniates between PCB version, then firmware version
		if("b100" in deviceType):
			# PCB version 1.0.0

			if("v010" in deviceType):
				# Commands:
				#
				# - Water Pump
				# -- 0x00 - ON		- 'water_pump_on'
				# -- 0x01 - OFF		- 'water_pump_off'
				#
				# - Shower & Toilet Fan
				# -- 0x02 - AUTO	- 'fan_auto'
				# -- 0x03 - OFF		- 'fan_off'
				#
				# - Grey Water Tank Heater
				# -- 0x04 - AUTO	- 'grey_tank_heater_auto'
				# -- 0x05 - OFF		- 'grey_tank_heater_off'
				#
				# - Grey Water Tank Valve
				# -- 0x06 - CLOSE	- 'grey_tank_valve_close'
				# -- 0x07 - OPEN	- 'grey_tank_valve_open'
				#
				# Requests:
				# 
				# - Device Type - 'request_type' - returns util_b100_v010
				# -- Offset:  		0x20
				# -- # of Bytes:  	14
				#
				# - Pin Status - 'request_status' - returns integer value of PINB bits
				# -- Offset:		0x21
				# -- # of Bytes:	1

				match cmd:
					# Commands

					case 'water_pump_on':
						self.bus.write_byte_data(self.devices[deviceType], 0, 0x00)
						
					case 'water_pump_off':
						self.bus.write_byte_data(self.devices[deviceType], 0, 0x01)
						
					case 'fan_auto':
						self.bus.write_byte_data(self.devices[deviceType], 0, 0x02)

					case 'fan_off':
						self.bus.write_byte_data(self.devices[deviceType], 0, 0x03)

					case 'grey_tank_heater_auto':
						self.bus.write_byte_data(self.devices[deviceType], 0, 0x04)

					case 'grey_tank_heater_off':
						self.bus.write_byte_data(self.devices[deviceType], 0, 0x05)

					case 'grey_tank_valve_close':
						self.bus.write_byte_data(self.devices[deviceType], 0, 0x06)

					case 'grey_tank_valve_open':
						self.bus.write_byte_data(self.devices[deviceType], 0, 0x07)

					# Requests
						
					case 'request_device_type':
						msg = self.bus.read_i2c_block_data(self.devices[deviceType], 0x20, 14)

					case 'request_status':
						msg = self.bus.read_i2c_block_data(self.devices[deviceType], 0x21, 1)

						match 

					case _:

