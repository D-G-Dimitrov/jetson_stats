# -*- coding: UTF-8 -*-
# This file is part of the jetson_stats package (https://github.com/rbonghi/jetson_stats or http://rnext.it).
# Copyright (c) 2019-2026 Raffaello Bonghi.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from .common import cat, check_file
import os
import re
import subprocess
import shutil
# Logging
import logging
# Create logger
logger = logging.getLogger(__name__)
TEMPERATURE_RE = re.compile(r'^temp(?P<num>\d+)_label$')
TEMPERATURE_OFFLINE = -256

def read_temperature(data):
    values = {}
    for name, path in data.items():
        try:
            value = float(cat(path)) / 1000.0
            values[name] = value
        except (OSError, ValueError):
            # If negative sensor offline
            values[name] = TEMPERATURE_OFFLINE
    return values

def read_sensor_value(sensor, sensor_type='generic', default_max=84, default_crit=100):
    """
    Read sensor value and convert to appropriate format.

    Args:
        sensor: Sensor dictionary containing temperature data
        sensor_type: Type of sensor ('generic', 'mellanox')
        default_max: Default maximum temperature for this sensor type
        default_crit: Default critical temperature for this sensor type

    Returns:
        Dictionary with temperature value, max, crit, and online status
    """
    values = {}

    # Check if sensor value is already a number (from Mellanox) or a path
    if isinstance(sensor.get('temp'), (int, float)):
        # Direct numeric value (stored in millidegrees)
        temp_value = sensor['temp'] / 1000.0
        values['temp'] = temp_value
        # Copy max and crit values if they exist
        # Note: For Mellanox sensors, max/crit could be in either millidegrees or Celsius
        # We need to check if the value is large enough to be in millidegrees (> 1000)
        if 'max' in sensor:
            if isinstance(sensor['max'], (int, float)):
                # Convert from millidegrees to Celsius if the value is large
                if sensor['max'] > 1000:
                    values['max'] = sensor['max'] / 1000.0
                else:
                    values['max'] = sensor['max']
            else:
                values['max'] = sensor['max']
        if 'crit' in sensor:
            if isinstance(sensor['crit'], (int, float)):
                # Convert from millidegrees to Celsius if the value is large
                if sensor['crit'] > 1000:
                    values['crit'] = sensor['crit'] / 1000.0
                else:
                    values['crit'] = sensor['crit']
            else:
                values['crit'] = sensor['crit']
        # Add default max and crit values if not present
        if 'max' not in values:
            values['max'] = default_max
        if 'crit' not in values:
            values['crit'] = default_crit
        values['online'] = True
    else:
        # Path-based sensor
        values = read_temperature(sensor)
        # Copy max and crit values if they exist
        if 'max' in sensor:
            values['max'] = sensor['max']
        if 'crit' in sensor:
            values['crit'] = sensor['crit']
        # Add default max and crit values if not present
        if 'max' not in values:
            values['max'] = default_max
        if 'crit' not in values:
            values['crit'] = default_crit
        values['online'] = values['temp'] != TEMPERATURE_OFFLINE

    return values

def get_virtual_thermal_temperature(thermal_path):
    temperature = {}
    # Find all thermal zone available
    items = os.listdir(thermal_path)
    subdirectories = ["{path}/{item}".format(path=thermal_path, item=item)
                      for item in items if os.path.isdir(os.path.join(thermal_path, item)) and 'thermal_' in item]
    # Check if is a real temperature
    idx = 0
    for thermal_path in subdirectories:
        path_name = "{path}/type".format(path=thermal_path)
        path_value = "{path}/temp".format(path=thermal_path)
        if os.path.isfile(path_name) and os.path.isfile(path_value):
            # Decode name
            raw_name = cat(path_name).strip()
            name = raw_name.split("-")[0] if '-' in raw_name else raw_name.split("_")[0]
            # Remove PMIC temperature (TX family)
            if 'PMIC' in name:
                logger.warn("Skipped PMIC")
                continue
            # Store new temperature
            name = name if name not in temperature else "{name}{idx}".format(name=name, idx=idx)
            idx = idx if name not in temperature else idx + 1
            # Check if is readable and accessible
            if check_file(os.path.join(thermal_path, "temp")):
                temperature[name] = {'temp': os.path.join(thermal_path, "temp")}
                # Message detected
                logger.info("Found thermal \"{name}\" in {path}".format(name=name, path=os.path.basename(thermal_path)))
    # Sort all temperatures
    return temperature

def get_hwmon_thermal_system(root_dir):
    sensor_name = {}
    if not os.path.isdir(root_dir):
        logger.error("Folder {root_dir} doesn't exist".format(root_dir=root_dir))
        return sensor_name
    # Fin all fans
    for dir in os.listdir(root_dir):
        path = os.path.join(root_dir, dir)
        if not os.path.isdir(path):
            continue
        # Read the hwmon device name (e.g. "nvme") so generic labels like
        # "Composite" or "Sensor 1" can be disambiguated by their source device.
        device_name_path = os.path.join(path, "name")
        device_name = cat(device_name_path).strip() if os.path.isfile(device_name_path) else ""
        # Find all pwm in folder
        for file in os.listdir(path):
            name_label_path = os.path.join(path, file)
            # Check if there is a label
            match = re.search(TEMPERATURE_RE, file)
            if not match:
                continue
            parsed_name = match.groupdict()
            # Build list current and average power read
            number_port = int(parsed_name['num'])
            # Read name
            raw_name = cat(name_label_path).strip()
            # Prefix with the hwmon device name (e.g. "nvme" + "Composite" -> "nvme Composite")
            if device_name:
                raw_name = "{dev} {label}".format(dev=device_name, label=raw_name.strip())
            logger.info("Found temperature sensor: {name}".format(name=raw_name))
            # Build list of path
            path_crit_alarm = os.path.join(path, "temp{num}_crit_alarm".format(num=number_port))
            if check_file(path_crit_alarm):
                warnings = {'crit_alarm': path_crit_alarm}
                values = read_temperature(warnings)
                logger.info("Alarms {name} - {data}".format(name=raw_name, data=values))
            # Read Temperatures
            sensor = {}
            if check_file(os.path.join(path, "temp{num}_input".format(num=number_port))):
                sensor['temp'] = os.path.join(path, "temp{num}_input".format(num=number_port))  # Temperature in deg
            if check_file(os.path.join(path, "temp{num}_input".format(num=number_port))):
                sensor['max'] = os.path.join(path, "temp{num}_max".format(num=number_port))  # Temperature in deg
            if check_file(os.path.join(path, "temp{num}_input".format(num=number_port))):
                sensor['crit'] = os.path.join(path, "temp{num}_crit".format(num=number_port))  # Temperature in deg
            # If there is an file is added in list
            if sensor:
                sensor_name[raw_name] = sensor
    return sensor_name

def get_mellanox_temperature():
    """Detect and read temperature from Mellanox NICs with MLNX_OFED support"""
    temperature = {}

    # Check if mget_temp is available (part of MLNX_OFED)
    if not shutil.which('mget_temp'):
        logger.debug("mget_temp not found, Mellanox temperature detection skipped")
        return temperature

    logger.info("MLNX_OFED detected, using mget_temp for Mellanox NIC temperatures")

    # Find all Mellanox devices
    try:
        # Get list of Mellanox devices
        devices_result = subprocess.run(
            ['lspci', '-d', '15b3:', '-D'],
            capture_output=True,
            text=True,
            timeout=5
        )
    except subprocess.TimeoutExpired:
        logger.warning("Timeout while running lspci to detect Mellanox devices")
        return temperature
    except Exception as e:
        logger.warning(f"Error running lspci to detect Mellanox devices: {str(e)}")
        return temperature

    if devices_result.returncode != 0 or not devices_result.stdout.strip():
        logger.debug("No Mellanox devices found via lspci")
        return temperature

    device_lines = devices_result.stdout.strip().split('\n')
    for device_line in device_lines:
        if device_line.strip():
            # Extract device name and bus address
            parts = device_line.strip().split()
            if len(parts) >= 2:
                bus_addr = parts[0]
                device_name = ' '.join(parts[1:])
                # Check if it's a ConnectX device
                if 'ConnectX' in device_name or 'MT' in device_name:
                    # Try to read temperature using mget_temp
                    # Note: mget_temp must be runnable without sudo
                    # Users should configure appropriate permissions or use sudo wrapper scripts
                    try:
                        temp_result = subprocess.run(
                            ['mget_temp', '-d', bus_addr],
                            capture_output=True,
                            text=True,
                            timeout=2
                        )
                    except subprocess.TimeoutExpired:
                        logger.warning(f"mget_temp timed out for {bus_addr}")
                        continue
                    except Exception as e:
                        logger.warning(f"Error reading temperature for {bus_addr}: {str(e)}")
                        continue

                    if temp_result.returncode == 0 and temp_result.stdout.strip():
                        raw_output = temp_result.stdout.strip()
                        # Use only the first line and extract the first numeric token to be resilient to format changes
                        first_line = raw_output.splitlines()[0]
                        match = re.search(r'([-+]?(?:\d+(?:\.\d*)?|\.\d+))', first_line)
                        if not match:
                            logger.warning(f"Could not find numeric temperature in mget_temp output for {bus_addr}: {first_line!r}")
                            continue
                        temp_value_str = match.group(1)
                        try:
                            temp_celsius = float(temp_value_str)
                            # Use simplified sensor name "mlx" for Mellanox devices
                            sensor_key = "mlx"
                            # Store with higher precision to preserve decimal places
                            # Include default max and crit values for Mellanox sensors (in Celsius)
                            temperature[sensor_key] = {
                                'temp': temp_celsius * 1000.0,  # Store in millidegrees for consistency
                                'max': 84,  # Default max temperature in Celsius
                                'crit': 100  # Default critical temperature in Celsius
                            }
                            logger.info(f"Found Mellanox NIC temperature: {device_name} = {temp_celsius:.2f}°C")
                        except ValueError:
                            logger.warning(f"Could not parse temperature from mget_temp for {bus_addr}: {temp_value_str!r}")
                    elif temp_result.returncode != 0:
                        logger.warning(f"mget_temp failed for {bus_addr}: {temp_result.stderr}")

    return temperature

def get_nvme_temperature():
    """Detect and read temperature from NVMe devices"""
    temperature = {}

    # Check if nvme command is available
    if not shutil.which('nvme'):
        logger.debug("nvme command not found, NVMe temperature detection skipped")
        return temperature

    logger.info("NVMe CLI detected, checking for NVMe devices")

    # Find all NVMe devices - look for controller devices (nvme0, nvme1, etc.)
    # not partition devices (nvme0n1, nvme0n2, etc.)
    try:
        # List all devices in /dev and filter for NVMe controllers
        # We need to do this manually since shell globbing doesn't work in subprocess
        devices = []
        if os.path.isdir('/dev'):
            for item in os.listdir('/dev'):
                # Match nvme0, nvme1, etc. but not nvme0n1, nvme-fabrics, etc.
                if re.match(r'^nvme\d+$', item):
                    devices.append(os.path.join('/dev', item))
        else:
            logger.debug("No /dev directory found")
            return temperature

        if not devices:
            logger.debug("No NVMe devices found")
            return temperature

    except Exception as e:
        logger.warning(f"Error detecting NVMe devices: {str(e)}")
        return temperature

    for device_path in devices:
        # Extract device name (e.g., /dev/nvme0 -> nvme0)
        device_name = device_path.replace('/dev/', '')
        # Remove partition suffix if present (e.g., nvme0n1 -> nvme0)
        device_name = re.sub(r'n\d+$', '', device_name)

        # Try to read temperature using nvme smart-log
        # Check if we're running with sudo privileges
        # Only use sudo if not already running as root
        # Note: When running as root (euid=0), we don't need sudo
        use_sudo = os.geteuid() != 0
        nvme_cmd = ['sudo', 'nvme', 'smart-log', device_path] if use_sudo else ['nvme', 'smart-log', device_path]

        try:
            temp_result = subprocess.run(
                nvme_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
        except subprocess.TimeoutExpired:
            logger.warning(f"nvme smart-log timed out for {device_path}")
            continue
        except Exception as e:
            logger.warning(f"Error reading temperature for {device_path}: {str(e)}")
            continue

        if temp_result.returncode == 0 and temp_result.stdout.strip():
            raw_output = temp_result.stdout.strip()
            # Parse first temperature reading from main output (e.g., "temperature				: 48 C (321 Kelvin)")
            temp_found = False
            for line in raw_output.split('\n'):
                if line.strip().startswith('temperature'):
                    # Extract temperature value (e.g., "temperature				: 48 C (321 Kelvin)")
                    # Match the temperature value followed by ' C'
                    match = re.search(r'([0-9]+)\s+C', line)
                    if match:
                        try:
                            temp_celsius = float(match.group(1))
                            sensor_key = device_name
                            # Store with higher precision to preserve decimal places
                            # Include default max and crit values for NVMe sensors
                            temperature[sensor_key] = {
                                'temp': temp_celsius * 1000.0,  # Store in millidegrees for consistency
                                'max': 84,  # Default max temperature
                                'crit': 100  # Default critical temperature
                            }
                            logger.info(f"Found NVMe device temperature: {device_name} = {temp_celsius:.2f}°C")
                            temp_found = True
                            break
                        except ValueError:
                            logger.warning(f"Could not parse temperature from line: {line!r}")

            if not temp_found:
                logger.debug(f"No temperature reading found in smart-log output for {device_path}")
        elif temp_result.returncode != 0:
            logger.warning(f"nvme smart-log failed for {device_path}: {temp_result.stderr}")

    return temperature

class TemperatureService(object):

    def __init__(self):
        self._temperature = {}
        # Find all temperature available
        sys_folder = "/sys"
        if os.getenv('JTOP_TESTING', False):
            logger.warning("Running in JTOP_TESTING folder={root_dir}".format(root_dir=sys_folder))
        # Build folders
        hwmon_dir = os.path.join(sys_folder, "class", "hwmon")
        thermal_path = os.path.join(sys_folder, "devices", "virtual", "thermal")
        if os.path.isdir(thermal_path):
            # Sort all temperatures
            self._temperature = get_virtual_thermal_temperature(thermal_path)
        if os.path.isdir(hwmon_dir):
            hwmon_temperatures = get_hwmon_thermal_system(hwmon_dir)
            self._temperature.update(hwmon_temperatures)
        # Check for Mellanox NICs with MLNX_OFED
        mellanox_temperatures = get_mellanox_temperature()
        self._temperature.update(mellanox_temperatures)
        # Check for NVMe devices
        nvme_temperatures = get_nvme_temperature()
        self._temperature.update(nvme_temperatures)
        if not self._temperature:
            logger.warning("Temperature not folder found!")
        # Sort all sensors
        self._temperature = dict(sorted(self._temperature.items(), key=lambda item: item[0].lower()))

    def get_status(self):
        status = {}
        # Read temperature from board
        for name, sensor in self._temperature.items():
            # Check if this is a Mellanox sensor that needs fresh data
            if name == 'mlx' and isinstance(sensor.get('temp'), (int, float)):
                # Get current Mellanox temperature
                mellanox_temps = get_mellanox_temperature()
                if name in mellanox_temps:
                    # Read Mellanox sensor with default max/crit values
                    values = read_sensor_value(mellanox_temps[name], sensor_type='mellanox')
                else:
                    # Sensor not found, mark as offline
                    values = {'temp': TEMPERATURE_OFFLINE, 'max': 84, 'crit': 100, 'online': False}
            # Check if this is a NVMe sensor that needs fresh data
            elif re.match(r'^nvme\d+$', name) and isinstance(sensor.get('temp'), (int, float)):
                # Get current NVMe temperature
                nvme_temps = get_nvme_temperature()
                if name in nvme_temps:
                    # Read NVMe sensor with default max/crit values
                    values = read_sensor_value(nvme_temps[name], sensor_type='generic')
                else:
                    # Sensor not found, mark as offline
                    values = {'temp': TEMPERATURE_OFFLINE, 'max': 84, 'crit': 100, 'online': False}
            else:
                # Read sensor value using generic function
                values = read_sensor_value(sensor)
            # Add sensor in dictionary
            status[name] = values
        return status
# EOF
