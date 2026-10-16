"""Unit tests for Section 2: Telemetry Data Processing & Aggregation."""

import json
import os
import pytest
from src.summarizer import (
    load_telemetry_csv,
    aggregate_and_filter_telemetry,
    export_to_json,
    process_telemetry,
)


@pytest.fixture
def sample_csv(tmp_path):
    """Create a temporary valid CSV file."""
    csv_file = tmp_path / "test_telemetry.csv"
    content = (
        "device_id,status,temperature\n"
        "DEV_1,ACTIVE,50.0\n"
        "DEV_1,ERROR,55.0\n"
        "DEV_2,ACTIVE,90.0\n"
        "DEV_2,WARNING,85.0\n"
        "DEV_3,ACTIVE,70.0\n"
        "DEV_3,ERROR,80.0\n"
        "DEV_3,ERROR,90.0\n"
    )
    csv_file.write_text(content, encoding="utf-8")
    return str(csv_file)


def test_load_telemetry_valid(sample_csv):
    """Test loading valid telemetry records."""
    records = load_telemetry_csv(sample_csv)
    assert len(records) == 7
    assert records[0] == {"device_id": "DEV_1", "status": "ACTIVE", "temperature": 50.0}
    assert records[1] == {"device_id": "DEV_1", "status": "ERROR", "temperature": 55.0}


def test_aggregation_and_filtering(sample_csv):
    """Test grouping, mean calculation, error count, and filtering > 80.0 threshold."""
    records = load_telemetry_csv(sample_csv)
    results = aggregate_and_filter_telemetry(records, temp_threshold=80.0)

    # DEV_1: temps=[50.0, 55.0] -> avg = 52.5 <= 80.0 (kept), error_count = 1, total = 2
    # DEV_2: temps=[90.0, 85.0] -> avg = 87.5 > 80.0 (filtered out!)
    # DEV_3: temps=[70.0, 80.0, 90.0] -> avg = 80.0 <= 80.0 (kept), error_count = 2, total = 3
    devices = [r["device_id"] for r in results]
    assert "DEV_1" in devices
    assert "DEV_2" not in devices  # Filtered out
    assert "DEV_3" in devices

    dev1 = next(r for r in results if r["device_id"] == "DEV_1")
    assert dev1["total_records"] == 2
    assert dev1["avg_temperature"] == 52.5
    assert dev1["error_count"] == 1

    dev3 = next(r for r in results if r["device_id"] == "DEV_3")
    assert dev3["total_records"] == 3
    assert dev3["avg_temperature"] == 80.0
    assert dev3["error_count"] == 2


def test_file_not_found():
    """Test that non-existent CSV file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_telemetry_csv("non_existent_file.csv")


def test_empty_csv_raises_error(tmp_path):
    """Test that an empty CSV file raises ValueError."""
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="is empty"):
        load_telemetry_csv(str(empty_csv))


def test_missing_headers_raises_error(tmp_path):
    """Test that missing required columns raises ValueError."""
    bad_header_csv = tmp_path / "bad_header.csv"
    bad_header_csv.write_text("device_id,wrong_column\nDEV_1,50.0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required columns"):
        load_telemetry_csv(str(bad_header_csv))


def test_corrupted_rows_handling(tmp_path):
    """Test that corrupted rows (malformed floats, missing fields) are safely skipped."""
    corrupted_csv = tmp_path / "corrupted.csv"
    content = (
        "device_id,status,temperature\n"
        "DEV_OK,ACTIVE,60.0\n"
        "DEV_BAD,ACTIVE,not_a_float\n"
        "DEV_SHORT,ACTIVE\n"
        "\n"
        ",ACTIVE,55.0\n"
        "DEV_OK,ERROR,62.0\n"
    )
    corrupted_csv.write_text(content, encoding="utf-8")
    records = load_telemetry_csv(str(corrupted_csv))

    assert len(records) == 2
    assert records[0]["device_id"] == "DEV_OK"
    assert records[1]["device_id"] == "DEV_OK"


def test_export_to_json(tmp_path):
    """Test exporting to and reading from JSON."""
    data = [
        {"device_id": "DEV_A", "total_records": 10, "avg_temperature": 55.4, "error_count": 0}
    ]
    json_path = tmp_path / "output.json"
    export_to_json(data, str(json_path))

    assert json_path.exists()
    with open(json_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded == data
