#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Test to reproduce the NVMe temperature detection issue

import sys
import os

# Add the current directory to the path to import jtop
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jtop.core.temperature import TemperatureService, get_nvme_temperature

def test_issue_reproduction():
    """
    Reproduce the NVMe temperature detection issue
    """
    print("Reproducing NVMe temperature detection issue...")
    print("=" * 70)

    # Test 1: Call get_nvme_temperature directly
    print("\n1. Testing get_nvme_temperature() directly:")
    nvme_temps = get_nvme_temperature()
    print(f"   Result: {nvme_temps}")

    # Test 2: Create TemperatureService and check initialization
    print("\n2. Testing TemperatureService initialization:")
    temp_service = TemperatureService()
    all_sensors = temp_service.get_status()

    print(f"   Total sensors detected: {len(all_sensors)}")
    nvme_sensors = {name: data for name, data in all_sensors.items()
                   if name.startswith('nvme_')}
    print(f"   NVMe sensors found: {len(nvme_sensors)}")

    if nvme_sensors:
        print("   ✅ NVMe sensors detected in get_status()!")
        for name, data in nvme_sensors.items():
            print(f"     {name}: {data}")
    else:
        print("   ❌ No NVMe sensors detected in get_status()")

    # Test 3: Check what's stored in the service
    print("\n3. Checking internal service state:")
    print(f"   Service._temperature keys: {list(temp_service._temperature.keys())}")
    for key, value in temp_service._temperature.items():
        if key.startswith('nvme'):
            print(f"     {key}: {value}")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        test_issue_reproduction()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
