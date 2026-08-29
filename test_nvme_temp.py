#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Test script for NVMe temperature reading functionality

import sys
import os

# Add the current directory to the path to import jtop
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jtop.core.temperature import get_nvme_temperature

def test_nvme_temperature():
    """Test NVMe temperature reading functionality"""
    print("Testing NVMe temperature reading...")
    print("=" * 60)

    # Test the get_nvme_temperature function
    temperatures = get_nvme_temperature()

    if not temperatures:
        print("No NVMe devices found or nvme command not available")
        print("This is expected if you don't have NVMe devices")
        return True

    print(f"Found {len(temperatures)} NVMe device(s):")
    print()

    for name, sensor in temperatures.items():
        temp_celsius = sensor['temp'] / 1000.0
        max_temp = sensor['max']
        crit_temp = sensor['crit']
        print(f"Device: {name}")
        print(f"  Temperature: {temp_celsius:.2f}°C")
        print(f"  Max: {max_temp}°C")
        print(f"  Critical: {crit_temp}°C")
        print()

    print("=" * 60)
    print("✓ NVMe temperature reading test completed successfully!")
    return True

if __name__ == "__main__":
    try:
        success = test_nvme_temperature()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
