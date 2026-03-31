import board
import adafruit_bh1750

class BH1750Sensor:
    def __init__(self):
        i2c = board.I2C()
        self.sensor = adafruit_bh1750.BH1750(i2c)

    def read_lux(self):
        return self.sensor.lux