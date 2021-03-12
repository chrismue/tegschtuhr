try:
    from micropython import const
except:
    const = lambda v: v

SUNNY = const(0)
CLOUDY = const(1)
RAINY = const(2)
SNOWY = const(3)

global _cfg

import os

try: 
    _cfg
except NameError:
    try:
        with open("cfg", "r") as f:
            _cfg = eval(f.read())
    except OSError:
        _cfg = {"lat": 46.98,
                "lon": 8.31,
                "foreindex": 4,
                "ap_id": "<Your OpenWeather-API-Key>",
                "min_level": 5,
                "min_lum": 0,
                "max_level": 15,
                "max_lum": 10,
                "custom_pos": [[0,0], [2, 8], [6,5], [7, 4], [8,0]],
                "timeout": 40000,
                "debug": False}

def store_config(lat, lon, foreindex, ap_id,
                 min_level, min_lum, max_level, max_lum,
                 custom_pos, 
                 timeout, debug):
    global _cfg
    _cfg = {"lat": float(lat), 
            "lon": float(lon), 
            "foreindex": int(foreindex), 
            "ap_id": str(ap_id),
            "min_level": int(min_level),
            "min_lum": int(min_lum),
            "max_level": int(max_level),
            "max_lum": int(max_lum),
            "custom_pos": custom_pos,
            "timeout": int(timeout),
            "debug": bool(debug)}
    
    with open("cfg", "w") as f:
        f.write(str(_cfg))
    print(_cfg)

def get_main_cfg():
    return _cfg["debug"], _cfg["timeout"], 

def get_luminance_cfg():
    return _cfg["min_level"], _cfg["min_lum"], _cfg["max_level"], _cfg["max_lum"]

def get_weather_cfg():
    return _cfg["lat"], _cfg["lon"], _cfg["foreindex"], _cfg["ap_id"]

def get_custompos_cfg():
    return _cfg["custom_pos"]

def get_config():
    return _cfg