import smbus2
import bme280
import time

port = 1
address = 0x76


class BME280:
    def __init__(addr):
        bus = smbus2.SMBus(port)
        calibration_params = bme280.load_calibration_params(bus, address)

    def read():
        data = bme280.sample(bus, address, calibration_params)
        temp = data.temperature
        pre = data.pressure
        hum = data.humidity
        
        return temp,pre,hum

 
