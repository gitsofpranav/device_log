"""Test suite for Section 1: Sensor Readings Sanitization."""

import pytest
from src.sanitizer import clean_and_normalize_sensor_readings


def test_mixed_inputs_cleaning():
    """Test standard mixed input list with valid strings, floats, ints, negatives, and None."""
    raw = [23.4, "45.6", -1.0, None, "ERROR_FLAG", 100, "0.0"]
    expected = [23.4, 45.6, 100.0, 0.0]
    assert clean_and_normalize_sensor_readings(raw) == expected


def test_clipping_at_threshold():
    """Test that numbers exceeding 500.0 are capped at 500.0 and <= 500.0 remain unchanged."""
    raw = [499.9, 500.0, 500.1, 9999.9, "650"]
    expected = [499.9, 500.0, 500.0, 500.0, 500.0]
    assert clean_and_normalize_sensor_readings(raw) == expected


def test_edge_cases_empty_and_invalid():
    """Test edge cases: empty list, None input, boolean values, and entirely invalid items."""
    assert clean_and_normalize_sensor_readings([]) == []
    assert clean_and_normalize_sensor_readings(None) == []
    assert clean_and_normalize_sensor_readings(["invalid", None, -50, "-999", "N/A"]) == []
    # Booleans should be filtered out and not converted to 1.0 or 0.0
    assert clean_and_normalize_sensor_readings([True, False, 15.0]) == [15.0]


def test_zero_and_boundary_readings():
    """Test boundary readings like 0.0, exact 500.0, and small positive numbers."""
    raw = [0, 0.0, "0", 1e-6, 500]
    expected = [0.0, 0.0, 0.0, 1e-6, 500.0]
    assert clean_and_normalize_sensor_readings(raw) == expected
