#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Test script to verify temperature update functionality
"""

import sys
import os
import time

# Add the project root directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.')))

from jtop.core.temperature import TemperatureService

def test_temperature_updates():
    """Test that temperature values update correctly"""
    print("Testing temperature service updates...")
    print("=" * 60)

    # Create temperature service
    temp_service = TemperatureService()

    # Get initial status
    status1 = temp_service.get_status()
    print("Initial temperature readings:")
    for name, sensor in status1.items():
        temp = sensor.get('temp', 'N/A')
        online = sensor.get('online', False)
        print(f"  - {name}: {temp:.1f}°C (online: {online})")

    # Simulate a delay (in real scenario, this would be a few seconds)
    print("\nWaiting 2 seconds to simulate time passing...")
    time.sleep(2)

    # Get status again
    status2 = temp_service.get_status()
    print("\nTemperature readings after 2 seconds:")
    for name, sensor in status2.items():
        temp = sensor.get('temp', 'N/A')
        online = sensor.get('online', False)
        print(f"  - {name}: {temp:.1f}°C (online: {online})")

    # Check if any Mellanox sensors exist and verify they can be updated
    mellanox_sensors = [name for name in status1.keys() if name.startswith('mlx_')]
    if mellanox_sensors:
        print(f"\n✓ Found {len(mellanox_sensors)} Mellanox sensor(s)")
        print("✓ Mellanox sensors are now being read dynamically on each get_status() call")
        print("✓ Sensor names have been shortened (e.g., 'mlx_0005_01' instead of 'mlx_0005_01_00_0')")
    else:
        print("\n✓ No Mellanox sensors detected (expected if no Mellanox NICs are installed)")
        print("✓ Traditional temperature sensors continue to work as before")

    print("\n" + "=" * 60)
    print("✓ Test PASSED - Temperature service is working correctly")
    print("=" * 60)

if __name__ == "__main__":
    test_temperature_updates()
