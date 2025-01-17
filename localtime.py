from externalrtc import DS1307
from machine import RTC
import ntptime
import utime

class LocalTime:
    def __init__(self, i2c):
        self._external_rtc = DS1307(i2c)
        self._internal_rtc = RTC()

    def sync_from_external_RTC(self):
        try:
            self._internal_rtc.datetime(self._external_rtc.datetime())
            return True
        except:
            print("Failed to get time from ext. RTC")
            return False

    def sync_from_ntp(self):
        try:
            ntptime.settime()
        except:
            return False
        try:
            self._external_rtc.datetime(self._internal_rtc.datetime())
        except:
            print("Failed to set NTP time in external RTC")
            pass
        return True

    @property
    def local_datetime(self):
        y, mo, d, wd, h, mi, s, _ = self._internal_rtc.datetime()
        y = max(y, 2000)  # micropython 19.1 starts with Year 2000
        y, mo, d, h, mi, s, wd, yd = utime.localtime(utime.mktime((y, mo, d, h, mi, s, wd, 0)) + 3600 + 3600*self.daylight_saving(mo, d, wd, h))
        return mo, d, h, mi

    @property
    def time(self):
        _, _, h, m = self.local_datetime
        return h, m

    @property
    def seconds_to_next_minute(self):
        _, _, _, _, _, _, s, us = self._internal_rtc.datetime()
        return 60 - (s + (us/1000000))

    @property
    def date(self):
        month, day, _, _ = self.local_datetime
        return day, month


    @staticmethod
    def daylight_saving(month, day, weekday, hour):
        # Daylight saving after last sonday of march and before last Sunday of Oct
        if 3 < month < 10:
            return True
        elif month == 3:
            if weekday == 6 and day >= 25 and hour >= 1:
                return True
            elif day + 6 - weekday > 31:  # next sunday is April
                # We're in the last week of march, after daylight saving change
                return True
        elif month == 10:
            # Change of daylight saving: +2 to +1 at 3am local on last sunday
            if day - ((weekday + 1) % 7) <= 24:
                # We're now in the beginning of october
                return True
            elif weekday == 6 and day >= 25 and hour < 1:
                # on the last sunday: check if its before 1am
                return True
        return False
