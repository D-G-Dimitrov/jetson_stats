#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Test script to verify Mellanox sensor name shortening and max/crit values.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import patch, MagicMock
from jtop.core.temperature import get_mellanox_temperature, TemperatureService

def test_mellanox_sensor_name():
    """Test that Mellanox sensor name is shortened to 'mlx'"""
    print("Testing Mellanox sensor name shortening...")

    # Mock subprocess to simulate Mellanox device detection
    mock_run = MagicMock()

    # Mock lspci output for Mellanox device
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="0005:01:00.0 Mellanox Technologies MT27800 Family [ConnectX-5]",
        stderr=""
    )

    # Mock mget_temp output
    def mock_run_side_effect(cmd, *args, **kwargs):
        result = MagicMock()
        if 'lspci' in cmd:
            result.returncode = 0
            result.stdout = "0005:01:00.0 Mellanox Technologies MT27800 Family [ConnectX-5]"
            result.stderr = ""
        elif 'mget_temp' in cmd:
            result.returncode = 0
            result.stdout = "45.5"
            result.stderr = ""
        else:
            result.returncode = 1
            result.stdout = ""
            result.stderr = "Unknown command"
        return result

    mock_run.side_effect = mock_run_side_effect

    with patch('subprocess.run', mock_run):
        with patch('shutil.which', return_value='/usr/bin/mget_temp'):
            mellanox_temps = get_mellanox_temperature()

    # Verify sensor name is 'mlx' (not 'mlx_0005_01_00_0')
    assert 'mlx' in mellanox_temps, "Sensor key 'mlx' not found"
    assert 'mlx_0005_01_00_0' not in mellanox_temps, "Old sensor name format still present"

    # Verify temperature value
    assert mellanox_temps['mlx']['temp'] == 45500.0, f"Expected 45500.0, got {mellanox_temps['mlx']['temp']}"

    # Verify max and crit values
    assert mellanox_temps['mlx']['max'] == 84, f"Expected max=84, got {mellanox_temps['mlx']['max']}"
    assert mellanox_temps['mlx']['crit'] == 100, f"Expected crit=100, got {mellanox_temps['mlx']['crit']}"

    print("✓ Sensor name is correctly shortened to 'mlx'")
    print(f"  Temperature: {mellanox_temps['mlx']['temp']} millidegrees")
    print(f"  Max: {mellanox_temps['mlx']['max']}°C")
    print(f"  Crit: {mellanox_temps['mlx']['crit']}°C")
    return True

def test_temperature_service_with_mlx():
    """Test TemperatureService with Mellanox sensor"""
    print("\nTesting TemperatureService with Mellanox sensor...")

    # Mock subprocess and shutil
    mock_run = MagicMock()

    def mock_run_side_effect(cmd, *args, **kwargs):
        result = MagicMock()
        if 'lspci' in cmd:
            result.returncode = 0
            result.stdout = "0005:01:00.0 Mellanox Technologies MT27800 Family [ConnectX-5]"
            result.stderr = ""
        elif 'mget_temp' in cmd:
            result.returncode = 0
            result.stdout = "45.5"
            result.stderr = ""
        else:
            result.returncode = 1
            result.stdout = ""
            result.stderr = "Unknown command"
        return result

    mock_run.side_effect = mock_run_side_effect

    with patch('subprocess.run', mock_run):
        with patch('shutil.which', return_value='/usr/bin/mget_temp'):
            with patch('os.path.isdir', return_value=False):  # No hwmon/thermal
                service = TemperatureService()
                status = service.get_status()

    # Verify 'mlx' sensor is in status
    assert 'mlx' in status, "Mellanox sensor 'mlx' not found in status"

    # Verify temperature conversion (from millidegrees to Celsius)
    assert abs(status['mlx']['temp'] - 45.5) < 0.01, f"Expected 45.5°C, got {status['mlx']['temp']}°C"

    # Verify max and crit values are in Celsius
    assert status['mlx']['max'] == 84, f"Expected max=84°C, got {status['mlx']['max']}°C"
    assert status['mlx']['crit'] == 100, f"Expected crit=100°C, got {status['mlx']['crit']}°C"

    # Verify online status
    assert status['mlx']['online'] == True, "Sensor should be online"

    print("✓ TemperatureService correctly handles 'mlx' sensor")
    print(f"  Temperature: {status['mlx']['temp']}°C")
    print(f"  Max: {status['mlx']['max']}°C")
    print(f"  Crit: {status['mlx']['crit']}°C")
    print(f"  Online: {status['mlx']['online']}")
    return True

def test_multiple_mellanox_devices():
    """Test that multiple Mellanox devices use the same 'mlx' key"""
    print("\nTesting multiple Mellanox devices...")

    # Mock subprocess to simulate multiple Mellanox devices
    mock_run = MagicMock()

    def mock_run_side_effect(cmd, *args, **kwargs):
        result = MagicMock()
        if 'lspci' in cmd:
            result.returncode = 0
            result.stdout = """0005:01:00.0 Mellanox Technologies MT27800 Family [ConnectX-5]
0005:01:00.1 Mellanox Technologies MT27800 Family [ConnectX-5]"""
            result.stderr = ""
        elif 'mget_temp' in cmd:
            result.returncode = 0
            result.stdout = "45.5"
            result.stderr = ""
        else:
            result.returncode = 1
            result.stdout = ""
            result.stderr = "Unknown command"
        return result

    mock_run.side_effect = mock_run_side_effect

    with patch('subprocess.run', mock_run):
        with patch('shutil.which', return_value='/usr/bin/mget_temp'):
            mellanox_temps = get_mellanox_temperature()

    # Should only have one 'mlx' key (not multiple)
    assert 'mlx' in mellanox_temps, "Sensor key 'mlx' not found"
    assert len([k for k in mellanox_temps.keys() if k.startswith('mlx')]) == 1, \
        "Should only have one 'mlx' key, not multiple"

    print("✓ Multiple Mellanox devices correctly use single 'mlx' key")
    return True

if __name__ == '__main__':
    try:
        test_mellanox_sensor_name()
        test_temperature_service_with_mlx()
        test_multiple_mellanox_devices()
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60)
        print("\nSummary of changes:")
        print("1. Mellanox sensor name shortened from 'mlx_0005_01_00_0' to 'mlx'")
        print("2. Max temperature set to 84°C")
        print("3. Critical temperature set to 100°C")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
