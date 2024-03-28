'''
Water System Status and Command Structure

Status:
    - This module maintains the status of all water-related sensors and controls. Status updates are commanded in ironVan_bus.Bus() and values are passed to the WaterSystem object instantiated in ironVan_main.py.

Commands:
    - All commands are sent to devices via the ironVan_bus.Bus() object instantiated in ironVan_main.py.

API:

    WaterSystem()
        .freshLevelLeft -    returns float value 0 - 100            defaults to None
        .freshLevelRight -   returns float value 0 - 100            defaults to None
        .greyLevel -         returns float value 0 - 100            defaults to None
        .greyHeat -          returns string value 'auto' / 'off'    defaults to None
        .greyHeatPower -     returns float value 0 - 100            defaults to None
        .greyValve -         returns string value 'open' / 'close'  defaults to None
        .waterHeat -         returns string value 'auto' / 'off'    defaults to None
        .waterHeatPower -    returns flaot value                    defaults to None
        .waterPump -         returns string value 'auto' / 'off'    defaults to None
        .waterPumpPower -    returns float value                    defaults to None

    BEMUSystem()

    LightingSystem()
'''

class WaterSystem():
    def __init__(self):
        '''
        To fully utilize the WaterSystem class, the following LRUs are required:
        - Utilities - incl. fresh water pump, greay water valve, and grey water heat control and monitoring
        - MeterSW120V - for the water heater
        - WaterLevel - for each fresh water tank and grey water tank

        The values stored in this class are read directly from the LRUs and are a means to detect faults in the system (comparing the values stored here with switch positions in the UI)
        '''

        # Fresh Water Level (left / driver-side tank):  (0 - 100) (%)
        self.freshLevelLeft = None

        # Fresh Water Level (right / passenger-side tank):  (0 - 100) (%)
        self.freshLevelRight = None

        # Grey Level:  (0 - 100) (%)
        self.greyLevel = None

        # Grey Water Heater Status: 'auto' / 'off'
        self.greyHeat = None

        # Grey Water Heater Current Power: float
        self.greyHeatPower = None

        # Grey Water Valve Status: 'open' / 'close'
        self.greyValve = None

        # Water Heater Status: 'auto' / 'off'
        self.waterHeat = None

        # Water Heater Current Power: float
        self.waterHeatPower = None

        # Water Pump Status: 'auto' / 'off'
        self.waterPump = None

        # Water Pump Power Consumption: float
        self.waterPumpPower = None

class BEMUSystem():
    def __init__(self):
        return

class LightingSystem():
    def __init__(self):
        return