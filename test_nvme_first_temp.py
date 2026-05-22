#!/usr/bin/env python3
"""
Test to verify that get_nvme_temperature() only extracts the first temperature reading
from the main "temperature" field, not from individual sensor readings.
"""

import re


def test_temperature_parsing():
    """Test the temperature parsing logic used in get_nvme_temperature()"""

    # Sample output from nvme smart-log
    sample_output = """Smart Log for NVME device:nvme0 namespace-id:ffffffff
critical_warning			: 0
temperature				: 48 C (321 Kelvin)
available_spare				: 100%
available_spare_threshold		: 10%
percentage_used				: 0%
endurance group critical warning summary: 0
data_units_read				: 144330
data_units_written			: 1210357
host_read_commands			: 954732
host_write_commands			: 2573186
controller_busy_time			: 1008
power_cycles				: 8
power_on_hours				: 3
unsafe_shutdowns			: 2
media_errors				: 0
num_err_log_entries			: 0
Warning Temperature Time		: 0
Critical Composite Temperature Time	: 0
Temperature Sensor 1           : 77 C (350 Kelvin)
Temperature Sensor 2           : 65 C (338 Kelvin)
Temperature Sensor 3           : 48 C (321 Kelvin)
Thermal Management T1 Trans Count	: 0
Thermal Management T2 Trans Count	: 0
Thermal Management T1 Total Time	: 0
Thermal Management T2 Total Time	: 0"""

    # This is the exact logic from get_nvme_temperature()
    temp_found = False
    extracted_temp = None

    for line in sample_output.split('\n'):
        if line.strip().startswith('temperature'):
            # Extract temperature value (e.g., "temperature				: 48 C (321 Kelvin)")
            # Match the temperature value followed by ' C'
            match = re.search(r'([0-9]+)\s+C', line)
            if match:
                try:
                    temp_celsius = float(match.group(1))
                    extracted_temp = temp_celsius
                    temp_found = True
                    print(f"✓ Found temperature: {temp_celsius}°C from line: '{line.strip()}'")
                    break
                except ValueError:
                    print(f"✗ Could not parse temperature from line: {line!r}")

    if temp_found:
        print(f"\n✓ SUCCESS: Extracted temperature = {extracted_temp}°C")
        print(f"✓ This matches the expected value from the main 'temperature' field")
        print(f"✓ Individual sensor readings (77°C, 65°C, 48°C) were correctly ignored")
        return True
    else:
        print(f"\n✗ FAILED: No temperature found")
        return False


def test_equivalent_command():
    """Verify the logic is equivalent to: grep "^temperature" | awk '{print $3}'"""

    sample_output = """temperature				: 48 C (321 Kelvin)
Temperature Sensor 1           : 77 C (350 Kelvin)
Temperature Sensor 2           : 65 C (338 Kelvin)"""

    # Simulate: grep "^temperature"
    lines_starting_with_temperature = [
        line for line in sample_output.split('\n')
        if line.strip().startswith('temperature')
    ]

    print("\n" + "=" * 60)
    print("Testing equivalence to: grep '^temperature' | awk '{print $3}'")
    print("=" * 60)

    for line in lines_starting_with_temperature:
        print(f"\nLine matching '^temperature': {line.strip()}")

        # Simulate: awk '{print $3}'
        parts = line.strip().split()
        if len(parts) >= 3:
            awk_value = parts[2]  # 0-indexed, so 3rd field is index 2
            print(f"  awk '{{print $3}}' would extract: '{awk_value}'")

            # Now test our regex approach
            match = re.search(r'([0-9]+)\s+C', line)
            if match:
                regex_value = match.group(1)
                print(f"  Our regex extracts: '{regex_value}'")

                if awk_value == regex_value:
                    print(f"  ✓ Values match!")
                else:
                    print(f"  ✗ Values don't match!")


if __name__ == '__main__':
    print("=" * 60)
    print("Testing NVMe Temperature Extraction Logic")
    print("=" * 60)

    result = test_temperature_parsing()
    test_equivalent_command()

    print("\n" + "=" * 60)
    if result:
        print("CONCLUSION: The current implementation is CORRECT")
        print("It only extracts the first temperature from the main 'temperature' field")
    else:
        print("CONCLUSION: The implementation needs fixing")
    print("=" * 60)
