import board
import adafruit_bme280

class BME280Sensor:
    def __init__(self):
        i2c = board.I2C()
        self.sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c)

    def read(self):
        temp = self.sensor.temperature
        hum = self.sensor.humidity
        return temp, hum
