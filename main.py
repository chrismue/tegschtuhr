from captive_portal import CaptivePortal

import time
import machine
from machine import I2C, Pin

from leddriver import Max7219Chain
from textmatrix import TextFinder
from lightsensor import BH1750
from touch import TouchSensor
from localtime import LocalTime
from ambient import BME280
from weather import Weather

CURRENT_MODE = 0  # 0: Time, 1: Temperature, 2: Humidity
MODE_TIMEOUTSTAMPSTAMP = 0
MODE_TIMEOUT_MS = 20000 # cfg.mode_timeout

#Initialize Hardware
matrix = Max7219Chain(1, cs_pinnr=27, sck_pinnr=14, mosi_pinnr=13, miso_pinnr=12)
supply_sensoren = Pin(33, Pin.OUT)
supply_sensoren.on()
textfinder = TextFinder()
i2c = I2C(1, scl=Pin(25), sda=Pin(26), freq=100000)
mytime = LocalTime(i2c)
lightsensor = BH1750(i2c)

DEBUG_MODE = True

if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print("Woke from deep sleep...")
else:
    mytime.sync_from_external_RTC()
    # portal = CaptivePortal()
    # portal.start()

def mode_switch():
    global CURRENT_MODE, MODE_TIMEOUTSTAMP
    print("Mode Switch!", CURRENT_MODE)
    positions=[]
    if CURRENT_MODE == 0:
        positions = textfinder.get_temperature_positions(ambient.temperature)
    elif CURRENT_MODE == 1:
        positions = textfinder.get_humidity_positions(ambient.humidity)
    elif CURRENT_MODE == 2:
        positions = textfinder.get_date_positions(*(mytime.date))
    elif CURRENT_MODE == 3:
        positions = [[0,0], [2, 8], [6,5], [7, 4], [8,0]]  # B R U N O
    elif CURRENT_MODE == 4:
        positions = textfinder.get_temperature_positions(weather.current_temp)
    elif CURRENT_MODE == 5:
        positions = textfinder.get_temperature_positions(weather.forecast_temp)
    elif CURRENT_MODE == 6:
        positions = textfinder.get_weather_positions(weather.forecast_icon)
    elif CURRENT_MODE == 7:
        for y in range(14):
            positions += [[x,y] for x in range(12)]
    matrix.show_pixels(positions)
    if CURRENT_MODE < 7:
        CURRENT_MODE = CURRENT_MODE + 1
    else: 
        CURRENT_MODE = 0
    
    MODE_TIMEOUTSTAMP = time.ticks_ms() + MODE_TIMEOUT_MS

touchsensor = TouchSensor(32, mode_switch)
touch_is_pressed = touchsensor.is_pressed()
if touchsensor.is_pressed():
    ambient = BME280(i2c)
    weather = Weather()

    mode_switch()

    portal = CaptivePortal()
    portal.start()
    time_synced = False
    weather_synced = False

    while time.ticks_ms() < MODE_TIMEOUTSTAMP:
        if not time_synced:
            if mytime.sync_from_ntp():
                print("Time Synched over NTP")
                time_synced = True
            else:
                print("Failed to Sync Time over NTP")
        if not weather_synced:
            if weather.update():
                print("Weather Updated.")
                weather_synced = True
            else:
                print("Failed to Sync Weather.")
        time.sleep(0.3)
        
h, m = mytime.time
print("Finding", h, ":", m)
positions = textfinder.get_time_positions(h,m)
matrix.set_brightness(lightsensor.get_light_level())
matrix.show_pixels(positions)
CURRENT_MODE = 0

if False and m % 5 == 0: # TODO
    rtc_sync_successful = mytime.sync_from_external_RTC()
    if not rtc_sync_successful:
        portal = CaptivePortal()
        if portal.connect_to_wifi():
            connected_time = time.ticks_ms()
            synced_once = False
            while not synced_once and time.ticks_ms() < connected_time + 10000:
                if mytime.sync_from_ntp():
                    print("Time Synched over NTP")
                    synced_once = True
                else:
                    print("Failed to Sync Time over NTP")
                time.sleep(0.3)


# sleep until next minute
touchsensor.configure_for_wakeup()
sleep_time = max(0.1, mytime.seconds_to_next_minute - 2)  # subtract 1 second for boot up
if not DEBUG_MODE:
    print("deep-sleeping at", h, ":", m, "; sleeping", sleep_time)
    supply_sensoren.off()
    # TODO: machine.deepsleep(int(sleep_time * 1000))  # deepsleep uses milliseconds
