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

from common import get_main_cfg, get_custompos_cfg

CURRENT_MODE = 0  # 0: Time, 1: Temperature, 2: Humidity
mode_timeoutstamp = 0
DEBUG_MODE, MODE_TIMEOUT_MS = get_main_cfg()

# import credentials
# credentials.Creds().remove()

def update_timeout():
    global mode_timeoutstamp
    mode_timeoutstamp = time.ticks_ms() + MODE_TIMEOUT_MS

#Initialize Hardware
matrix = Max7219Chain(1, cs_pinnr=27, sck_pinnr=14, mosi_pinnr=13, miso_pinnr=12)
i2c = I2C(1, scl=Pin(25, pull=Pin.PULL_UP), sda=Pin(26, pull=Pin.PULL_UP), freq=100000)
supply_sensoren = Pin(33, Pin.OUT)
supply_sensoren.on()
textfinder = TextFinder()
mytime = LocalTime(i2c)
lightsensor = BH1750(i2c)

if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print("Woke from deep sleep...")
else:
    mytime.sync_from_external_RTC()

def get_measurements_for_web():
    return ambient.temperature, ambient.humidity, ambient.pressure, lightsensor.luminance()

def mode_switch():
    global CURRENT_MODE
    update_timeout()

    print("Mode Switch!", CURRENT_MODE)
    positions=[]
    if CURRENT_MODE == 0:
        positions = textfinder.get_temperature_positions(ambient.temperature)
    elif CURRENT_MODE == 1:
        positions = textfinder.get_humidity_positions(ambient.humidity)
    elif CURRENT_MODE == 2:
        positions = textfinder.get_luminance_position(lightsensor.luminance())
    elif CURRENT_MODE == 3:
        positions = textfinder.get_date_positions(*(mytime.date))
    elif CURRENT_MODE == 4:
        positions = get_custompos_cfg()
    elif weather.got_data and CURRENT_MODE == 5:
        positions = textfinder.get_temperature_positions(weather.current_temp)
    elif weather.got_data and CURRENT_MODE == 6:
        positions = textfinder.get_temperature_positions(weather.forecast_temp)
    elif weather.got_data and CURRENT_MODE == 7:
        positions = textfinder.get_weather_positions(weather.forecast_icon)
    elif (weather.got_data and CURRENT_MODE >= 8) or (not weather.got_data and CURRENT_MODE >= 5):
        for y in range(14):
            positions += [[x,y] for x in range(12)]
    matrix.show_pixels(positions)
    if (weather.got_data and CURRENT_MODE >= 8) or (not weather.got_data and CURRENT_MODE >= 5):
        CURRENT_MODE = 0
    else:
        CURRENT_MODE = CURRENT_MODE + 1

    update_timeout()

touchsensor = TouchSensor(32, mode_switch)
if DEBUG_MODE or touchsensor.is_pressed():
    try:
        ambient = BME280(i2c)
        weather = Weather()

        mode_switch()

        from captive_portal import CaptivePortal
        portal = CaptivePortal(get_measurements_for_web, matrix.set_brightness)
        if portal.start(MODE_TIMEOUT_MS):
            update_timeout()
            time_synced = False
            weather_synced = False

            while time.ticks_ms() < mode_timeoutstamp:
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
                if portal.handle_socket_events():
                    update_timeout()
    except Exception as e:
        print("Error", repr(e), "in Mode Initialisation...")

h, m = mytime.time
print("Finding", h, ":", m)
positions = textfinder.get_time_positions(h,m)
matrix.set_brightness(lightsensor.get_light_level())
matrix.show_pixels(positions)
CURRENT_MODE = 0

if m % 5 == 0:
    rtc_sync_successful = mytime.sync_from_external_RTC()
    if not rtc_sync_successful or (h==3 and m==30):  # sync over NTP once a day
        try:
            portal  # check if CaptivePortal already initialized and port in use
        except NameError:
            from captive_portal import CaptivePortal
            portal = CaptivePortal(get_measurements_for_web, matrix.set_brightness)
        if portal.try_connect_from_file():
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
    machine.deepsleep(int(sleep_time * 1000))  # deepsleep uses milliseconds
