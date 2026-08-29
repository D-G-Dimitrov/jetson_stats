#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Test regex pattern - final version

import re

mock_output = """Smart Log for NVME device:nvme0 namespace-id:ffffffff
critical_warning                        : 0
temperature                             : 48 C (321 Kelvin)
available_spare                         : 100%
available_spare_threshold               : 10%
percentage_used                         : 1%
endurance group critical warning summary: 0
data_units_read                         : 83159341
data_units_written                      : 48220461
host_read_commands                      : 800657575
host_write_commands                     : 277362220
controller_busy_time                    : 807
power_cycles                            : 405
power_on_hours                          : 562
unsafe_shutdowns                        : 30
media_errors                            : 0
num_err_log_entries                     : 0
Warning Temperature Time                : 0
Critical Composite Temperature Time     : 0
Temperature Sensor 1           : 48 C (321 Kelvin)
Temperature Sensor 2           : 54 C (327 Kelvin)
Thermal Management T1 Trans Count       : 0
Thermal Management T2 Trans Count       : 0
Thermal Management T1 Total Time        : 0
Thermal Management T2 Total Time        : 0
"""

print("Testing regex pattern - final version")
print("=" * 60)

# The issue is that we need to match the colon AFTER the sensor number
# The pattern should be: "Temperature Sensor X : Y C"
# We need to match the colon that comes after the sensor number and spaces

patterns = [
    # This matches the colon at the end of the line before the temperature
    r'Temperature Sensor \d+:\s*([0-9]+)\s+C',
    # More specific - match the exact format
    r'Temperature Sensor \d+:\s*([0-9]+)\s+C\s*\(.*Kelvin\)',
]

for pattern in patterns:
    print(f"Pattern: {pattern}")
    sensor_temps = []
    for line in mock_output.split('\n'):
        if 'Temperature Sensor' in line:
            match = re.search(pattern, line)
            if match:
                temp = float(match.group(1))
                sensor_temps.append(temp)
                print(f"  ✓ Found: {temp}°C")
            else:
                print(f"  ✗ No match: {line.strip()}")
    print(f"  Result: {len(sensor_temps)} sensors, max = {max(sensor_temps) if sensor_temps else 'N/A'}°C")
    print()

# Let's try a different approach - match from the end of the line
print("=" * 60)
print("Alternative approach - match temperature value with C:")
pattern = r'([0-9]+)\s+C'
for line in mock_output.split('\n'):
    if 'Temperature Sensor' in line:
        match = re.search(pattern, line)
        if match:
            temp = float(match.group(1))
            print(f"  ✓ Found: {temp}°C in line: {line.strip()}")
        else:
            print(f"  ✗ No match: {line.strip()}")
