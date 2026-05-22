#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Test script to verify NVMe temperature on Jetson device
# Run this script on your Jetson device with NVMe SSD installed
# NOTE: This script must be run with sudo privileges to access NVMe devices

from jtop.core.temperature import TemperatureService
import sys
import os

# Add the current directory to the path to import jtop
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_nvme_on_jetson():
    """
    Test NVMe temperature detection on actual Jetson hardware
    """
    print("Testing NVMe temperature on Jetson device...")
    print("=" * 70)

    # Check if running with sudo
    if os.geteuid() != 0:
        print("⚠️  WARNING: This script should be run with sudo privileges")
        print("   Run: sudo python3 test_nvme_on_jetson.py")
        print()

    # Create TemperatureService instance
    temp_service = TemperatureService()

    # Get all temperature sensors
    all_sensors = temp_service.get_status()

    print(f"Total temperature sensors detected: {len(all_sensors)}")
    print()

    # Filter NVMe sensors
    nvme_sensors = {name: data for name, data in all_sensors.items()
                    if name.startswith('nvme_')}

    if not nvme_sensors:
        print("No NVMe sensors detected.")
        print()
        print("Troubleshooting:")
        print("1. Check if NVMe device exists: ls /dev/nvme*")
        print("2. Check if nvme-cli is installed: sudo apt-get install nvme-cli")
        print("3. Test manual reading: sudo nvme smart-log /dev/nvme0")
        print("4. Ensure you're running this script with sudo")
        return False

    print(f"✅ Found {len(nvme_sensors)} NVMe sensor(s):")
    print()

    for name, data in nvme_sensors.items():
        print(f"Sensor: {name}")
        print(f"  Temperature: {data['temp']:.2f}°C")
        print(f"  Max threshold: {data['max']}°C")
        print(f"  Critical threshold: {data['crit']}°C")
        print(f"  Status: {'Online' if data['online'] else 'Offline'}")
        print()

    print("=" * 70)
    print("✅ NVMe temperature monitoring is working correctly!")
    print("=" * 70)

    return True


if __name__ == "__main__":
    try:
        success = test_nvme_on_jetson()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
