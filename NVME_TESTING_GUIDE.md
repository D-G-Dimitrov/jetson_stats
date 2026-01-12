# NVMe Temperature Monitoring - Testing Guide

## Overview

This guide explains how to test and use the NVMe temperature monitoring feature that has been added to jetson_stats.

## Implementation Summary

The NVMe temperature monitoring feature:
- Detects NVMe SSDs automatically
- Reads temperature from all sensors on each device
- Reports the maximum temperature from all sensors
- Displays temperatures in the jtop interface with the prefix `nvme_` (e.g., `nvme_nvme0`)

## Prerequisites

Before testing, ensure your Jetson device has:

1. **NVMe SSD installed** - The device must have an NVMe SSD connected
2. **nvme-cli package** - Required to read NVMe smart data
3. **sudo privileges** - Required to run `nvme smart-log` command

## Installation

Install the nvme-cli package if not already installed:

```bash
sudo apt-get update
sudo apt-get install nvme-cli
```

## Testing the Implementation

### Method 1: Manual Testing (Recommended)

1. **Check if NVMe device exists**:
   ```bash
   ls /dev/nvme*
   ```
   Expected output: `/dev/nvme0` (or similar)

2. **Test nvme command manually**:
   ```bash
   sudo nvme smart-log /dev/nvme0
   ```
   Look for lines like:
   ```
   Temperature Sensor 1           : 48 C (321 Kelvin)
   Temperature Sensor 2           : 54 C (327 Kelvin)
   ```

3. **Run the test script**:
   ```bash
   python3 test_nvme_on_jetson.py
   ```
   This will show all detected temperature sensors including NVMe sensors.

### Method 2: Integration Test

Run the integration test to verify the feature works with mocked data:

```bash
python3 test_jtop_nvme_integration.py
```

This test simulates NVMe output and verifies the integration with jtop.

### Method 3: Using jtop Directly

1. **Start jtop service** (if not running):
   ```bash
   sudo systemctl start jtop
   ```

2. **Run jtop**:
   ```bash
   jtop
   ```

3. **Check temperature readings**:
   - Look for sensors with the prefix `nvme_` (e.g., `nvme_nvme0`)
   - The temperature will be displayed along with other sensors

## Expected Output

When NVMe temperature monitoring is working correctly, you should see output similar to:

```
Testing NVMe temperature on Jetson device...
======================================================================
Total temperature sensors detected: 5

✅ Found 1 NVMe sensor(s):

Sensor: nvme_nvme0
  Temperature: 54.00°C
  Max threshold: 84°C
  Critical threshold: 100°C
  Status: Online

======================================================================
✅ NVMe temperature monitoring is working correctly!
======================================================================
```

## Troubleshooting

### No NVMe sensors detected

**Symptom**: The test script reports "No NVMe sensors detected."

**Solutions**:

1. **Check NVMe device exists**:
   ```bash
   ls /dev/nvme*
   ```
   If no devices are listed, your Jetson may not have an NVMe SSD installed.

2. **Install nvme-cli**:
   ```bash
   sudo apt-get install nvme-cli
   ```

3. **Check nvme command works**:
   ```bash
   sudo nvme smart-log /dev/nvme0
   ```
   If this fails, there may be a permissions issue or the device is not properly connected.

4. **Check kernel support**:
   Ensure your Jetson's kernel has NVMe support compiled in.

### Permission denied errors

**Symptom**: Errors about permission denied when running nvme commands.

**Solution**:

1. Add your user to the sudoers file for passwordless sudo:
   ```bash
   sudo visudo
   ```
   Add this line (replace `username` with your actual username):
   ```
   username ALL=(ALL) NOPASSWD: /usr/sbin/nvme
   ```

2. Alternatively, you can run jtop with sudo:
   ```bash
   sudo jtop
   ```

## Technical Details

### How It Works

1. **Detection**: The system scans `/dev/nvme*` for NVMe devices
2. **Reading**: For each device, it runs `sudo nvme smart-log <device>`
3. **Parsing**: Extracts temperature values from "Temperature Sensor X" lines
4. **Calculation**: Computes the maximum temperature from all sensors
5. **Display**: Shows the temperature in jtop with the format `nvme_<device_name>`

### Data Format

NVMe temperatures are stored in the same format as other sensors:
- **Temperature**: Value in millidegrees (e.g., 54000.0 = 54.00°C)
- **Max threshold**: 84°C (default)
- **Critical threshold**: 100°C (default)
- **Online status**: True if sensor is accessible

## Verification

To verify the implementation is complete:

1. ✅ NVMe temperature reading function implemented
2. ✅ Integration with TemperatureService
3. ✅ Proper error handling
4. ✅ Consistent data format with other sensors
5. ✅ Comprehensive test coverage
6. ✅ Documentation provided

## Support

If you encounter any issues, please check:
- The NVME_IMPLEMENTATION_SUMMARY.md file for technical details
- The test scripts for examples of expected behavior
- The troubleshooting section above for common issues
