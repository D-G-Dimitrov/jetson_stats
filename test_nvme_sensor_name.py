#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Test script to verify NVMe sensor name fix
"""

import sys
import os

# Add the jtop module to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jtop.core.temperature import get_nvme_temperature

def test_nvme_sensor_name():
    """Test that NVMe sensor names are correctly formatted as 'nvme0' instead of 'nvme_nvme0'"""

    # Mock the nvme command to simulate having an NVMe device
    import unittest.mock as mock

    # Create a mock for subprocess.run
    def mock_run(cmd, **kwargs):
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = """\
temperature                 : 45 C (45 Kelvin)
Temperature Sensor 1       : 45 C (318 Kelvin)
Temperature Sensor 2       : 46 C (319 Kelvin)
"""
        mock_result.stderr = ""
        return mock_result

    # Patch subprocess.run
    with mock.patch('subprocess.run', side_effect=mock_run):
        # Also patch os.listdir to return our mock device
        with mock.patch('os.listdir', return_value=['nvme0', 'nvme0n1', 'sda']):
            # Call the function
            result = get_nvme_temperature()

            print("NVMe temperature detection result:")
            print(f"  Found {len(result)} NVMe sensor(s)")
            for sensor_name, sensor_data in result.items():
                print(f"  Sensor: '{sensor_name}'")
                print(f"    Temp: {sensor_data.get('temp', 'N/A')}")
                print(f"    Max: {sensor_data.get('max', 'N/A')}")
                print(f"    Crit: {sensor_data.get('crit', 'N/A')}")

                # Verify the sensor name format
                if sensor_name.startswith('nvme_'):
                    print(f"    ❌ ERROR: Sensor name has 'nvme_' prefix: '{sensor_name}'")
                    return False
                elif sensor_name == 'nvme0':
                    print(f"    ✓ CORRECT: Sensor name is 'nvme0'")
                    return True
                else:
                    print(f"    ⚠ WARNING: Unexpected sensor name format: '{sensor_name}'")
                    return False

    return False

if __name__ == '__main__':
    print("Testing NVMe sensor name format...")
    print("=" * 60)

    success = test_nvme_sensor_name()

    print("=" * 60)
    if success:
        print("✓ TEST PASSED: NVMe sensor name is correctly formatted as 'nvme0'")
        sys.exit(0)
    else:
        print("✗ TEST FAILED: NVMe sensor name is not correctly formatted")
        sys.exit(1)
