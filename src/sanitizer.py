"""Section 1: Coding Logic & Sanitization.

Problem: Clean and Normalize Sensor Readings
Takes a list of mixed inputs (strings, None, numbers, negative error flags)
and returns a cleaned list of floats by applying:
1. Type Conversion & Filtering: Convert to float where possible, drop non-convertible, None, or < 0.
2. Clipping: If any valid number > 500.0, cap/limit it to 500.0.
3. Edge Case Handling: Handle empty lists or lists with entirely invalid entries gracefully.
"""

from typing import Any, List
import math


def clean_and_normalize_sensor_readings(sensor_values: Any) -> List[float]:
    """Clean and normalize a list of mixed sensor readings.

    Args:
        sensor_values: Iterable containing sensor readings of various types
            (e.g., str, float, int, None, etc.).

    Returns:
        List[float]: Cleaned, non-negative floats clipped to a maximum of 500.0.
                     Returns an empty list if input is invalid or contains no valid readings.
    """
    if sensor_values is None:
        return []

    if not isinstance(sensor_values, (list, tuple)):
        # Handle cases where input might be another iterable or invalid type
        try:
            sensor_values = list(sensor_values)
        except TypeError:
            return []

    cleaned: List[float] = []

    for item in sensor_values:
        # Explicitly ignore booleans (in Python, bool is a subclass of int, so float(True) == 1.0)
        if isinstance(item, bool) or item is None:
            continue

        try:
            val = float(item)
        except (ValueError, TypeError):
            continue

        # Drop NaN, infinite values, and negative readings (< 0)
        if math.isnan(val) or math.isinf(val) or val < 0.0:
            continue

        # Clipping: cap at 500.0
        if val > 500.0:
            val = 500.0

        cleaned.append(val)

    return cleaned


if __name__ == "__main__":
    # Simple standalone demonstration with test cases
    sample_inputs = [
        ("Mixed valid & invalid", [12.5, "45.0", -3.2, None, "error", 620.0, 0.0]),
        ("Empty list", []),
        ("All invalid entries", ["bad", None, -100, -0.0001, "NaN", "invalid"]),
        ("Clipping edge cases", [500.0, 500.0001, 1200.5, 499.99]),
    ]

    print("=== Section 1: Sensor Readings Sanitization Demo ===")
    for desc, inp in sample_inputs:
        result = clean_and_normalize_sensor_readings(inp)
        print(f"[{desc}]")
        print(f"  Input:  {inp}")
        print(f"  Output: {result}\n")
