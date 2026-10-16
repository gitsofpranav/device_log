"""Unit tests for Section 3: Visualization Module."""

import os
import pytest
from src.visualizer import load_summary_data, generate_temperature_chart


def test_load_summary_data_valid(tmp_path):
    """Test loading valid summary JSON."""
    json_path = tmp_path / "valid.json"
    json_path.write_text(
        '[{"device_id": "DEV_A", "total_records": 5, "avg_temperature": 45.0, "error_count": 0}]',
        encoding="utf-8",
    )
    data = load_summary_data(str(json_path))
    assert len(data) == 1
    assert data[0]["device_id"] == "DEV_A"


def test_load_summary_data_not_found():
    """Test loading missing JSON file."""
    with pytest.raises(FileNotFoundError):
        load_summary_data("non_existent_summary.json")


def test_load_summary_data_invalid_json(tmp_path):
    """Test loading malformed JSON file."""
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("NOT_JSON", encoding="utf-8")
    with pytest.raises(ValueError, match="Corrupted or invalid JSON"):
        load_summary_data(str(bad_json))


def test_generate_temperature_chart(tmp_path):
    """Test generating chart from summary records."""
    data = [
        {"device_id": "DEV_A", "total_records": 4, "avg_temperature": 48.65, "error_count": 0},
        {"device_id": "DEV_B", "total_records": 5, "avg_temperature": 71.40, "error_count": 2},
    ]
    out_img = tmp_path / "test_chart.png"
    result_path = generate_temperature_chart(data, output_image_path=str(out_img))

    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0


def test_generate_chart_empty_data(tmp_path):
    """Test generating chart with empty list returns empty string without crashing."""
    out_img = tmp_path / "empty_chart.png"
    result = generate_temperature_chart([], output_image_path=str(out_img))
    assert result == ""
    assert not out_img.exists()
