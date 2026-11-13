from micropython import const
import urequests
import common
import gc

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
icons = {"01": common.SUNNY,
         "02": common.SUNNY,
         "03": common.CLOUDY,
         "04": common.CLOUDY,
         "09": common.RAINY,
         "10": common.RAINY,
         "11": common.RAINY,
         "13": common.SNOWY,
         "50": common.CLOUDY}


class Weather:
    def __init__(self, lat=None, lon=None, appid=None, forecast_index=None):
        if lat is None or lon is None or appid is None or forecast_index is None:
            lat, lon, forecast_index, appid = common.get_weather_cfg()
        self.got_data = False
        self._current_url = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&units=metric&appid={}".format(lat, lon, appid)
        self._forecast_url = "http://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&units=metric&cnt={}&appid={}".format(lat, lon, forecast_index + 1, appid)
        self._forecast_index = forecast_index
        self.current_temp = 0.0
        self.forecast_temp = 0.0
        self.forecast_icon = common.SUNNY

    def update(self):
        try:
            gc.collect()
            resp = urequests.get(self._current_url)
            data = resp.json()
            resp.close()
            self.current_temp = data["main"]["temp"]
            print("Temp: ", self.current_temp)
            gc.collect()
            resp = urequests.get(self._forecast_url)
            data = resp.json()
            resp.close()
            entry = data["list"][self._forecast_index]
            self.forecast_temp = entry["main"]["temp"]
            self.forecast_icon = icons[entry["weather"][0]["icon"][:2]]
            print(self.forecast_icon)
            self.got_data = True
            return True
        except Exception as e:
            print("Weather update failed:", e)
            return False
