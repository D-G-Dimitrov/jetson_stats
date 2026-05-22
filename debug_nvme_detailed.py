#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Detailed debug script for NVMe temperature detection

import sys
import os
import subprocess
import shutil

# Add the current directory to the path to import jtop
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def debug_nvme_detection():
    """
    Detailed debugging of NVMe temperature detection
    """
    print("Detailed NVMe temperature detection debug...")
    print("=" * 70)

    # Check 1: Running with sudo
    print("\n1. Sudo privileges check:")
    if os.geteuid() == 0:
        print("   ✓ Running as root (euid = 0)")
    else:
        print(f"   ✗ NOT running as root (euid = {os.geteuid()})")

    # Check 2: nvme command availability
    print("\n2. nvme command check:")
    if shutil.which('nvme'):
        print("   ✓ nvme command found")
    else:
        print("   ✗ nvme command NOT found")

    # Check 3: NVMe devices
    print("\n3. NVMe devices check:")
    try:
        result = subprocess.run(
            ['ls', '/dev/nvme[0-9]*'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"   ✓ Found devices: {result.stdout.strip()}")
        else:
            print("   ✗ No NVMe controller devices found")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Check 4: Manual nvme smart-log test
    print("\n4. Manual nvme smart-log test:")
    try:
        use_sudo = os.geteuid() != 0
        cmd = ['sudo', 'nvme', 'smart-log', '/dev/nvme0'] if use_sudo else ['nvme', 'smart-log', '/dev/nvme0']
        print(f"   Command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("   ✓ Command succeeded")
            print(f"   Output (first 300 chars): {result.stdout[:300]}...")
        else:
            print(f"   ✗ Command failed with return code {result.returncode}")
            print(f"   stderr: {result.stderr}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Check 5: Test get_nvme_temperature function
    print("\n5. Testing get_nvme_temperature() function:")
    try:
        from jtop.core.temperature import get_nvme_temperature
        nvme_temps = get_nvme_temperature()
        print(f"   Result: {nvme_temps}")
        if nvme_temps:
            print("   ✓ NVMe temperatures detected!")
            for name, data in nvme_temps.items():
                print(f"     {name}: {data['temp'] / 1000.0:.2f}°C")
        else:
            print("   ✗ No NVMe temperatures detected")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()

    # Check 6: Test TemperatureService
    print("\n6. Testing TemperatureService:")
    try:
        from jtop.core.temperature import TemperatureService
        temp_service = TemperatureService()
        all_sensors = temp_service.get_status()

        print(f"   Total sensors: {len(all_sensors)}")
        nvme_sensors = {name: data for name, data in all_sensors.items()
                        if name.startswith('nvme_')}
        print(f"   NVMe sensors: {len(nvme_sensors)}")

        if nvme_sensors:
            print("   ✓ NVMe sensors found in service!")
            for name, data in nvme_sensors.items():
                print(f"     {name}: {data}")
        else:
            print("   ✗ No NVMe sensors in service")

        # Debug internal state
        print("\n   Internal service state:")
        print(f"   Service._temperature keys: {list(temp_service._temperature.keys())}")
        for key, value in temp_service._temperature.items():
            if key.startswith('nvme'):
                print(f"     {key}: {value}")

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        debug_nvme_detection()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
