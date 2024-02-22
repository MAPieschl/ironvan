from smbus2 import SMBus

class Bus:
	def __init__(self):
		self.bus = SMBus(1)
		
		for addr in range(0x03, 0x77):
			try:
				# Request module type from address (addr)
				moduleType = self.bus.read_byte_data(addr, 0)
				print("Device found at address: ", addr)
			except:
				continue	
				
	def sendCommand(self):
		while(True):
			addr = int(input("Address: "))
			cmd = int(input("Command: "))
			self.bus.write_byte_data(addr, 0, cmd)
