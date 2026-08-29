#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Test regex pattern with more debugging

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

print("Testing regex pattern with detailed debugging...")
print("=" * 60)

for line in mock_output.split('\n'):
    if 'Temperature Sensor' in line:
        print(f"Line: {line!r}")
        print(f"  Length: {len(line)}")
        print(f"  Characters around colon:")
        for i, char in enumerate(line):
            if char == ':':
                print(f"    Position {i}: '{char}'")
                start = max(0, i-10)
                end = min(len(line), i+20)
                print(f"    Context: {line[start:end]!r}")
        print()

print("=" * 60)
print("Testing various patterns:")
print()

patterns = [
    r'Temperature Sensor \d+: ([0-9]+) C',
    r'Temperature Sensor \d+:\s+([0-9]+) C',
    r'Temperature Sensor \d+:\s*([0-9]+) C',
    r'Temperature Sensor \d+:\s*([0-9]+)\s+C',
    r'Temperature Sensor \d+:\s*([0-9]+)\s+C\s*\(.*\)',
]

for pattern in patterns:
    print(f"Pattern: {pattern}")
    for line in mock_output.split('\n'):
        if 'Temperature Sensor' in line:
            match = re.search(pattern, line)
            if match:
                print(f"  ✓ Match: {match.group(1)}")
            else:
                print(f"  ✗ No match for: {line[:50]}...")
    print()
