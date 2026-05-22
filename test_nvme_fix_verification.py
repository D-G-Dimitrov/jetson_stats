#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Test script to verify NVMe temperature detection fix

from jtop.core.temperature import get_nvme_temperature
import sys
import os
import subprocess
from unittest.mock import patch, MagicMock

# Add the current directory to the path to import jtop
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_nvme_fix():
    """
    Test NVMe temperature detection with mocked data
    """
    print("Testing NVMe temperature detection fix...")
    print("=" * 70)

    # Mock os.listdir to simulate NVMe devices
    def mock_listdir(path):
        if path == '/dev':
            return ['nvme0', 'nvme0n1', 'nvme0n2', 'nvme-fabrics', 'null', 'zero']
        return []

    # Mock subprocess.run to simulate nvme smart-log output
    def mock_run(cmd, **kwargs):
        mock_result = MagicMock()
        mock_result.returncode = 0

        # Simulate nvme smart-log output
        if 'nvme' in cmd and 'smart-log' in cmd:
            mock_result.stdout = """Smart Log for NVME device:nvme0 namespace-id:ffffffff
critical_warning			: 0
temperature				: 44 C (317 Kelvin)
available_spare				: 100%
available_spare_threshold		: 10%
percentage_used				: 1%
endurance group critical warning summary: 0
data_units_read				: 83249440
data_units_written			: 48221596
host_read_commands			: 800889659
host_write_commands			: 277389777
controller_busy_time			: 809
power_cycles				: 405
power_on_hours				: 565
unsafe_shutdowns			: 30
media_errors				: 0
num_err_log_entries			: 0
Warning Temperature Time		: 0
Critical Composite Temperature Time	: 0
Temperature Sensor 1           : 44 C (317 Kelvin)
Temperature Sensor 2           : 49 C (322 Kelvin)
Thermal Management T1 Trans Count	: 0
Thermal Management T2 Trans Count	: 0
Thermal Management T1 Total Time	: 0
Thermal Management T2 Total Time	: 0
"""
            mock_result.stderr = ''
            return mock_result

        # Default behavior for other commands
        mock_result.stdout = ''
        mock_result.stderr = 'Command not found'
        return mock_result

    # Patch os.listdir, subprocess.run, and os.geteuid()
    with patch('os.listdir', side_effect=mock_listdir):
        with patch('subprocess.run', side_effect=mock_run):
            with patch('os.geteuid', return_value=0):  # Simulate running as root
                with patch('shutil.which', return_value='/usr/sbin/nvme'):
                    nvme_temps = get_nvme_temperature()

    print(f"Result: {nvme_temps}")
    print()

    if not nvme_temps:
        print("❌ FAILED: No NVMe temperatures detected")
        return False

    print("✅ SUCCESS: Found NVMe sensor(s):")
    for name, data in nvme_temps.items():
        temp_c = data['temp'] / 1000.0
        print(f"  {name}: {temp_c:.2f}°C")
        print(f"    Max: {data['max']}°C")
        print(f"    Critical: {data['crit']}°C")

    # Verify the temperature is correct (should be 49°C - max of 44 and 49)
    expected_temp = 49.0
    actual_temp = nvme_temps.get('nvme_nvme0', {}).get('temp', 0) / 1000.0

    if abs(actual_temp - expected_temp) < 0.1:
        print(f"\n✅ Temperature value is correct: {actual_temp:.2f}°C (expected {expected_temp:.2f}°C)")
        return True
    else:
        print(f"\n❌ Temperature value is incorrect: {actual_temp:.2f}°C (expected {expected_temp:.2f}°C)")
        return False


def test_device_path_handling():
    """
    Test that device path handling works correctly
    """
    print("\n" + "=" * 70)
    print("Testing device path handling...")
    print("=" * 70)

    import re

    # Test cases for device name extraction
    test_cases = [
        ('/dev/nvme0', 'nvme0'),
        ('/dev/nvme0n1', 'nvme0'),
        ('/dev/nvme0n2', 'nvme0'),
        ('/dev/nvme1', 'nvme1'),
        ('/dev/nvme1n1', 'nvme1'),
    ]

    all_passed = True
    for device_path, expected_name in test_cases:
        # Extract device name
        device_name = device_path.replace('/dev/', '')
        # Remove partition suffix if present
        device_name = re.sub(r'n\d+$', '', device_name)

        if device_name == expected_name:
            print(f"✅ {device_path} -> {device_name}")
        else:
            print(f"❌ {device_path} -> {device_name} (expected {expected_name})")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    try:
        test1_passed = test_nvme_fix()
        test2_passed = test_device_path_handling()

        print("\n" + "=" * 70)
        if test1_passed and test2_passed:
            print("✅ All tests PASSED!")
            print("=" * 70)
            sys.exit(0)
        else:
            print("❌ Some tests FAILED!")
            print("=" * 70)
            sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
