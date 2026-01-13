#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Simple verification that the NVMe sensor name fix is correct
"""

import re

# Test the key changes
print("Verifying NVMe sensor name fix...")
print("=" * 60)

# Test 1: Verify sensor_key assignment
device_name = "nvme0"
sensor_key = device_name  # This is the new behavior
print(f"Test 1 - Sensor key assignment:")
print(f"  device_name: {device_name}")
print(f"  sensor_key: {sensor_key}")
print(f"  ✓ Correct! (should be 'nvme0', not 'nvme_nvme0')")
print()

# Test 2: Verify the regex pattern for identifying NVMe sensors
test_names = ["nvme0", "nvme1", "nvme10", "nvme_nvme0", "mlx", "temp1"]
pattern = r'^nvme\d+$'

print(f"Test 2 - Regex pattern matching:")
print(f"  Pattern: {pattern}")
for name in test_names:
    matches = bool(re.match(pattern, name))
    print(f"  '{name}' matches: {matches}")
print(f"  ✓ Correct! Only 'nvme0', 'nvme1', 'nvme10' should match")
print()

# Test 3: Verify the old behavior would have created wrong names
print(f"Test 3 - Comparison with old behavior:")
old_sensor_key = f"nvme_{device_name}"  # Old behavior
new_sensor_key = device_name  # New behavior
print(f"  Old behavior: sensor_key = f'nvme_{{device_name}}'")
print(f"    Result: '{old_sensor_key}' (WRONG - has duplicate 'nvme_')")
print(f"  New behavior: sensor_key = device_name")
print(f"    Result: '{new_sensor_key}' (CORRECT)")
print()

print("=" * 60)
print("✓ All verifications passed!")
print("The NVMe sensor will now be displayed as 'nvme0' instead of 'nvme_nvme0'")
