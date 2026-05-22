#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Mock test for NVMe temperature reading functionality

from jtop.core.temperature import get_nvme_temperature
import sys
import os
from unittest.mock import patch, MagicMock

# Add the current directory to the path to import jtop
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_nvme_with_mock():
    """Test NVMe temperature reading with mocked nvme command"""
    print("Testing NVMe temperature reading with mock data...")
    print("=" * 60)

    # Mock the subprocess.run to simulate nvme smart-log output
    mock_output = """Smart Log for NVME device:nvme0 namespace-id:ffffffff
critical_warning                        : 0
temperature                             : 48 C (321 Kelvin)
available_spare                         : 100%
available_spare_threshold               : 10%
percentage_used                         : 1%
endurance group critical warning summary: 0
data_units_read                         : 83159341
data_units_written                      : 48220461
host_read_commands                      : 800657575
host_write_commands                     : 277362220
controller_busy_time                    : 807
power_cycles                            : 405
power_on_hours                          : 562
unsafe_shutdowns                        : 30
media_errors                            : 0
num_err_log_entries                     : 0
Warning Temperature Time                : 0
Critical Composite Temperature Time     : 0
Temperature Sensor 1           : 48 C (321 Kelvin)
Temperature Sensor 2           : 54 C (327 Kelvin)
Thermal Management T1 Trans Count       : 0
Thermal Management T2 Trans Count       : 0
Thermal Management T1 Total Time        : 0
Thermal Management T2 Total Time        : 0
"""

    with patch('jtop.core.temperature.shutil.which') as mock_which, \
            patch('jtop.core.temperature.subprocess.run') as mock_run:

        # Mock nvme command availability
        mock_which.return_value = '/usr/sbin/nvme'

        # Mock ls command to find NVMe devices
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='/dev/nvme0\n/dev/nvme0n1\n',
            stderr=''
        )

        # First call is for ls /dev/nvme*
        # Second call is for sudo nvme smart-log /dev/nvme0
        # Third call is for sudo nvme smart-log /dev/nvme0n1
        call_count = [0]

        def run_side_effect(cmd, *args, **kwargs):
            if cmd[0] == 'ls':
                return MagicMock(
                    returncode=0,
                    stdout='/dev/nvme0\n/dev/nvme0n1\n',
                    stderr=''
                )
            elif cmd[0] == 'sudo' and len(cmd) > 1 and cmd[1] == 'nvme' and 'smart-log' in cmd:
                return MagicMock(
                    returncode=0,
                    stdout=mock_output,
                    stderr=''
                )
            return MagicMock(returncode=0, stdout='', stderr='')

        mock_run.side_effect = run_side_effect

        # Test the function
        temperatures = get_nvme_temperature()

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
            print(f"  Expected: 54.00°C (max of Sensor 1: 48°C and Sensor 2: 54°C)")
            print()

        # Verify the temperature is correct (should be max of 48 and 54 = 54)
        assert len(temperatures) == 1, f"Expected 1 NVMe device, got {len(temperatures)}"
        assert 'nvme_nvme0' in temperatures, "Expected nvme_nvme0 in temperatures"
        assert temperatures['nvme_nvme0']['temp'] == 54000.0, f"Expected 54000.0, got {temperatures['nvme_nvme0']['temp']}"

        print("=" * 60)
        print("✓ Mock NVMe temperature reading test passed successfully!")
        return True


if __name__ == "__main__":
    try:
        success = test_nvme_with_mock()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
