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

if __name__ == "__main__":
    def test_all_hours(month, day, wday, exp_value):
        for hour in range(24):
            if LocalTime.daylight_saving(month,day,wday,hour) != exp_value:
                raise AssertionError("{} {} {} {} {}".format(month, day, wday, hour, exp_value))
    def test_changes_to(month, day, wday, initial):
        if LocalTime.daylight_saving(month,day,wday,0) != initial:
            raise AssertionError("{} {} {} {} {}".format(month, day, wday, 0, initial))
        for hour in range(1,24):
            if LocalTime.daylight_saving(month,day,wday,hour) == initial:
                raise AssertionError("{} {} {} {} {}".format(month, day, wday, hour, not initial))

    for month in range(4,9):
        for day in range(1,32):
            for wday in range(7):
                test_all_hours(month, day, wday, True)
    for month in [11,12,1,2]:
        for day in range(1,32):
            for wday in range(7):
                test_all_hours(month, day, wday, False)
    
    for day in range(1,25):
        for wday in range(7):
            test_all_hours(3, day, wday, False)

    test_all_hours(3, 25, 0, False)
    test_all_hours(3, 25, 1, False)
    test_all_hours(3, 25, 2, False)
    test_all_hours(3, 25, 3, False)
    test_all_hours(3, 25, 4, False)
    test_all_hours(3, 25, 5, False)
    test_all_hours(3, 26, 1, False)
    test_all_hours(3, 26, 2, False)
    test_all_hours(3, 26, 3, False)
    test_all_hours(3, 26, 4, False)
    test_all_hours(3, 26, 5, False)
    test_all_hours(3, 27, 2, False)
    test_all_hours(3, 27, 3, False)
    test_all_hours(3, 27, 4, False)
    test_all_hours(3, 27, 5, False)
    test_all_hours(3, 28, 3, False)
    test_all_hours(3, 28, 4, False)
    test_all_hours(3, 28, 5, False)
    test_all_hours(3, 29, 4, False)
    test_all_hours(3, 29, 5, False)
    test_all_hours(3, 30, 5, False)

    test_all_hours(3, 26, 0, True)
    test_all_hours(3, 27, 0, True)
    test_all_hours(3, 27, 1, True)
    test_all_hours(3, 28, 0, True)
    test_all_hours(3, 28, 1, True)
    test_all_hours(3, 28, 2, True)
    test_all_hours(3, 29, 0, True)
    test_all_hours(3, 29, 1, True)
    test_all_hours(3, 29, 2, True)
    test_all_hours(3, 29, 3, True)
    test_all_hours(3, 30, 0, True)
    test_all_hours(3, 30, 1, True)
    test_all_hours(3, 30, 2, True)
    test_all_hours(3, 30, 3, True)
    test_all_hours(3, 30, 4, True)
    test_all_hours(3, 31, 0, True)
    test_all_hours(3, 31, 1, True)
    test_all_hours(3, 31, 2, True)
    test_all_hours(3, 31, 3, True)
    test_all_hours(3, 31, 4, True)
    test_all_hours(3, 31, 5, True)

    test_changes_to(3, 25, 6, False)
    test_changes_to(3, 26, 6, False)
    test_changes_to(3, 27, 6, False)
    test_changes_to(3, 28, 6, False)
    test_changes_to(3, 29, 6, False)
    test_changes_to(3, 30, 6, False)
    test_changes_to(3, 31, 6, False)

    for day in range(1,25):
        for wday in range(7):
            test_all_hours(10, day, wday, True)
    
    test_all_hours(10, 25, 0, True)
    test_all_hours(10, 25, 1, True)
    test_all_hours(10, 25, 2, True)
    test_all_hours(10, 25, 3, True)
    test_all_hours(10, 25, 4, True)
    test_all_hours(10, 25, 5, True)
    test_all_hours(10, 26, 1, True)
    test_all_hours(10, 26, 2, True)
    test_all_hours(10, 26, 3, True)
    test_all_hours(10, 26, 4, True)
    test_all_hours(10, 26, 5, True)
    test_all_hours(10, 27, 2, True)
    test_all_hours(10, 27, 3, True)
    test_all_hours(10, 27, 4, True)
    test_all_hours(10, 27, 5, True)
    test_all_hours(10, 28, 3, True)
    test_all_hours(10, 28, 4, True)
    test_all_hours(10, 28, 5, True)
    test_all_hours(10, 29, 4, True)
    test_all_hours(10, 29, 5, True)
    test_all_hours(10, 30, 5, True)

    test_all_hours(10, 26, 0, False)
    test_all_hours(10, 27, 0, False)
    test_all_hours(10, 27, 1, False)
    test_all_hours(10, 28, 0, False)
    test_all_hours(10, 28, 1, False)
    test_all_hours(10, 28, 2, False)
    test_all_hours(10, 29, 0, False)
    test_all_hours(10, 29, 1, False)
    test_all_hours(10, 29, 2, False)
    test_all_hours(10, 29, 3, False)
    test_all_hours(10, 30, 0, False)
    test_all_hours(10, 30, 1, False)
    test_all_hours(10, 30, 2, False)
    test_all_hours(10, 30, 3, False)
    test_all_hours(10, 30, 4, False)
    test_all_hours(10, 31, 0, False)
    test_all_hours(10, 31, 1, False)
    test_all_hours(10, 31, 2, False)
    test_all_hours(10, 31, 3, False)
    test_all_hours(10, 31, 4, False)
    test_all_hours(10, 31, 5, False)

    test_changes_to(10, 25, 6, True)
    test_changes_to(10, 26, 6, True)
    test_changes_to(10, 27, 6, True)
    test_changes_to(10, 28, 6, True)
    test_changes_to(10, 29, 6, True)
    test_changes_to(10, 30, 6, True)
    test_changes_to(10, 31, 6, True)

    print("PASSED")