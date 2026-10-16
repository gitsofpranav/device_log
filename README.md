# Device Log Summarizer CLI

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: Pytest](https://img.shields.io/badge/tests-pytest-green.svg)](https://docs.pytest.org/)

A robust, modular Command Line Interface (CLI) tool built for ingesting, cleaning, aggregating, filtering, and visualizing device telemetry data.

Developed as part of the **Software Engineering Intern Technical Assessment**.

---

## Table of Contents
- [Project Architecture](#project-architecture)
- [Assessment Sections Overview](#assessment-sections-overview)
  - [Section 1: Coding Logic & Sanitization](#section-1-coding-logic--sanitization)
  - [Section 2: Core Data Processing](#section-2-core-data-processing)
  - [Section 3: AI Prompting & Visualization](#section-3-ai-prompting--visualization)
- [Repository Structure](#repository-structure)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
  - [1. Summarize Telemetry (Default)](#1-summarize-telemetry-default)
  - [2. Clean Raw Sensor Readings](#2-clean-raw-sensor-readings)
- [Sample Output](#sample-output)
- [Running Unit Tests](#running-unit-tests)
- [Robustness & Edge-Case Handling](#robustness--edge-case-handling)

---

## Project Architecture

```
device_log_summarizer/
│
├── device_telemetry.csv        # Sample input telemetry dataset
├── main.py                     # Root CLI entry point
├── requirements.txt            # Project dependencies (matplotlib, pytest)
├── README.md                   # Complete documentation
├── PROMPT_LOG.md               # Section 3 AI collaboration log
│
├── src/
│   ├── __init__.py
│   ├── sanitizer.py            # Section 1: Sensor data cleaning & normalization
│   ├── summarizer.py           # Section 2: CSV ingestion, aggregation & filtering
│   ├── visualizer.py           # Section 3: Matplotlib bar chart generation
│   └── cli.py                  # CLI argument parser and command orchestrator
│
├── tests/
│   ├── __init__.py
│   ├── test_sanitizer.py       # Unit tests for Section 1
│   ├── test_summarizer.py      # Unit tests for Section 2
│   └── test_visualizer.py      # Unit tests for Section 3
│
└── output/
    ├── summary.json            # Generated JSON aggregation output
    └── device_temperatures.png # Generated high-resolution bar chart
```

---

## Assessment Sections Overview

### Section 1: Coding Logic & Sanitization
- **File:** `src/sanitizer.py`
- **Function:** `clean_and_normalize_sensor_readings(sensor_values: list) -> list[float]`
- **Capabilities:**
  - Converts convertible values to `float`.
  - Drops non-convertible items, `None`, boolean values, and negative readings (`< 0`).
  - Caps/limits any reading $> 500.0$ to `500.0`.
  - Handles empty lists, `None` inputs, and all-invalid collections without unhandled exceptions.

### Section 2: Core Data Processing
- **File:** `src/summarizer.py`
- **Capabilities:**
  - Ingests CSV telemetry data with columns: `device_id`, `status`, `temperature`.
  - Groups records by `device_id` and computes:
    - **Total Records** per device.
    - **Average (Mean) Temperature**.
    - **Error Count** (records where `status == "ERROR"`).
  - Filters out any devices with average temperature **$> 80.0°C$**.
  - Prints a formatted ASCII table in the terminal and exports valid records to `output/summary.json`.

### Section 3: AI Prompting & Visualization
- **File:** `src/visualizer.py` & `PROMPT_LOG.md`
- **Capabilities:**
  - Ingests the JSON output from Section 2.
  - Renders a publication-ready Matplotlib bar chart comparing average temperatures per device.
  - Highlights devices with error logs (red/coral) vs healthy devices (blue).
  - Annotates exact numerical values on top of each bar.
  - Draws a dashed reference line at the $80.0°C$ filtering threshold.
  - Fixes layout truncation, edge collision, and label overlap.

---

## Installation & Setup

1. **Clone or Extract the Repository:**
   ```bash
   git clone <repository_url>
   cd device_log_summarizer
   ```

2. **(Optional) Create and Activate Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage Guide

### 1. Summarize Telemetry (Default)
Run the full summarization pipeline on the telemetry CSV:
```bash
python main.py summarize device_telemetry.csv
```
Or simply run:
```bash
python main.py
```

**Options:**
- `-o, --output PATH`: Specify custom JSON output path (default: `output/summary.json`).
- `-p, --plot PATH`: Specify custom chart image path (default: `output/device_temperatures.png`).
- `-t, --threshold FLOAT`: Specify custom max average temperature threshold (default: `80.0`).
- `--no-plot`: Run aggregation and JSON export without generating a chart.

### 2. Clean Raw Sensor Readings
Run the Section 1 sensor cleaning logic from the CLI:
```bash
python main.py clean 12.5 "45.0" -3.2 None "error" 620.0 0.0
```

---

## Sample Output

### Terminal Summary Table
```
=================================================================
 DEVICE TELEMETRY SUMMARY REPORT (Filtered: Avg Temp <= 80.0°C)
=================================================================
Device ID    |  Total Records |    Avg Temperature |  Error Count
-------------+----------------+--------------------+-------------
DEV_A        |              4 |            48.65°C |            0
DEV_B        |              5 |            71.40°C |            2
DEV_D        |              4 |            65.00°C |            0
DEV_F        |              5 |            36.16°C |            1
=================================================================
```
*(Notice: Overheating devices `DEV_C` [avg 90.1°C] and `DEV_E` [avg 103.6°C] were automatically filtered out)*

### Exported JSON (`output/summary.json`)
```json
[
    {
        "device_id": "DEV_A",
        "total_records": 4,
        "avg_temperature": 48.65,
        "error_count": 0
    },
    {
        "device_id": "DEV_B",
        "total_records": 5,
        "avg_temperature": 71.4,
        "error_count": 2
    },
    {
        "device_id": "DEV_D",
        "total_records": 4,
        "avg_temperature": 65.0,
        "error_count": 0
    },
    {
        "device_id": "DEV_F",
        "total_records": 5,
        "avg_temperature": 36.16,
        "error_count": 1
    }
]
```

### Generated Chart (`output/device_temperatures.png`)
Saved automatically at 300 DPI with bar value labels, rotated ticks, and the 80°C threshold line.

---

## Running Unit Tests

The test suite covers:
- Sensor conversion, clipping, negative dropping, null handling, and boolean filtering.
- Telemetry CSV parsing, missing column validation, and corrupted row skipping.
- Grouping, average computation, and 80.0°C threshold filtering.
- JSON serialization and deserialization.
- Chart generation, file creation, and empty dataset handling.

To run all tests:
```bash
pytest -v
```

---

## Robustness & Edge-Case Handling

- **Missing Files:** Raises clear `FileNotFoundError` without unhandled stack traces.
- **Corrupt Rows:** Malformed numeric strings or incomplete CSV lines are logged to `stderr` and skipped safely without terminating the batch.
- **Header Validation:** Case-insensitive and whitespace-tolerant validation of column names.
- **Terminal Encoding Resilience:** Automatically adapts temperature degree symbol to the active terminal encoding (`sys.stdout.encoding`) to avoid encoding crashes on Windows PowerShell/CMD.
- **Empty Datasets:** Handled gracefully across all modules (returns `[]` or clean notice without division-by-zero errors).
