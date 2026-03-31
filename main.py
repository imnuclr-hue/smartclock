from sensors.bh1750_sensor import BH1750Sensor
from sensors.bme280_sensor import BME280Sensor
from sensors.pir_sensor import PIRSensor
from services.api import start_api

import time

def main():
    print("Starting Smart Clock...")

    # Initialise sensors
    light = BH1750Sensor()
    climate = BME280Sensor()
    pir = PIRSensor()

    # Start API in background
    start_api()

    while True:
        lux = light.read_lux()
        temp, hum = climate.read()
        motion = pir.detect_motion()

        print(f"Lux: {lux:.2f} | Temp: {temp:.1f}°C | Humidity: {hum:.1f}% | Motion: {motion}")

        time.sleep(1)

if __name__ == "__main__":
    main()
