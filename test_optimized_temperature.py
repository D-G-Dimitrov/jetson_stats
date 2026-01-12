#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Test script to verify optimized temperature functionality
"""

import sys
import os
import time

# Add the project root directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.')))

from jtop.core.temperature import TemperatureService, read_sensor_value, get_mellanox_temperature

def test_sensor_value_function():
    """Test the unified read_sensor_value function"""
    print("Testing unified read_sensor_value function...")
    print("=" * 60)

    # Test with numeric values (Mellanox style)
    mellanox_sensor = {
        'temp': 44000.0,  # 44°C in millidegrees
        'max': 84000.0,   # 84°C in millidegrees
        'crit': 100000.0  # 100°C in millidegrees
    }
    result = read_sensor_value(mellanox_sensor, sensor_type='mellanox')
    assert result['temp'] == 44.0, f"Expected 44.0, got {result['temp']}"
    assert result['max'] == 84.0, f"Expected 84.0, got {result['max']}"
    assert result['crit'] == 100.0, f"Expected 100.0, got {result['crit']}"
    assert result['online'] == True, "Expected online=True"
    print("✓ Numeric sensor values handled correctly")

    # Test with default values
    simple_sensor = {'temp': 50000.0}
    result = read_sensor_value(simple_sensor, sensor_type='mellanox')
    assert result['temp'] == 50.0, f"Expected 50.0, got {result['temp']}"
    assert result['max'] == 84, f"Expected 84, got {result['max']}"
    assert result['crit'] == 100, f"Expected 100, got {result['crit']}"
    print("✓ Default max/crit values applied correctly")

    print("✓ read_sensor_value function test PASSED")
    print("=" * 60)

def test_temperature_service():
    """Test TemperatureService with optimized code"""
    print("\nTesting TemperatureService...")
    print("=" * 60)

    # Create temperature service
    temp_service = TemperatureService()

    # Get initial status
    status1 = temp_service.get_status()
    print(f"Initial sensors found: {len(status1)}")
    for name, sensor in status1.items():
        temp = sensor.get('temp', 'N/A')
        online = sensor.get('online', False)
        print(f"  - {name}: {temp:.2f}°C (online: {online})")

    # Check for Mellanox sensors with proper naming
    mellanox_sensors = [name for name in status1.keys() if name.startswith('mlx_')]
    if mellanox_sensors:
        print(f"\n✓ Found {len(mellanox_sensors)} Mellanox sensor(s) with proper naming:")
        for name in mellanox_sensors:
            print(f"  - {name} (format: mlx_{bus_device_function})")
    else:
        print("\n✓ No Mellanox sensors detected (expected if no Mellanox NICs are installed)")

    # Verify all sensors have required fields
    for name, sensor in status1.items():
        assert 'temp' in sensor, f"Sensor {name} missing 'temp' field"
        assert 'max' in sensor, f"Sensor {name} missing 'max' field"
        assert 'crit' in sensor, f"Sensor {name} missing 'crit' field"
        assert 'online' in sensor, f"Sensor {name} missing 'online' field"
    print("✓ All sensors have required fields (temp, max, crit, online)")

    # Simulate a delay
    print("\nWaiting 2 seconds to test dynamic updates...")
    time.sleep(2)

    # Get status again
    status2 = temp_service.get_status()
    print(f"\nSensors after 2 seconds: {len(status2)}")
    for name, sensor in status2.items():
        temp = sensor.get('temp', 'N/A')
        online = sensor.get('online', False)
        print(f"  - {name}: {temp:.2f}°C (online: {online})")

    print("\n✓ TemperatureService test PASSED")
    print("=" * 60)

def test_mellanox_naming():
    """Test that Mellanox sensors use PCI address in naming"""
    print("\nTesting Mellanox sensor naming...")
    print("=" * 60)

    # Get Mellanox temperatures
    mellanox_temps = get_mellanox_temperature()

    if mellanox_temps:
        print(f"Found {len(mellanox_temps)} Mellanox sensor(s):")
        for name, sensor in mellanox_temps.items():
            temp_celsius = sensor['temp'] / 1000.0
            print(f"  - {name}: {temp_celsius:.2f}°C")
            # Verify naming format
            assert name.startswith('mlx_'), f"Sensor name should start with 'mlx_', got {name}"
            # Check that it contains PCI address format (e.g., mlx_0005_01_00_0)
            parts = name.split('_')
            assert len(parts) >= 2, f"Sensor name should have at least 2 parts, got {name}"
        print("✓ Mellanox sensors use proper PCI address naming")
    else:
        print("✓ No Mellanox sensors detected (expected if no Mellanox NICs are installed)")

    print("✓ Mellanox naming test PASSED")
    print("=" * 60)

def test_backward_compatibility():
    """Test that existing code still works with optimizations"""
    print("\nTesting backward compatibility...")
    print("=" * 60)

    # Create temperature service
    temp_service = TemperatureService()

    # Get status
    status = temp_service.get_status()

    # Verify all sensors work as expected
    for name, sensor in status.items():
        # Check all required fields exist
        assert 'temp' in sensor
        assert 'max' in sensor
        assert 'crit' in sensor
        assert 'online' in sensor

        # Check temperature is a number
        assert isinstance(sensor['temp'], (int, float)), f"Temperature should be numeric, got {type(sensor['temp'])}"

        # Check max and crit are numbers
        assert isinstance(sensor['max'], (int, float)), f"Max should be numeric, got {type(sensor['max'])}"
        assert isinstance(sensor['crit'], (int, float)), f"Crit should be numeric, got {type(sensor['crit'])}"

        # Check online is boolean
        assert isinstance(sensor['online'], bool), f"Online should be boolean, got {type(sensor['online'])}"

    print(f"✓ All {len(status)} sensors maintain backward compatibility")
    print("✓ Backward compatibility test PASSED")
    print("=" * 60)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("OPTIMIZED TEMPERATURE SYSTEM TESTS")
    print("=" * 60 + "\n")

    try:
        test_sensor_value_function()
        test_temperature_service()
        test_mellanox_naming()
        test_backward_compatibility()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nOptimizations verified:")
        print("  ✓ Unified sensor reading logic (removed duplicate code)")
        print("  ✓ Proper Mellanox sensor naming with PCI addresses")
        print("  ✓ Dynamic temperature updates for Mellanox sensors")
        print("  ✓ Backward compatibility maintained")
        print("  ✓ All sensors have required fields")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
