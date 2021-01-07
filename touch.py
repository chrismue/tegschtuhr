from machine import Pin
import esp32

class TouchSensor:
    def __init__(self, pin_nr, callback):
        self.pin = Pin(pin_nr, Pin.IN)
        self.pin.irq(trigger=Pin.IRQ_RISING, handler=lambda x: callback())

    def is_pressed(self):
        return self.pin.value()

    def configure_for_wakeup(self):
        esp32.wake_on_ext0(pin = self.pin, level = esp32.WAKEUP_ANY_HIGH)


def demotouch():
    import time
    def _pressed():
        print("PRESSED!")
    return TouchSensor(0, _pressed)
