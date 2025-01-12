"""
Micropython BH1750 ambient light sensor driver.
"""

from micropython import const
from utime import sleep_ms
import common


PWR_OFF = const(0x00)
PWR_ON = const(0x01)
RESET = const(0x07)

# modes
CONT_LOWRES = const(0x13)
CONT_HIRES_1 = const(0x10)
CONT_HIRES_2 = const(0x11)
ONCE_HIRES_1 = const(0x20)
ONCE_HIRES_2 = const(0x21)
ONCE_LOWRES = const(0x23)


class BH1750():
    """Micropython BH1750 ambient light sensor driver."""

    # default addr=0x23 if addr pin floating or pulled to ground
    # addr=0x5c if addr pin pulled high
    def __init__(self, i2cbus, addr=0x23):
        self.bus = i2cbus
        # print(self.bus)
        self.addr = addr
        try:
            self.off()
            self.reset()
            self.connected = True
        except OSError:
            self.connected = False

    def off(self):
        """Turn sensor off."""
        self.set_mode(PWR_OFF)

    def on(self):
        """Turn sensor on."""
        self.set_mode(PWR_ON)

    def reset(self):
        """Reset sensor, turn on first if required."""
        self.on()
        self.set_mode(RESET)

    def set_mode(self, mode):
        """Set sensor mode."""
        self.mode = mode
        self.bus.writeto(self.addr, bytes([self.mode]))

    def luminance(self, mode=None):
        """Sample luminance (in lux), using specified sensor mode."""
        if self.connected:
            mode = ONCE_HIRES_1 if mode is None else mode
            # continuous modes
            if mode & 0x10 and mode != self.mode:
                self.set_mode(mode)
            # one shot modes
            if mode & 0x20:
                self.set_mode(mode)
            # earlier measurements return previous reading
            sleep_ms(24 if mode in (0x13, 0x23) else 180)
            data = self.bus.readfrom(self.addr, 2)
            factor = 2.0 if mode in (0x11, 0x21) else 1.0
            return (data[0]<<8 | data[1]) / (1.2 * factor)
        else:
            return 666

    def get_light_level(self):
        if self.connected:
            min_level, min_lum, max_level, max_lum = common.get_luminance_cfg()

            if min_level == max_level:
                l = max_level
            elif min_lum == max_lum:
                l = max_level
            else:
                lum = self.luminance()
                if lum <= min_lum:
                    l = min_level
                elif lum >= max_lum:
                    l = max_level
                else:
                    l = round(min_level + (max_level - min_level) / (max_lum - min_lum) * (lum - min_lum), 0)
                # print(lum, "->", l, "(", min_level, "@", min_lum, ",", max_level, "@", max_lum, ")")
            return int(l)
        else:
            return 15
