# AI Prompt Log (`PROMPT_LOG.md`)

**Role:** Software Engineering Intern Assessment  
**Project:** Device Log Summarizer CLI Tool  
**Focus:** Section 3 — AI Prompting & Charting Challenge  

---

## 1. Initial Prompt to AI Assistant

**Prompt:**
> *"Write a Python script using Matplotlib that loads a JSON file named `summary.json` containing aggregated telemetry records (each item has `device_id`, `total_records`, `avg_temperature`, and `error_count`) and generates a bar chart comparing the average temperature per device. Save the resulting chart as an image."*

---

## 2. Review of AI's Initial Attempt & Identified Mistakes

When inspecting the script produced by the initial prompt, several usability and formatting issues were identified:

1. **Truncated and Overlapping X-Axis Labels:**
   - The device IDs were placed horizontally along the x-axis without rotation or horizontal alignment adjustments. With longer device identifiers or additional devices, labels overlapped and collided with one another.
2. **Missing Value Annotations:**
   - The bars displayed temperature heights, but viewers could not ascertain exact values without squinting at the y-axis grid lines. Numerical labels above each bar were missing.
3. **Top Edge Clipping (No Headroom):**
   - The y-axis scaled strictly up to `max(avg_temperatures)`. Consequently, the highest bar touched the upper boundary of the chart frame.
4. **Lack of Layout Auto-Adjustment:**
   - The initial code called `plt.savefig()` without `plt.tight_layout()` or `bbox_inches='tight'`, which caused x-axis labels and the bottom title to be partially cropped out when saved to disk.
5. **No Contextual Distinction or Threshold Indicator:**
   - The assessment required filtering devices above 80.0°C in Section 2. The initial chart did not show this threshold line or distinguish devices with error logs.

---

## 3. Follow-Up Prompt to Fix the Issues

**Follow-Up Prompt:**
> *"Refactor the charting script to address the formatting and layout bugs:*
> 1. *Rotate the x-axis tick labels by 30° to 45° with right-alignment (`ha='right'`) to avoid label overlapping.*
> 2. *Add explicit numerical value annotations (e.g., `'71.4°C'`) centered directly on top of each bar with sufficient vertical offset.*
> 3. *Add 15–20% headroom to the y-axis limit (`ax.set_ylim`) so top labels and bars don't clip against the chart border.*
> 4. *Draw a dashed reference line at 80.0°C to visually highlight the Section 2 filtering threshold.*
> 5. *Distinguish devices with active errors (`error_count > 0`) using a warning color (coral/red) versus healthy devices (blue).*
> 6. *Add `plt.tight_layout()` and use `bbox_inches='tight'` with 300 DPI export so nothing is truncated in the saved PNG.*
> 7. *Include robust file-loading error handling if the JSON file is missing, empty, or corrupt."*

---

## 4. Final Outcome & Verification

- The resulting code was organized into [`src/visualizer.py`](src/visualizer.py) and integrated into the CLI tool [`src/cli.py`](src/cli.py).
- The generated chart ([`output/device_temperatures.png`](output/device_temperatures.png)) cleanly presents:
  - High-resolution (300 DPI) rendering with crisp fonts.
  - Proper margin headroom above bars.
  - Clear color coding (coral for devices with error logs, blue for healthy devices).
  - Clear 80°C threshold line with legend.
  - Formatted temperature callouts above each bar.
