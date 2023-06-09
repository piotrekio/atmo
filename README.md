# Atmo

Atmo is a home weather station for Raspberry Pi.


## How it works

Atmo is a Python program that collects data from an indoor (BME680), and an outdoor (DS18B20) weather sensors,
and sends it to Graphite, where you can visualise it.

The data consists of four metrics:

* `atmo.temperature_indoor` - indoor temperature (Celsius)
* `atmo.temperature_outdoor` - outdoor temperature (Celsius)
* `atmo.pressure` - pressure (hPa)
* `atmo.humidity` - humidity (relative, %)


## Installation

1. Enable I2C and 1-Wire interfaces in your Raspberry Pi using `raspi-config`.

2. Clone the repository:
   
   ```
   git clone git@github.com:piotrekio/atmo.git ~/atmo
   ```

3. Create a virtualenv:
   
   ```
   python -m venv ~/atmo/venv
   ```

4. Install dependencies:

   ```
   ~/atmo/venv/bin/pip install -r ~/atmo/requirements.txt
   ```

5. Create and edit a file in `~/atmo/.env`, enter the following line:

   ```
   GRAPHITE_HOST=<GRAPHITE_ADDRESS>
   ```
   
   Replace `<GRAPHITE_ADDRESS>` with the address of your Graphite instance.

6. Create a service file from a template:

   ```
   cp ~/atmo/atmo.service.example ~/atmo/atmo.service
   ```

7. Edit the file, replace `<VIRTUALENV_PATH>` and `<REPOSITORY_PATH>`
   with the actual paths from your system.

8. Link the service file:

   ```
   ln -s ~/atmo/atmo/atmo.service /etc/systemd/system/atmo.service
   ```

9. Reload the service manager and enable Atmo:

   ```
   sudo systemctl daemon-reload
   sudo systemctl enable atmo.service
   ```

The service will now start running, and will auto-start after a reboot.


## Configuration

You can use environment variables to modify Atmo's behavior:

Variable name | Default value | Description
--- | --- | ---
`SENSORS_SAMPLE_INTERVAL` | `5.0` | Interval (in seconds) between capturing samples.
`SENSOR_INDOOR_I2C_ADDR` | `0x76` | I2C address of the BME680 sensor. You can find is using `i2cdetect -y 1`.
`GRAPHITE_HOST` | | Address of a Graphite instance.
`GRAPHITE_PORT` | `8125` | Port number on which a Graphite instance is running.
`GRAPHITE_TIMEOUT` | `1.0` | Timeout (in seconds) for sending a metric value to Graphite.
`METRICS_PREFIX` | `atmo` | Prefix for all metric names.
`METRIC_TEMPERATURE_INDOOR` | `temperature_indoor` | Name for the metric representing indoor temperature.
`METRIC_TEMPERATURE_OUTDOOR` | `temperature_outdoor` | Name for the metric representing outdoor temperature.
`METRIC_PRESSURE` | `pressure` | Name for the metric representing pressure.
`METRIC_HUMIDITY` | `humidity` | Name for the metric representing indoor humidity.


## Debugging

Once you install Atmo, you don't have to maintain it, but in case the metrics are not showing up
in your Graphite, you can check program logs with `journalctl -u atmo -f` or status of the service with
`systemctl status atmo`.


## See also

* [BME680 page on manufacturer's website](https://web.archive.org/web/20230324000708/https://www.bosch-sensortec.com/products/environmental-sensors/gas-sensors/bme680/)
* [DS18B20 page on manufacturer's website](https://web.archive.org/web/20230507101742/https://www.analog.com/en/products/ds18b20.html)
