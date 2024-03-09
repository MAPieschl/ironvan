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
    def __init__(self, bus, log):

        # ---- State variables ----

        # Fresh Water Level (left / driver-side tank):  (0 - 100) (%)
        self.freshLevelLeft = None

        # Fresh Water Level 

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