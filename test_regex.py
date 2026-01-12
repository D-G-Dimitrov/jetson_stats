#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Test regex pattern

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

print("Testing regex pattern...")
print("=" * 60)

pattern = r'Temperature Sensor \d+:\s+([0-9]+) C'
print(f"Pattern: {pattern}")
print()

sensor_temps = []
for line in mock_output.split('\n'):
    if 'Temperature Sensor' in line:
        print(f"Line: {line!r}")
        match = re.search(pattern, line)
        if match:
            print(f"  ✓ Match found: {match.group(1)}")
            sensor_temps.append(float(match.group(1)))
        else:
            print("  ✗ No match")

print()
print(f"Found {len(sensor_temps)} temperature sensors")
if sensor_temps:
    print(f"Temperatures: {sensor_temps}")
    print(f"Max temperature: {max(sensor_temps)}°C")
