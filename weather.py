from micropython import const
import urequests
from common import SUNNY, CLOUDY, RAINY, SNOWY

# https://openweathermap.org/weather-conditions#How-to-get-icon-URL
"""
Day    Night    Description
01d    01n      clear sky
02d    02n      few clouds
03d    03n      scattered clouds
04d    04n      broken clouds
09d    09n      shower rain
10d    10n      rain
11d    11n      thunderstorm
13d    13n      snow
50d    50n      mist 
"""
icons = {"01": SUNNY,
         "02": SUNNY,
         "03": CLOUDY,
         "04": CLOUDY,
         "09": RAINY,
         "10": RAINY,
         "11": RAINY,
         "13": SNOWY,
         "50": CLOUDY}


class Weather:
    def __init__(self, lat=46.98457, lon=8.30702, appid="<YOUR_APPID>", forecast_index = 4):
        self._url = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&units=metric&exclude=minutely,daily&appid={}".format(lat, lon, appid)
        self._forecast_index = forecast_index
        self.current_temp = 0.0
        self.forecast_temp = 0.0
        self.forecast_index = SUNNY

    def update(self):
        try:
            resp = urequests.get(self._url)
            data = resp.json()
            self.current_temp = data["current"]["temp"]
            self.forecast_temp = data["hourly"][self._forecast_index]["temp"]
            icon = ["hourly"][self._forecast_index]["weather"][0]["icon"]
            self.forecast_index = icons[icon[:2]]
            return True
        except:
            return False
