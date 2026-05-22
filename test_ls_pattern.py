#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Test ls pattern matching

import subprocess


def test_ls_pattern():
    """
    Test if ls /dev/nvme[0-9]* finds the right devices
    """
    print("Testing ls pattern matching...")
    print("=" * 70)

    # Test the exact command from the code
    result = subprocess.run(
        ['ls', '/dev/nvme[0-9]*'],
        capture_output=True,
        text=True,
        timeout=5
    )

    print(f"Return code: {result.returncode}")
    print(f"stdout: {result.stdout!r}")
    print(f"stderr: {result.stderr!r}")

    if result.returncode == 0 and result.stdout.strip():
        devices = result.stdout.strip().split('\n')
        print(f"\nFound {len(devices)} device(s):")
        for device in devices:
            if device.strip():
                print(f"  - {device.strip()}")
    else:
        print("\nNo devices found")

    print("=" * 70)


if __name__ == "__main__":
    test_ls_pattern()
