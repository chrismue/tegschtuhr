from micropython import const

SUNNY = const(0)
CLOUDY = const(1)
RAINY = const(2)
SNOWY = const(3)

global cfg

import os

try: 
    cfg
    print("-----FOUND CFG!!!!")
except NameError:
    print("-----NEW CFG")
    try:
        with open("cfg", "r") as f:
            cfg = eval(f.read())
    except OSError:
        cfg = {"lat": 46.98457,
               "lon": 8.30702,
               "foreindex": 4,
               "ap_id": "b7b444cf2b2026989fe60b68b32ff926",
               "min_level": 15,
               "min_lum": 15,
               "max_level": 15,
               "max_lum": 100,
               "custom_pos": [[1,3], [4,8], [1,2]],
               "timeout": 20000,
               "debug": False}

def store_config(lat, lon, foreindex, ap_id,
                 min_level, min_lum, max_level, max_lum,
                 custom_pos, 
                 timeout, debug):
    global cfg
    cfg = {"lat": lat, 
           "lon": lon, 
           "foreindex": foreindex, 
           "ap_id": ap_id,
           "min_level": min_level,
           "min_lum": min_lum,
           "max_level": max_level,
           "max_lum": max_lum,
           "custom_pos": custom_pos,
           "timeout": timeout, 
           "debug": debug}
      
    with open("cfg", "w") as f:
        f.write(str(cfg))

def get_luminance_cfg():
    return cfg["min_level"], cfg["min_lum"], cfg["max_level"], cfg["max_lum"]

def get_weather_cfg():
    return cfg["lat"], cfg["lon"], cfg["foreindex"], cfg["ap_id"]

def get_config():
    return cfg