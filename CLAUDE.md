# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A cycling performance desktop GUI app for race simulation and aerodynamic drag (CdA) testing. Built with Python + `customtkinter`.

## Running

```bash
python main.py             # launch the GUI app
```

## Tests

Tests use pytest with shared fixtures in `tests/conftest.py`:

```bash
pytest tests/
pytest tests/test_model.py
pytest tests/test_calcs.py
pytest tests/test_controller.py
```

## Architecture

Strict MVC. Files are organized into packages:

- **`model/entities.py`** — dataclasses: `Rider`, `Environment`, `Simulation`, `AeroTest`, `PowerPlan`, `PowerPlanPoint`. All snake_case. `Simulation` and `AeroTest` store `rider_id`/`envir_id` integers rather than object references — the controller resolves them from `Storage` when needed.
- **`model/storage.py`** — `Storage` owns the lists of all entities and persists them via `pickle` to `~/Library/Application Support/wott_project/`. Manages monotonically increasing integer IDs so deleted IDs are never reused. Loaded on init, saved explicitly via `storage.save()` on app close.
- **`calcs.py`** — physics. `IPCalculator` solves a cycling ODE (rolling + aero drag + pedaling force) using `scipy.odeint` to produce velocity/position/split outputs. `CdACalculator` computes CdA from `.fit` files via `fitdecode`.
- **`view/panels.py`** — top-level `View` and all panel widgets built on `customtkinter`.
- **`view/components.py`** — reusable lower-level widgets.
- **`controller.py`** — `Controller` wires `Storage` to `View`. All button callbacks live here.
- **`main.py`** — entry point. Instantiates `Storage`, `View`, `Controller`; calls `storage.save()` on close.

## Key patterns

- **`entity.update(**kwargs)`** validates inputs atomically (all-or-nothing) on every entity. Raises `TypeError` or `AttributeError` on bad input; the controller catches these and routes them to the view's error display.
- `Simulation` and `AeroTest` store IDs only — no embedded `Rider`/`Environment` objects and no back-reference to `Storage`. The controller passes the resolved objects in when running a simulation or aero test.
- `tests/conftest.py` provides shared pytest fixtures (`sample_rider`, `sample_envir`, `sample_sim`, `sample_aero_test`, `tmp_storage`) used across all test files. `tmp_storage` writes to pytest's `tmp_path` so tests never touch real app data.

## Dependencies

`customtkinter`, `numpy`, `scipy`, `matplotlib`, `fitdecode`
