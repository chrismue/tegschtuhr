"""
MicroPython max7219 cascadable 8x8 LED matrix driver
https://github.com/mcauser/micropython-max7219
MIT License
Copyright (c) 2017 Mike Causer
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from micropython import const
import framebuf
from machine import Pin, SPI

_NOOP = const(0)
_DIGIT0 = const(1)
_DECODEMODE = const(9)
_INTENSITY = const(10)
_SCANLIMIT = const(11)
_SHUTDOWN = const(12)
_DISPLAYTEST = const(15)

class Max7219Chain:
    def __init__(self, spi_nr, cs_pinnr, sck_pinnr=14, mosi_pinnr=13, miso_pinnr=12):
        # self._spi = SPI(spi_nr, 5000000)  # (14 SK, 13 MOSI), 5'000'000
        # self._spi = SPI(-1, baudrate=100000, sck=Pin(14), mosi=Pin(13), miso=Pin(0))
        self._spi = SPI(spi_nr, 5000000, sck=Pin(sck_pinnr), mosi=Pin(mosi_pinnr), miso=Pin(miso_pinnr))  # (14 SK, 13 MOSI), 5'000'000
        self._cs = Pin(cs_pinnr, Pin.OUT)
        self._cs.on()
        self._buffer = bytearray(8*3)
        self._initialize()

    def _initialize(self):
        for cmd, data in ((_SHUTDOWN, 0),
                          (_DISPLAYTEST, 0),
                          (_SCANLIMIT, 7),
                          (_DECODEMODE, 0),
                          (_SHUTDOWN, 1)):
            self._write_to_all(cmd, data)
        self.set_brightness(15)
        self.show()

    def _write_to_all(self, command, data):
        self._cs.off()
        self._write_spi(command,data)
        self._write_spi(command,data)
        self._write_spi(command,data)
        self._cs.on()
        print("CMD:", command, data)

    def _write_spi(self,c,d):
        self._spi.write(bytearray([c,d]))

    def show(self):
        for digit_nr in range(8):
            self._cs.off()
            self._write_spi(_DIGIT0 + digit_nr, self._buffer[2*8+digit_nr])
            self._write_spi(_DIGIT0 + digit_nr, self._buffer[ 8 +digit_nr])
            self._write_spi(_DIGIT0 + digit_nr, self._buffer[digit_nr])
            self._cs.on()
        # print(self._buffer)
        #self.reset_buffer()

    def set_brightness(self, brightness):
        if brightness > 15:
            brightness = 15
        if brightness < 1:
            brightness = 1
        self._write_to_all(_INTENSITY, brightness)

    def reset_buffer(self):
        self._buffer = bytearray(8*3)

    def add_pixels(self, positions):
        for pos in positions:
            self.add_pixel(pos[0], pos[1])

    def add_led(self, lednr):
        self.add_pixel(lednr // 14, lednr % 14)

    def add_pixel(self, r, c):
        if r < 8:
            driver_nr = c // 7
            digit_nr = r
        else:
            driver_nr = 2
            if c<7:
                digit_nr = r - 8
            else:
                digit_nr = r - 4
        offset = c % 7
        #print("->", driver_nr, digit_nr, offset, driver_nr*8 + digit_nr)
        self._buffer[driver_nr*8 + digit_nr] |= 1 << offset
        self.show()

    def show_pixels(self, positions):
        # print("showing", positions)
        self.reset_buffer()
        self.add_pixels(positions)
        self.show()

def demo():
    m=MatrixDrivers(1,15)
    import time
    for i in range(12*14):
        #m.reset_buffer()
        m.add_led(i)
        time.sleep(0.1)
        #time.sleep(0.2)
    time.sleep(1)
    m.reset_buffer()
    m.show()
