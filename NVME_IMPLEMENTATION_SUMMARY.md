# NVMe Temperature Monitoring Implementation

## Summary
Successfully implemented NVMe temperature monitoring functionality to jetson_stats, similar to the existing MLX (Mellanox) sensor temperature monitoring.

## Changes Made

### File: `jtop/core/temperature.py`

#### 1. Added `get_nvme_temperature()` function
- Detects NVMe devices using `ls /dev/nvme*`
- Reads temperature data using `sudo nvme smart-log <device>`
- Parses temperature from "Temperature Sensor X" lines
- Returns maximum temperature from all sensors on each device
- Stores data in millidegrees for consistency with other sensors

#### 2. Updated `TemperatureService.__init__()`
- Added call to `get_nvme_temperature()` to detect NVMe devices
- Integrates NVMe temperature data into the existing temperature sensor dictionary

#### 3. Updated `TemperatureService.get_status()`
- Added handling for NVMe sensors (similar to Mellanox sensors)
- NVMe sensors require fresh data on each read (like Mellanox)
- Properly marks sensors as offline if not available

## Features

- **Automatic Detection**: Automatically detects all NVMe devices in `/dev/nvme*`
- **Multiple Sensors**: Handles devices with multiple temperature sensors (Sensor 1, Sensor 2, etc.)
- **Max Temperature**: Reports the maximum temperature from all sensors on each device
- **Default Thresholds**: Uses default max (84°C) and critical (100°C) thresholds
- **Error Handling**: Gracefully handles missing nvme command or devices
- **Consistent Format**: Follows the same data format as other temperature sensors

## Usage

When NVMe devices are present, they will appear in the temperature readings with the prefix `nvme_` followed by the device name (e.g., `nvme_nvme0`).

Example output format:
```python
{
    'nvme_nvme0': {
        'temp': 54000.0,  # Temperature in millidegrees (54.00°C)
        'max': 84,        # Max threshold in °C
        'crit': 100,      # Critical threshold in °C
        'online': True
    }
}
```

## Requirements

- `nvme` command must be installed (typically part of `nvme-cli` package)
- `sudo` privileges required to run `nvme smart-log` (handled automatically)
- NVMe devices must be present in the system

## Testing

Created comprehensive tests:
- `test_nvme_temp.py`: Tests real NVMe device detection
- `test_nvme_mock.py`: Tests with mocked NVMe output data
- All tests pass successfully

## Compatibility

- Works alongside existing temperature sensors (MLX, virtual thermal, hwmon)
- No breaking changes to existing functionality
- Follows the same patterns as Mellanox temperature implementation
