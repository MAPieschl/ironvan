from datetime import datetime
import requests
import json

class Location():
    def __init__(self):
        self.api_key = 'ipb_live_FKgcNeSzddarJZyyDS22NSgfNaEtFR7lf0tx4SRM'
        self.base_url = 'https://api.ipbase.com/v2/info?apikey=ipb_live_FKgcNeSzddarJZyyDS22NSgfNaEtFR7lf0tx4SRM&ip'

    def getLocation(self, app):

        publicIP = self.getPublicIP()
        self.current_url = f'{self.base_url}={publicIP}'

        try:
            rawResponse = requests.get(self.current_url)
            response = rawResponse.json()

            self.latitude = float(response.get('data').get('location').get('latitude'))
            self.longitude = float(response.get('data').get('location').get('longitude'))
            self.timezone = response.get('data').get('timezone').get('id')
            
        except:
            print('No location data received -- check WiFi connection.')
            return
        
    def getPublicIP(self):
        try:
            response = requests.get('https://api.ipify.org')
            publicIP = response.text.strip()
            return publicIP
        except:
            print('Could not locate current IP address.')
            return '1.1.1.1'

class Weather():
    def __init__(self):
        self.api_key = 'd7cb298cf0dc3ac284d33e3571ade470'
        self.base_current_url = 'http://api.openweathermap.org/data/2.5/weather?units=imperial'
        self.base_forecast_url = 'http://api.openweathermap.org/data/2.5/forecast?units=imperial'
        
    def getWeather(self, *args):
        app = args[0]
        
        try:
            self.current_url = self.base_current_url + '&lat=' + str(app.location.latitude) + '&lon=' + str(app.location.longitude) +'&appid=' + self.api_key

            rawResponse = requests.get(self.current_url)
            currentResponse = rawResponse.json()

            self.forecast_url = self.base_forecast_url + '&lat=' + str(app.location.latitude) + '&lon=' + str(app.location.longitude) +'&appid=' + self.api_key

            rawResponse = requests.get(self.forecast_url)
            forecastResponse = rawResponse.json()

        except:
            print('No weather data received -- check WiFi connection.')
            return

        # Extract and print current weather
        try:
            iconName = currentResponse.get('weather')[0].get('icon')
            iconURL = f'https://openweathermap.org/img/wn/{iconName}@2x.png'
            currentTemp = int(currentResponse.get('main').get('temp'))
            minTemp = int(currentResponse.get('main').get('temp_min'))
            maxTemp = int(currentResponse.get('main').get('temp_max'))

            app.root.ids['outside_temp_quick_label'].text = f'{currentTemp}' + u'\N{DEGREE SIGN}'
            app.root.ids['weather_icon'].source = iconURL
            app.root.ids['low_temp_quick_label'].text = f'{minTemp}' + u'\N{DEGREE SIGN}'
            app.root.ids['high_temp_quick_label'].text = f'{maxTemp}' + u'\N{DEGREE SIGN}'
        except:
            print('Weather data received; error extracting data.')

        # Extract and print forecasted weather
        
        # forecastList = {'%m/%d': DailyForecast}
        forecastList = {}
        try:
            for forecast in forecastResponse.get('list'):
                systemDate = datetime.fromtimestamp(forecast.get('dt')).strftime('%m/%d')

                if systemDate in forecastList:
                    forecastList[systemDate].addData(forecast)
                else:
                    forecastList[systemDate] = DailyForecast(forecast)

        except:
            print('Forecast data received; error extracting data.')
            

class DailyForecast():
    def __init__(self, forecast):
        self.date = None
        self.highTemp = None
        self.lowTemp = None
        self.icon = None

        self.addData(forecast)

    def addData(self, forecast):
        return