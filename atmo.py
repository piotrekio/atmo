"""
Atmo, a home weather station for Raspberry Pi
"""
import socket
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional

import structlog
from bme680 import BME680
from bme680.constants import DISABLE_GAS_MEAS, OS_8X
from decouple import config
from w1thermsensor import W1ThermSensor

# Sensors
SENSORS_SAMPLE_INTERVAL = config("SENSORS_SAMPLE_INTERVAL", cast=float, default=5.0)
SENSOR_INDOOR_I2C_ADDR = config("SENSOR_INDOOR_I2C_ADDR", cast=int, default=0x76)

# Graphite
GRAPHITE_HOST = config("GRAPHITE_HOST")
GRAPHITE_PORT = config("GRAPHITE_PORT", cast=int, default=8125)
GRAPHITE_TIMEOUT = config("GRAPHITE_TIMEOUT", cast=float, default=1.0)

# Metric names
METRICS_PREFIX = config("METRICS_PREFIX", default="atmo")
METRIC_TEMPERATURE_INDOOR = config(
    "METRIC_TEMPERATURE_INDOOR", default="temperature_indoor"
)
METRIC_TEMPERATURE_OUTDOOR = config(
    "METRIC_TEMPERATURE_OUTDOOR", default="temperature_outdoor"
)
METRIC_PRESSURE = config("METRIC_PRESSURE", default="pressure")
METRIC_HUMIDITY = config("METRIC_HUMIDITY", default="humidity")


# Set up logging
logger = structlog.get_logger()

IndoorSensor = BME680
OutdoorSensor = W1ThermSensor


@dataclass(frozen=True)
class Sample:
    temperature: float
    humidity: Optional[float] = None
    pressure: Optional[float] = None


def get_indoor_sensor(
    error_interval: float = SENSORS_SAMPLE_INTERVAL,
) -> Optional[IndoorSensor]:
    """
    Return an instance of the class representing the indoor sensor

    If the sensor is not available, the function will retry until it is.
    """
    while True:
        try:
            return BME680(SENSOR_INDOOR_I2C_ADDR)
        except (RuntimeError, PermissionError):
            logger.error(f"Sensor not found. Retrying in {error_interval} second(s)...")
            time.sleep(error_interval)
            continue
    return None


def get_outdoor_sensor() -> Opitonal[OutdoorSensor]:
    """
    Return an instance of the class representing the outdoor sensor
    """
    try:
        return W1ThermSensor()
    except Exception:
        return None


def initalize_indoor_sensor(sensor: IndoorSensor, oversampling: int = OS_8X):
    """
    Set up parameters of the indoor sensor
    """
    sensor.set_gas_status(DISABLE_GAS_MEAS)
    sensor.set_humidity_oversample(oversampling)
    sensor.set_temperature_oversample(oversampling)
    sensor.set_pressure_oversample(oversampling)


def get_indoor_sample(sensor: IndoorSensor) -> Optional[Sample]:
    """
    Return a sample from the indoor sensor
    """
    try:
        status: bool = sensor.get_sensor_data()
    except OSError:
        initalize_indoor_sensor(sensor)
        return
    if status:
        return Sample(
            temperature=sensor.data.temperature,
            pressure=sensor.data.pressure,
            humidity=sensor.data.humidity,
        )
    return None


def get_outdoor_sample(sensor: OutdoorSensor) -> Sample:
    """
    Return a sample from the outdoor sensor
    """
    return Sample(temperature=sensor.get_temperature())


def send_metric(
    metric_name: str,
    metric_value: float,
    metric_type: str = "g",
    prefix: str = METRICS_PREFIX,
    timeout: float = GRAPHITE_TIMEOUT,
):
    """
    Send a UDP message with a metric value to Graphite

    The message format follows StatsD syntax.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(
            f"{prefix}.{metric_name}:{metric_value}|{metric_type}".encode(),
            (GRAPHITE_HOST, GRAPHITE_PORT),
        )
    except OSError:
        # Raised when network is unreachable
        pass
    finally:
        sock.close()


def capture_sample(
    indoor_sensor: Optional[IndoorSensor], outdoor_sensor: Optional[OutdoorSensor]
):
    """
    Get samples from both sensors and send them to Graphite
    """
    if indoor_sensor:
        if indoor_sample := get_indoor_sample(indoor_sensor):
            send_metric(METRIC_HUMIDITY, indoor_sample.humidity)
            send_metric(METRIC_PRESSURE, indoor_sample.pressure)
            send_metric(METRIC_TEMPERATURE_INDOOR, indoor_sample.temperature)
        else:
            logger.error(f"Unable to read data from the indoor sensor")
    if outdoor_sensor:
        outdoor_sample = get_outdoor_sample(outdoor_sensor)
        send_metric(METRIC_TEMPERATURE_OUTDOOR, outdoor_sample.temperature)


@contextmanager
def ensure_duration(expected_duration: float):
    """
    Add sleep to ensure duration of instructions in the context
    """
    time_start = time.monotonic()
    yield
    time_end = time.monotonic()
    duration = time_end - time_start
    if duration < expected_duration:
        time.sleep(expected_duration - duration)


def main(interval: float = SENSORS_SAMPLE_INTERVAL):
    """
    Start the main loop of the program
    """
    sensor_outdoor = get_outdoor_sensor()
    sensor_indoor = get_indoor_sensor()
    if not (sensor_outdoor and sendor_indoor):
        logger.error("Unable to acquire any sensor, exiting")
        return
    logger.info("Sensors acquired", outdoor=sensor_outdoor, indoor=sensor_indoor)
    initalize_indoor_sensor(sensor_indoor)
    while True:
        with ensure_duration(interval):
            capture_sample(sensor_indoor, sensor_outdoor)


if __name__ == "__main__":
    main()
