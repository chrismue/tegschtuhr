# from machine import I2C
from micropython import const
import time

# Operating Modes
BME280_OSAMPLE_1 = const(1)
BME280_OSAMPLE_2 = const(2)
BME280_OSAMPLE_4 = const(3)
BME280_OSAMPLE_8 = const(4)
BME280_OSAMPLE_16 = const(5)

# BME280 Registers

class Device:
    def __init__(self, address, i2c):
        self._address = address
        self._i2c = i2c

    def write8(self, register, value):
        b = bytearray(1)
        b[0] = value & 0xFF
        self._i2c.writeto_mem(self._address, register, b)

    def readU8(self, register):
        return int.from_bytes(
            self._i2c.readfrom_mem(self._address, register, 1), 'little') & 0xFF

    def readS8(self, register):
        result = self.readU8(register)
        if result > 127:
            result -= 256
        return result

    def readU16(self, register):
        result = int.from_bytes(
            self._i2c.readfrom_mem(self._address, register, 2), 'little') & 0xFFFF
        return result

    def readS16(self, register):
        result = self.readU16(register)
        if result > 32767:
            result -= 65536
        return result

    def readU16LE(self, register):
        return self.readU16(register)

    def readS16LE(self, register):
        return self.readS16(register)

class BME280:
    def __init__(self, i2c, mode=BME280_OSAMPLE_1, address=0x76,
                 **kwargs):
        # Check that mode is valid.
        if mode not in [BME280_OSAMPLE_1, BME280_OSAMPLE_2, BME280_OSAMPLE_4,
                        BME280_OSAMPLE_8, BME280_OSAMPLE_16]:
            raise ValueError(
                'Unexpected mode value {0}. Set mode to one of '
                'BME280_ULTRALOWPOWER, BME280_STANDARD, BME280_HIGHRES, or '
                'BME280_ULTRAHIGHRES'.format(mode))
        self._mode = mode
        # Create I2C device.
        self._device = Device(address, i2c)
        # Load calibration values.
        self._load_calibration()
        self._device.write8(0xF4, 0x3F)  # REG_CONTROL
        self.t_fine = 0
        # First measurement after power up is invalid, read here once
        _ = self.temperature

    def _load_calibration(self):
        self.dig_T1 = self._device.readU16LE(0x88)
        self.dig_T2 = self._device.readS16LE(0x8A)
        self.dig_T3 = self._device.readS16LE(0x8C)

        self.dig_P1 = self._device.readU16LE(0x8E)
        self.dig_P2 = self._device.readS16LE(0x90)
        self.dig_P3 = self._device.readS16LE(0x92)
        self.dig_P4 = self._device.readS16LE(0x94)
        self.dig_P5 = self._device.readS16LE(0x96)
        self.dig_P6 = self._device.readS16LE(0x98)
        self.dig_P7 = self._device.readS16LE(0x9A)
        self.dig_P8 = self._device.readS16LE(0x9C)
        self.dig_P9 = self._device.readS16LE(0x9E)

        self.dig_H1 = self._device.readU8(0xA1)
        self.dig_H2 = self._device.readS16LE(0xE1)
        self.dig_H3 = self._device.readU8(0xE3)
        self.dig_H6 = self._device.readS8(0xE7)

        h4 = self._device.readS8(0xE4)
        h4 = (h4 << 24) >> 20
        self.dig_H4 = h4 | (self._device.readU8(0xE5) & 0x0F)

        h5 = self._device.readS8(0xE6)
        h5 = (h5 << 24) >> 20
        self.dig_H5 = h5 | (
            self._device.readU8(0xE5) >> 4 & 0x0F)

    def read_raw_temp(self):
        """Reads the raw (uncompensated) temperature from the sensor."""
        meas = self._mode
        self._device.write8(0xF2, meas)  # CONTROL_HUM
        meas = self._mode << 5 | self._mode << 2 | 1
        self._device.write8(0xF4, meas)  # CONTROL
        sleep_time = 1250 + 2300 * (1 << self._mode)

        sleep_time = sleep_time + 2300 * (1 << self._mode) + 575
        sleep_time = sleep_time + 2300 * (1 << self._mode) + 575
        time.sleep_us(sleep_time)  # Wait the required time
        msb = self._device.readU8(0xFA)  # TEMP_DATA
        lsb = self._device.readU8(0xFA + 1)
        xlsb = self._device.readU8(0xFA + 2)
        raw = ((msb << 16) | (lsb << 8) | xlsb) >> 4
        return raw

    def read_raw_pressure(self):
        """Reads the raw (uncompensated) pressure level from the sensor."""
        """Assumes that the temperature has already been read """
        """i.e. that enough delay has been provided"""
        msb = self._device.readU8(0xF7)  # PRESSURE_DATA
        lsb = self._device.readU8(0xF7 + 1)
        xlsb = self._device.readU8(0xF7 + 2)
        raw = ((msb << 16) | (lsb << 8) | xlsb) >> 4
        return raw

    def read_raw_humidity(self):
        """Assumes that the temperature has already been read """
        """i.e. that enough delay has been provided"""
        msb = self._device.readU8(0xFD)  # HUMIDITY_DATA
        lsb = self._device.readU8(0xFD + 1)
        raw = (msb << 8) | lsb
        return raw

    def read_temperature(self):
        """Get the compensated temperature in 0.01 of a degree celsius."""
        adc = self.read_raw_temp()
        var1 = ((adc >> 3) - (self.dig_T1 << 1)) * (self.dig_T2 >> 11)
        var2 = ((
            (((adc >> 4) - self.dig_T1) * ((adc >> 4) - self.dig_T1)) >> 12) *
            self.dig_T3) >> 14
        self.t_fine = var1 + var2
        return (self.t_fine * 5 + 128) >> 8

    def read_pressure(self):
        """Gets the compensated pressure in Pascals."""
        adc = self.read_raw_pressure()
        var1 = self.t_fine - 128000
        var2 = var1 * var1 * self.dig_P6
        var2 = var2 + ((var1 * self.dig_P5) << 17)
        var2 = var2 + (self.dig_P4 << 35)
        var1 = (((var1 * var1 * self.dig_P3) >> 8) +
                ((var1 * self.dig_P2) >> 12))
        var1 = (((1 << 47) + var1) * self.dig_P1) >> 33
        if var1 == 0:
            return 0
        p = 1048576 - adc
        p = (((p << 31) - var2) * 3125) // var1
        var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
        var2 = (self.dig_P8 * p) >> 19
        return ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)

    def read_humidity(self):
        adc = self.read_raw_humidity()
        h = self.t_fine - 76800
        h = (((((adc << 14) - (self.dig_H4 << 20) - (self.dig_H5 * h)) +
               16384) >> 15) * (((((((h * self.dig_H6) >> 10) * (((h *
                                                                   self.dig_H3) >> 11) + 32768)) >> 10) + 2097152) *
                                 self.dig_H2 + 8192) >> 14))
        h = h - (((((h >> 15) * (h >> 15)) >> 7) * self.dig_H1) >> 4)
        h = 0 if h < 0 else h
        h = 419430400 if h > 419430400 else h
        return h >> 12

    @property
    def temperature(self):
        "Return the temperature in degrees."
        return self.read_temperature() / 100

    @property
    def pressure(self, with_unit=False):
        "Return the temperature in hPa."
        return (self.read_pressure() // 256) / 100

    @property
    def humidity(self, with_unit=False):
        "Return the humidity in percent."
        return self.read_humidity() // 1024
