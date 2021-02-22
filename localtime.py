from externalrtc import DS1307
from machine import RTC
import ntptime

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
    def time(self):
        _, month, day, weekday, h, m, _, _ = self._internal_rtc.datetime()
        return h + 1 + self.daylight_saving(month, day, weekday, h), m

    @property
    def seconds_to_next_minute(self):
        _, _, _, _, _, _, s, us = self._internal_rtc.datetime()
        return 60 - (s + (us/1000000))
    
    @property
    def date(self):
        _, month, day, weekday, h, _, _, _ = self._internal_rtc.datetime()
        # check if daylight saving leads to next day
        if h + 1 + self.daylight_saving(month, day, weekday, h) >= 24:
            day = day + 1
        return day, month


    @staticmethod
    def daylight_saving(month, day, weekday, hour):
        # Daylight saving after last sonday of march and before last Sunday of Oct
        if 3 < month < 10:
            return True
        elif month == 3 and day >= 31 - weekday:
            # Change of daylight saving: +1 to +2 at 2 am local
            # We're now in the last days of march, check if its before sunday 1am
            if weekday < 6 or hour >= 1:
                return True
        elif month == 10 and day <= 31 - weekday:
            # Change of daylight saving: +2 to +1 at 3am local on last sunday
            # We're now in the beginning of october, check if its before sunday 1am
            if weekday < 6 or day + weekday < 31 or hour < 1:
                return True
        return False
