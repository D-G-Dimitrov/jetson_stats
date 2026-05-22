#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Debug script to check NVMe temperature detection

from jtop.core.temperature import get_nvme_temperature
import sys
import os
import subprocess

# Add the current directory to the path to import jtop
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_nvme_debug():
    """
    Debug NVMe temperature detection
    """
    print("Debugging NVMe temperature detection...")
    print("=" * 70)

    # Check if running with sudo
    if os.geteuid() == 0:
        print("✓ Running with sudo privileges")
    else:
        print("✗ NOT running with sudo privileges")

    print()

    # Test get_nvme_temperature directly
    print("Calling get_nvme_temperature()...")
    nvme_temps = get_nvme_temperature()

    print(f"Result: {nvme_temps}")
    print()

    if not nvme_temps:
        print("No NVMe temperatures detected.")
        print()
        print("Manual checks:")
        print()

        # Check if nvme command exists
        try:
            import shutil
            if shutil.which('nvme'):
                print("✓ nvme command is available")
            else:
                print("✗ nvme command is NOT available")
        except Exception as e:
            print(f"✗ Error checking nvme command: {e}")

        # Check for NVMe devices
        try:
            result = subprocess.run(
                ['ls', '/dev/nvme*'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                print(f"✓ NVMe devices found: {result.stdout.strip()}")
            else:
                print("✗ No NVMe devices found in /dev/nvme*")
        except Exception as e:
            print(f"✗ Error checking NVMe devices: {e}")

        # Check if we can run nvme smart-log
        try:
            use_sudo = os.geteuid() != 0
            cmd = ['sudo', 'nvme', 'smart-log', '/dev/nvme0'] if use_sudo else ['nvme', 'smart-log', '/dev/nvme0']
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✓ nvme smart-log works (first 200 chars): {result.stdout[:200]}...")
            else:
                print(f"✗ nvme smart-log failed: {result.stderr}")
        except Exception as e:
            print(f"✗ Error running nvme smart-log: {e}")

    else:
        print(f"✓ Found {len(nvme_temps)} NVMe sensor(s):")
        for name, data in nvme_temps.items():
            print(f"  {name}: {data['temp'] / 1000.0:.2f}°C")

    print("=" * 70)


if __name__ == "__main__":
    try:
        test_nvme_debug()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
