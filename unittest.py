from localtime import LocalTime

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
