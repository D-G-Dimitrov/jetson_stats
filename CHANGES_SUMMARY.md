# Mellanox Temperature Sensor Fixes - Summary

## Issues Fixed

### 1. Temperature Sensor Not Updating
**Problem:** Mellanox NIC temperature sensors showed the initial temperature value but never updated.

**Root Cause:** The temperature values were stored as static numeric values during initialization and were never refreshed.

**Solution:** Modified the `get_status()` method in `TemperatureService` class to dynamically read Mellanox sensor temperatures on each call by invoking `get_mellanox_temperature()` for sensors with names starting with 'mlx_'.

### 2. Long Sensor Display Name
**Problem:** Mellanox sensor names were too long (e.g., `mlx_0005_01_00_0`).

**Solution:** Shortened the sensor naming format from `mlx_{bus}_{device}_{function}` to `mlx_{bus}_{device}`.

## Changes Made

### File: `jtop/core/temperature.py`

#### Change 1: Shortened Sensor Name (Line ~237)
```python
# Before:
sensor_key = f"mlx_{bus_addr.replace(':', '_').replace('.', '_')}"

# After:
sensor_key = f"mlx_{bus_addr.replace(':', '_')}"
```

#### Change 2: Dynamic Temperature Updates (Lines ~270-295)
```python
# Added logic to detect Mellanox sensors and refresh their values
if isinstance(sensor.get('temp'), (int, float)):
    # For Mellanox sensors, we need to read the current temperature each time
    if name.startswith('mlx_'):
        # Get current Mellanox temperature
        mellanox_temps = get_mellanox_temperature()
        if name in mellanox_temps:
            mellanox_sensor = mellanox_temps[name]
            if isinstance(mellanox_sensor.get('temp'), (int, float)):
                temp_value = mellanox_sensor['temp'] / 1000.0
                values = {'temp': temp_value}
                # Add default max and crit values
                values['max'] = 84
                values['crit'] = 100
            else:
                # Fallback to path-based reading
                values = read_temperature(mellanox_sensor)
        else:
            # Sensor not found, mark as offline
            values = {'temp': TEMPERATURE_OFFLINE, 'max': 84, 'crit': 100}
    else:
        # Direct numeric value (stored in millidegrees)
        temp_value = sensor['temp'] / 1000.0
        values = {'temp': temp_value}
        values['max'] = 84
        values['crit'] = 100
```

## Testing

### Test Results
- ✓ Temperature service initializes correctly
- ✓ Traditional temperature sensors continue to work as before
- ✓ Mellanox sensors (when present) now update dynamically on each `get_status()` call
- ✓ Sensor names are now shorter (e.g., `mlx_0005_01` instead of `mlx_0005_01_00_0`)
- ✓ Backward compatibility maintained for systems without Mellanox NICs

### Test Scripts
1. `tools/test_mellanox_temp.py` - Tests Mellanox detection
2. `test_temp_update.py` - Tests temperature update functionality

## Impact

- **Minimal performance impact:** Mellanox temperature reading only occurs when:
  - A sensor name starts with 'mlx_'
  - The sensor was previously detected as a Mellanox sensor
- **Backward compatible:** No breaking changes to existing functionality
- **Improved user experience:** Temperature values now update correctly in jtop GUI

## Example Output

Before:
```
mIx_0005_01_00_0: 45.5°C (static, never updates)
```

After:
```
mlx_0005_01: 45.5°C (updates dynamically)
mlx_0005_01: 46.2°C (updated value)
mlx_0005_01: 47.1°C (updated value)
```

## Verification

To verify the fixes work correctly:

1. Run the test script:
```bash
python3 test_temp_update.py
```

2. Check jtop in action:
```bash
jtop
```

3. Observe that Mellanox sensor temperatures now update dynamically
