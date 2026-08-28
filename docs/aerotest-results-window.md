# AeroTest Results Window — Design Brainstorm

## Overview

A dedicated window that opens when an aero test is run. It has two core functions:
1. View and explore the full fit file data
2. Select sub-sections of the data to save as test intervals for CdA calculation

---

## Requirement 1 — Fit File Viewer

### Plot behavior
- Multi-variable time-series plot of the fit file data
- X axis is time; supports zoom/pan on the x axis
- Each variable gets its own y axis (so e.g. power and cadence don't fight for scaling)
- Variables can be toggled on/off individually
- All numeric variables present in the fit file are available as toggles (discovered dynamically at load time)

### Default variable visibility
| Variable    | Default             |
|-------------|---------------------|
| Speed       | On (if present)     |
| Power       | On (if present)     |
| Cadence     | On (if present)     |
| Wind speed  | On (if present)     |
| All others  | Off                 |

---

## Requirement 2 — Sub-section Selection

### Creating a selection
- User drags horizontally across the plot to define a time range
- The selection is shown visually on the plot (shaded region)

### Selection stats panel (right-side column)
- Top of the column shows the name of the currently active selection
- Stats displayed for the active selection:
  - Time duration
  - Distance (integrated from speed)
  - Average power
  - Average speed
  - Max speed − min speed
  - End speed − start speed
- Below the stats: a scrollable list of all saved selections
- "Save selection" button saves the current selection

### Adjusting a selection
- Start and end times can be adjusted after the initial drag (e.g. text inputs or drag handles)

### Saved selections
- Multiple saved selections can coexist on the same `AeroTest`
- Saved selections can be renamed and deleted
- Clicking a saved selection in the list highlights its region on the plot and populates the stats panel

---

## Data Model

### `AeroTestSelection` (new entity)
Stored as a list on `AeroTest`. Fields:
- `name` — user-assigned label
- `start_time` / `end_time` — references into the fit file (no raw data copied)
- Computed selection stats (duration, distance, avg power, avg speed, etc.) — stored so they don't need to be recomputed on every load
- CdA calculation results — populated once a CdA calc is run on this selection

### `AeroTest` changes
- Gains a `selections: list[AeroTestSelection]` field

---

## Tech Stack

- Plot: matplotlib embedded via `FigureCanvasTkAgg` (already a dependency)
- Drag selection: `matplotlib.widgets.SpanSelector`
- Zoom/pan: `NavigationToolbar2Tk`
- Multiple y-axes: `ax.twinx()` per variable

---

## Layout

- Window split: **75% plot area / 25% right panel**
- Plot area: plot on top, variable toggle strip below
- Variable toggles: horizontal strip of checkboxes below the plot; each checkbox label and the checkbox color matches its variable's line/axis color
- Right panel (top to bottom): active selection name → selection stats → saved selections list → save button

## Visual Style

- Each variable gets a unique color applied consistently to:
  - The plotted line
  - Its y-axis ticks and label
  - Its checkbox in the variable toggle strip
  - Its entry in any legend

