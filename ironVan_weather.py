from datetime import datetime, date
from functools import partial
from kivy.clock import Clock
import requests
import json
import time

class Location():
    def __init__(self):
        self.weather = Weather()
        self.api_key = 'ipb_live_FKgcNeSzddarJZyyDS22NSgfNaEtFR7lf0tx4SRM'
        self.base_url = 'https://api.ipbase.com/v2/info?apikey=ipb_live_FKgcNeSzddarJZyyDS22NSgfNaEtFR7lf0tx4SRM&ip'

    def startThreadScheduler(self, app):
        # Initial location and weather grab
        self.getLocation(app)

        # Schedule future location & weather updates
        self.threadScheduler = Clock.schedule_interval(partial(self.getLocation, app), 600)

    def getLocation(self, app, *args):
        print(args)

        publicIP = self.getPublicIP(app)
        self.current_url = f'{self.base_url}={publicIP}'
        
        try:
            rawResponse = requests.get(self.current_url)
            response = rawResponse.json()

            # self.latitude = float(response.get('data').get('location').get('latitude'))
            # self.longitude = float(response.get('data').get('location').get('longitude'))
            # self.timezone = response.get('data').get('timezone').get('id')

            self.latitude = 39.84
            self.longitude = -84.05
            self.timezone = '-4:00'
            print('ipify location services skipped for testing -- reconfigure in weather.getLocation()')
            print(f'Location is hardcoded as {self.latitude}, {self.longitude}, {self.timezone}')

            self.weather.getWeather(app)
            
        except:
            app.write2MessageBuffer(f"locationServices_{time.strftime('%Y-%m-%d_%H:%M:%S', time.gmtime())}", f"No location data received -- check WiFi connection.", "error")
            return
        
    def getPublicIP(self, app):
        try:
            # response = requests.get('https://api.ipify.org')
            # publicIP = response.text.strip()
            publicIP = '192.168.1.3'
            print('ipify request skipped for testing -- reconfigure in weather.getPublicIP()')
            print(f'IP address hardcoded as {publicIP}')
            return publicIP
        except:
            app.write2MessageBuffer(f"requestIP_{time.strftime('%Y-%m-%d_%H:%M:%S', time.gmtime())}", f"IP address could not be determined. Default IP set - 1.1.1.1", "error")
            return '1.1.1.1'

class Weather():
    def __init__(self):
        self.api_key = 'd7cb298cf0dc3ac284d33e3571ade470'
        self.base_current_url = 'http://api.openweathermap.org/data/2.5/weather?'
        self.base_forecast_url = 'http://api.openweathermap.org/data/2.5/forecast?'

        # Values stored for settings modification
        self.sunrise = ''
        self.sunset = ''
        
    def getWeather(self, *args):
        app = args[0]
        userSettings = app.userSettings

        currentTemp = '--'
        minTemp = '--'
        maxTemp = '--'
        location = ''
        
        try:
            self.current_url = self.base_current_url + '&lat=' + str(app.location.latitude) + '&lon=' + str(app.location.longitude) +'&appid=' + self.api_key
            
            rawResponse = requests.get(self.current_url)
            currentResponse = rawResponse.json()
            
            self.forecast_url = self.base_forecast_url + '&lat=' + str(app.location.latitude) + '&lon=' + str(app.location.longitude) + '&appid=' + self.api_key
            
            rawResponse = requests.get(self.forecast_url)
            forecastResponse = rawResponse.json()
            
        except:
            app.write2MessageBuffer(f"weatherServices_{time.strftime('%Y-%m-%d_%H:%M:%S', time.gmtime())}", f"No weather data received -- check WiFi connection.", "error")
            return
        
        # Extract and print current weather
        try:
            iconName = currentResponse.get('weather')[0].get('icon')
            iconURL = f'https://openweathermap.org/img/wn/{iconName}@2x.png'
            currentTemp = userSettings.kelvinTo(int(currentResponse.get('main').get('temp')), userSettings.tempCelsius)
            minTemp = userSettings.kelvinTo(int(currentResponse.get('main').get('temp_min')), userSettings.tempCelsius)
            maxTemp = userSettings.kelvinTo(int(currentResponse.get('main').get('temp_max')), userSettings.tempCelsius)
            location = currentResponse.get('name')
            
            self.sunrise = int(currentResponse.get('sys').get('sunrise'))
            self.sunset = int(currentResponse.get('sys').get('sunset'))

            if(len(location) > 12):
                location = location[:11] + '...'

        except:
            app.write2MessageBuffer(f"weatherServices_{time.strftime('%Y-%m-%d_%H:%M:%S', time.gmtime())}", f"Weather data received - error extracting data.", "error")

        # Extract and print forecasted weather
        
        # forecastList = {'%m/%d': DailyForecast}
        forecastList = {}
        try:
            for forecast in forecastResponse.get('list'):
                systemDate = datetime.fromtimestamp(forecast.get('dt')).strftime('%m/%d')

                if systemDate in forecastList:
                    forecastList[systemDate].addData(forecast, userSettings)
                else:
                    forecastList[systemDate] = DailyForecast(forecast, userSettings)

        except:
            app.write2MessageBuffer(f"weatherServices_{time.strftime('%Y-%m-%d_%H:%M:%S', time.gmtime())}", f"Forecast data received - error extracting data.", "error")

        app.root.ids['outside_temp_quick_label'].text = f'{currentTemp}' + u'\N{DEGREE SIGN}'
        app.root.ids['weather_icon'].source = iconURL
        app.root.ids['location_label'].text = f"{'in': ^22}\n{location: ^20}"

        try:
            newLow = 1000
            for timeIterator in forecastList[date.today().strftime('%m/%d')].hourlyData.keys():
                temp = forecastList[date.today().strftime('%m/%d')].hourlyData[timeIterator]['temp_min']
                if(int(temp) < newLow):
                    newLow = int(temp)
            
            if(newLow < minTemp):
                minTemp = newLow
            
            newHigh = -1000
            for timeIterator in forecastList[date.today().strftime('%m/%d')].hourlyData.keys():
                temp = forecastList[date.today().strftime('%m/%d')].hourlyData[timeIterator]['temp_max']
                if(int(temp) > newHigh):
                    newHigh = int(temp)
            
            if(newHigh > maxTemp):
                maxTemp = newHigh

            # Convert temp to user units -- API not outputting Kelvin as expected - stuck in Fahrenheit
            #minTemp = userSettings.kelvinTo(newLow, userSettings.tempCelsius)
            #maxTemp = userSettings.kelvinTo(newHigh, userSettings.tempCelsius)

            app.root.ids['low_temp_quick_label'].text = f'{minTemp}' + u'\N{DEGREE SIGN}'
            app.root.ids['high_temp_quick_label'].text = f'{maxTemp}' + u'\N{DEGREE SIGN}'

        except:
            app.write2MessageBuffer(f"weatherServices_{time.strftime('%Y-%m-%d_%H:%M:%S', time.gmtime())}", f"Could not extract min/max temperature from weather data.", "error")

            app.root.ids['low_temp_quick_label'].text = f'--' + u'\N{DEGREE SIGN}'
            app.root.ids['high_temp_quick_label'].text = f'--' + u'\N{DEGREE SIGN}'

class DailyForecast():
    def __init__(self, forecast, userSettings):
        self.date = datetime.fromtimestamp(forecast.get('dt')).strftime('%A, %B %d')
        self.minTemp = None
        self.maxTemp = None
        self.hourlyData = {}
        
        self.addData(forecast, userSettings)

    def addData(self, forecast, userSettings):
        self.hourlyData[datetime.fromtimestamp(forecast.get('dt')).strftime('%H:%M') if userSettings.time24hr == True else datetime.fromtimestamp(forecast.get('dt')).strftime('%I:%M %p')] = {
            'temp': userSettings.kelvinTo(float(forecast.get('main').get('temp')), userSettings.tempCelsius),

            'temp_max': userSettings.kelvinTo(float(forecast.get('main').get('temp_max')), userSettings.tempCelsius),

            'temp_min': userSettings.kelvinTo(float(forecast.get('main').get('temp_min')), userSettings.tempCelsius),

            'icon': forecast.get('weather')[0]['icon'],
            'clouds': forecast.get('clouds').get('all')
        }