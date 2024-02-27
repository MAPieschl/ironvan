import ironVan_bus as i2c

def main():
	bus = i2c.Bus()
	bus.sendCommandCLI()
		
if __name__ == "__main__":  main()
