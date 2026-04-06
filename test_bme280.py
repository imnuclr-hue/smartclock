import smbus2
import bme280
import time

port = 1
address = 0x76

bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

print("BME280 test (0x76)\n")

while True:
    data = bme280.sample(bus, address, calibration_params)

    print(f"Temperature: {data.temperature:.2f} °C")
    print(f"Pressure:    {data.pressure:.2f} hPa")
    print(f"Humidity:    {data.humidity:.2f} %")
    print("-" * 30)

    time.sleep(2)
