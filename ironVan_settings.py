

class UserSettings():
    def __init__(self):
        # True -> temperautre displayed in celsius // False -> temperature displayed in fahrenheit
        self.tempCelsius = None

        # True -> display time in a 24 hour format // False -> display time in a 12 hour format with associated 'am' or 'pm' value
        self.time24hr = None

        # Default daytime brightness
        self.dayBright = 64

        # Default nighttime brightness
        self.nightBright = 12

        # Offset all automatic brightness adjustments by brightnessOffset
        self.brightnessOffset = 0

        # True - daytime / False - nighttime
        self.daytime = True

    def initUserSettings(self, *args):
        app = args[0]

        app.root.ids['fahrenheit_toggle'].state = 'down'
        app.root.ids['celsius_toggle'].state = 'normal'
        app.root.ids['hour24_toggle'].state = 'down'
        app.root.ids['hour12_toggle'].state = 'normal'

    def kelvinTo(self, kelvin, isCelsius):
        temperature = None
        match isCelsius:
            case True:
                temperature = kelvin - 273.15

            case False:
                temperature = (9/5)*(kelvin - 273.15) + 32

        return int(temperature)