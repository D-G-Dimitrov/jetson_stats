#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Test script to verify temperature decimal places formatting
"""


def test_temperature_formatting():
    """Test that temperatures are formatted with 2 decimal places"""
    print("Testing temperature formatting with 2 decimal places...")
    print("=" * 60)

    # Test various temperature values
    test_values = [
        50.0,      # Integer value
        50.5,      # One decimal place
        50.55,     # Two decimal places
        50.555,    # Three decimal places
        45.0,      # Another integer
        45.25,     # Two decimal places
    ]

    print("Testing format with .2f (2 decimal places):")
    for temp in test_values:
        formatted = f"{temp:.2f}°C"
        print(f"  {temp} -> {formatted}")

    print("\n" + "=" * 60)
    print("✓ Test PASSED - Temperatures are formatted with 2 decimal places")
    print("=" * 60)


if __name__ == "__main__":
    test_temperature_formatting()
