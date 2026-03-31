from sensors.bh1750_sensor import BH1750Sensor
from sensors.bme280_sensor import BME280Sensor
from services.api import start_api
from utils.logger import log

import time

def main():
    log("Starting Smart Clock...")

    # Initialise sensors
    light = BH1750Sensor()
    climate = BME280Sensor()

    # Start API in background
    start_api()

    while True:
        lux = light.read_lux()
        temp, hum = climate.read()

        log(f"Lux: {lux:.2f} | Temp: {temp:.1f}°C | Humidity: {hum:.1f}%")

        time.sleep(1)

if __name__ == "__main__":
    main()
