"""Section 3: Visualization Module.

Generates a bar chart comparing average temperatures per device using matplotlib,
loading from the aggregated JSON output.
"""

import json
import os
import sys
from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt


def load_summary_data(json_path: str) -> List[Dict[str, Any]]:
    """Load and validate the aggregated telemetry JSON file."""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Summary JSON file not found at: '{json_path}'")

    with open(json_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Corrupted or invalid JSON in '{json_path}': {e}")

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a list of device summary records in '{json_path}', got {type(data).__name__}"
        )

    return data


def generate_temperature_chart(
    data: List[Dict[str, Any]],
    output_image_path: str = "output/device_temperatures.png",
    threshold_temp: Optional[float] = 80.0,
) -> str:
    """Generate and save a bar chart comparing average temperatures per device.

    Features:
    - Clean color palette with conditional highlighting
    - Explicit value labels on top of each bar
    - Reference threshold line for the 80°C filtering boundary
    - Rotated x-axis labels with proper alignment to prevent overlaps
    - Tight layout and high DPI export to prevent any label truncation

    Args:
        data: List of aggregated device dictionaries.
        output_image_path: Target path to save the chart image.
        threshold_temp: Optional threshold temperature line to display.

    Returns:
        str: Absolute path of the generated chart.
    """
    if not data:
        print("[WARN] No device data to plot. Skipping chart generation.", file=sys.stderr)
        return ""

    device_ids = [item.get("device_id", "Unknown") for item in data]
    avg_temps = [float(item.get("avg_temperature", 0.0)) for item in data]
    error_counts = [item.get("error_count", 0) for item in data]

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    # Styling colors: cool blue for healthy, coral/amber for devices with errors
    colors = [
        "#e74c3c" if err > 0 else "#3498db"
        for err in error_counts
    ]

    bars = ax.bar(
        device_ids,
        avg_temps,
        color=colors,
        width=0.55,
        edgecolor="#2c3e50",
        linewidth=1.0,
        zorder=3,
    )

    # Annotate bar values on top of each bar with padding
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.1f}°C",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),  # 5 points vertical offset
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color="#2c3e50",
        )

    # Optional reference line for 80°C threshold
    if threshold_temp is not None:
        ax.axhline(
            y=threshold_temp,
            color="#c0392b",
            linestyle="--",
            linewidth=1.2,
            label=f"Max Filter Threshold ({threshold_temp:.0f}°C)",
            zorder=2,
        )

    # Chart titles and labels
    ax.set_title(
        "Device Log Summarizer: Average Temperature per Device",
        fontsize=14,
        fontweight="bold",
        pad=15,
        color="#2c3e50",
    )
    ax.set_xlabel("Device ID", fontsize=11, fontweight="bold", labelpad=10, color="#2c3e50")
    ax.set_ylabel("Average Temperature (°C)", fontsize=11, fontweight="bold", labelpad=10, color="#2c3e50")

    # Rotate x-tick labels to prevent overlapping
    ax.set_xticks(range(len(device_ids)))
    ax.set_xticklabels(device_ids, rotation=30, ha="right", fontsize=10)

    # Set y-axis limits with 15% headroom above the max value so labels don't collide with top edge
    max_val = max(avg_temps + ([threshold_temp] if threshold_temp else [0.0]))
    ax.set_ylim(0, max_val * 1.18)

    # Subtle horizontal grid lines behind bars
    ax.yaxis.grid(True, linestyle=":", alpha=0.6, zorder=0)
    ax.set_axisbelow(True)

    # Clean spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#bdc3c7")
    ax.spines["bottom"].set_color("#bdc3c7")

    # Legend
    legend_elements = [
        plt.Line2D([0], [0], color="#3498db", lw=6, label="Normal Device (0 Errors)"),
        plt.Line2D([0], [0], color="#e74c3c", lw=6, label="Device with Error Logs"),
    ]
    if threshold_temp is not None:
        legend_elements.append(
            plt.Line2D([0], [0], color="#c0392b", linestyle="--", lw=1.5, label=f"Threshold ({threshold_temp:.0f}°C)")
        )
    ax.legend(handles=legend_elements, loc="upper right", framealpha=0.9, fontsize=9)

    # Prevent layout clipping
    plt.tight_layout()

    # Save output image
    os.makedirs(os.path.dirname(os.path.abspath(output_image_path)), exist_ok=True)
    plt.savefig(output_image_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"[INFO] Bar chart generated successfully at: {output_image_path}")
    return os.path.abspath(output_image_path)


if __name__ == "__main__":
    target_json = sys.argv[1] if len(sys.argv) > 1 else "output/summary.json"
    target_img = sys.argv[2] if len(sys.argv) > 2 else "output/device_temperatures.png"

    try:
        loaded_data = load_summary_data(target_json)
        generate_temperature_chart(loaded_data, target_img)
    except Exception as err:
        print(f"[ERROR] Failed to generate chart: {err}", file=sys.stderr)
        sys.exit(1)
