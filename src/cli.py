"""Command Line Interface (CLI) for Device Log Summarizer.

Provides comprehensive commands for:
1. summarize: Ingest CSV, aggregate metrics, filter by max temperature, print table, export JSON, and optionally generate plot.
2. clean: Run Section 1 sensor cleaning logic on arbitrary values.
"""

import argparse
import sys
from typing import List, Optional
from src.sanitizer import clean_and_normalize_sensor_readings
from src.summarizer import process_telemetry
from src.visualizer import generate_temperature_chart


def build_parser() -> argparse.ArgumentParser:
    """Construct command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="device-summarizer",
        description="Device Log Summarizer CLI: Analyze, filter, and visualize device telemetry logs.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: summarize
    sum_parser = subparsers.add_parser("summarize", help="Process and summarize telemetry CSV data")
    sum_parser.add_argument(
        "csv_path",
        nargs="?",
        default="device_telemetry.csv",
        help="Path to telemetry CSV file (default: device_telemetry.csv)",
    )
    sum_parser.add_argument(
        "-o",
        "--output",
        dest="output_json",
        default="output/summary.json",
        help="Output path for aggregated JSON file (default: output/summary.json)",
    )
    sum_parser.add_argument(
        "-p",
        "--plot",
        dest="output_plot",
        default="output/device_temperatures.png",
        help="Output path for temperature bar chart image (default: output/device_temperatures.png)",
    )
    sum_parser.add_argument(
        "-t",
        "--threshold",
        dest="threshold",
        type=float,
        default=80.0,
        help="Maximum average temperature threshold to filter out devices above this value (default: 80.0)",
    )
    sum_parser.add_argument(
        "--no-plot",
        dest="no_plot",
        action="store_true",
        help="Disable chart generation",
    )

    # Command: clean (Section 1)
    clean_parser = subparsers.add_parser("clean", help="Clean and normalize a list of raw sensor readings")
    clean_parser.add_argument(
        "values",
        nargs="+",
        help="Space-separated list of raw sensor readings to clean (e.g., 23.4 '45.0' -5 None 600)",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI execution routine."""
    parser = build_parser()

    # If no arguments provided, default to summarize device_telemetry.csv
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        argv = ["summarize"]

    args = parser.parse_args(argv)

    if args.command == "summarize":
        try:
            print(f"[INFO] Ingesting telemetry data from: {args.csv_path}")
            aggregated = process_telemetry(
                csv_path=args.csv_path,
                output_json_path=args.output_json,
                temp_threshold=args.threshold,
            )

            if not args.no_plot:
                print(f"[INFO] Generating visualization chart...")
                generate_temperature_chart(
                    data=aggregated,
                    output_image_path=args.output_plot,
                    threshold_temp=args.threshold,
                )

            return 0
        except FileNotFoundError as e:
            print(f"[ERROR] File not found: {e}", file=sys.stderr)
            return 1
        except ValueError as e:
            print(f"[ERROR] Data validation error: {e}", file=sys.stderr)
            return 2
        except Exception as e:
            print(f"[FATAL] Unexpected error: {e}", file=sys.stderr)
            return 3

    elif args.command == "clean":
        # Parse inputs; convert literal string 'None' or 'null' to None
        parsed_inputs = []
        for v in args.values:
            if v.strip().lower() in ("none", "null"):
                parsed_inputs.append(None)
            else:
                parsed_inputs.append(v)

        result = clean_and_normalize_sensor_readings(parsed_inputs)
        print("=== Cleaned & Normalized Sensor Readings ===")
        print(f"Raw Input:   {parsed_inputs}")
        print(f"Cleaned:     {result}")
        return 0

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
