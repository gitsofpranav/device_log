"""Section 2: Core Data Processing Task.

Reads device telemetry CSV data, aggregates per device:
- Total number of records
- Average (mean) temperature
- Count of records where status == 'ERROR'
Filters out devices with an average temperature above 80.0.
Exports clean aggregated results to JSON and prints an ASCII summary table in the terminal.
"""

import csv
import json
import os
import sys
from typing import Dict, List, Any, Optional


def load_telemetry_csv(csv_path: str) -> List[Dict[str, Any]]:
    """Load and validate records from the telemetry CSV file.

    Handles missing files, empty files, malformed rows, and missing headers.

    Args:
        csv_path: Path to the telemetry CSV file.

    Returns:
        List[Dict[str, Any]]: List of valid row dictionaries with parsed values.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If required columns are missing from the header or file is empty.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Telemetry CSV file not found at: '{csv_path}'")

    records: List[Dict[str, Any]] = []

    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        try:
            raw_header = next(reader)
        except StopIteration:
            raise ValueError(f"Telemetry CSV file is empty: '{csv_path}'")

        # Normalize column header names
        header = [col.strip().lower() for col in raw_header]
        required_cols = {"device_id", "status", "temperature"}
        missing_cols = required_cols - set(header)
        if missing_cols:
            raise ValueError(
                f"CSV file is missing required columns: {sorted(list(missing_cols))}. "
                f"Found: {header}"
            )

        col_indices = {
            "device_id": header.index("device_id"),
            "status": header.index("status"),
            "temperature": header.index("temperature"),
        }

        for row_idx, row in enumerate(reader, start=2):
            if not row or all(not cell.strip() for cell in row):
                continue  # Skip blank lines

            if len(row) <= max(col_indices.values()):
                print(
                    f"[WARN] Row {row_idx}: Incomplete row data, skipping. Content: {row}",
                    file=sys.stderr,
                )
                continue

            device_id = row[col_indices["device_id"]].strip()
            status = row[col_indices["status"]].strip().upper()
            raw_temp = row[col_indices["temperature"]].strip()

            if not device_id:
                print(f"[WARN] Row {row_idx}: Empty device_id, skipping.", file=sys.stderr)
                continue

            try:
                temp = float(raw_temp)
            except ValueError:
                print(
                    f"[WARN] Row {row_idx}: Invalid temperature '{raw_temp}' for device '{device_id}', skipping.",
                    file=sys.stderr,
                )
                continue

            records.append(
                {
                    "device_id": device_id,
                    "status": status,
                    "temperature": temp,
                }
            )

    return records


def aggregate_and_filter_telemetry(
    records: List[Dict[str, Any]],
    temp_threshold: float = 80.0,
) -> List[Dict[str, Any]]:
    """Group records by device_id, compute metrics, and filter out devices with avg_temp > threshold.

    Metrics per device:
    - total_records: Total count of records
    - avg_temperature: Mean temperature rounded to 2 decimal places
    - error_count: Total count of status == 'ERROR'

    Args:
        records: List of validated telemetry records.
        temp_threshold: Upper limit for average temperature (devices above this are excluded).

    Returns:
        List[Dict[str, Any]]: Aggregated device records sorted by device_id.
    """
    grouped: Dict[str, Dict[str, Any]] = {}

    for rec in records:
        dev_id = rec["device_id"]
        if dev_id not in grouped:
            grouped[dev_id] = {
                "temperatures": [],
                "error_count": 0,
                "total_records": 0,
            }

        grouped[dev_id]["total_records"] += 1
        grouped[dev_id]["temperatures"].append(rec["temperature"])
        if rec["status"] == "ERROR":
            grouped[dev_id]["error_count"] += 1

    results: List[Dict[str, Any]] = []

    for dev_id, data in sorted(grouped.items()):
        temps = data["temperatures"]
        avg_temp = round(sum(temps) / len(temps), 2) if temps else 0.0

        # Filter requirement: "Filter out any devices that have an average temperature above 80.0"
        if avg_temp <= temp_threshold:
            results.append(
                {
                    "device_id": dev_id,
                    "total_records": data["total_records"],
                    "avg_temperature": avg_temp,
                    "error_count": data["error_count"],
                }
            )

    return results


def export_to_json(data: List[Dict[str, Any]], output_path: str) -> None:
    """Export aggregated device data to a formatted JSON file."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def print_summary_table(data: List[Dict[str, Any]], temp_threshold: float = 80.0) -> None:
    """Print an ASCII summary table to stdout."""
    unit = "°C"
    try:
        if sys.stdout and sys.stdout.encoding:
            unit.encode(sys.stdout.encoding)
    except Exception:
        unit = " C"

    print("\n" + "=" * 65)
    print(f" DEVICE TELEMETRY SUMMARY REPORT (Filtered: Avg Temp <= {temp_threshold}{unit})")
    print("=" * 65)

    if not data:
        print(" No devices met the criteria or no valid records were processed.")
        print("=" * 65 + "\n")
        return

    header_fmt = "{:<12} | {:>14} | {:>18} | {:>12}"
    divider = "-" * 13 + "+" + "-" * 16 + "+" + "-" * 20 + "+" + "-" * 13
    print(header_fmt.format("Device ID", "Total Records", "Avg Temperature", "Error Count"))
    print(divider)

    for item in data:
        print(
            header_fmt.format(
                item["device_id"],
                item["total_records"],
                f"{item['avg_temperature']:.2f}{unit}",
                item["error_count"],
            )
        )

    print("=" * 65 + "\n")


def process_telemetry(
    csv_path: str,
    output_json_path: Optional[str] = None,
    temp_threshold: float = 80.0,
) -> List[Dict[str, Any]]:
    """Complete pipeline: reads CSV, aggregates & filters data, optionally saves JSON, prints table."""
    records = load_telemetry_csv(csv_path)
    aggregated = aggregate_and_filter_telemetry(records, temp_threshold=temp_threshold)

    print_summary_table(aggregated, temp_threshold=temp_threshold)

    if output_json_path:
        export_to_json(aggregated, output_json_path)
        print(f"[INFO] Summary successfully saved to: {output_json_path}")

    return aggregated
