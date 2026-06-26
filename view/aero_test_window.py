import tkinter as tk
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import SpanSelector
import matplotlib.pyplot as plt
import numpy as np
from functools import partial
from pathlib import Path
from typing import Optional

from model.entities import AeroTest, AeroTestSelection
from view.components import SectionLabel


_DEFAULT_ON = frozenset({'speed', 'power', 'cadence', 'wind_speed'})

_SPEED_FIELDS = frozenset({'speed', 'enhanced_speed', 'wind_speed'})
_MPS_TO_KPH = 3.6

_UNITS: dict[str, str] = {
    'speed': 'km/h',
    'enhanced_speed': 'km/h',
    'power': 'W',
    'cadence': 'rpm',
    'wind_speed': 'km/h',
    'heart_rate': 'bpm',
    'altitude': 'm',
    'enhanced_altitude': 'm',
    'temperature': 'degC',
    'distance': 'm',
    'grade': '%',
}

# Border color used to indicate the currently active saved selection.
_ACTIVE_SEL_BORDER = ("white", "gray75")


class AeroTestWindow(ctk.CTkToplevel):
    def __init__(self, root, aero_test: AeroTest, fit_data: dict[str, np.ndarray],
                 controller=None):
        super().__init__(root)
        self.title(Path(aero_test.data_file).name if aero_test.data_file else aero_test.name)
        self.geometry("1400x800")
        self.minsize(900, 600)

        self.aero_test_id = aero_test.aero_test_id
        self.controller = controller
        self._fit_data = fit_data
        self._time = fit_data.get('elapsed_time', np.array([]))

        self._var_names = sorted(k for k in fit_data if k != 'elapsed_time')

        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        self._var_colors: dict[str, str] = {
            name: colors[i % len(colors)]
            for i, name in enumerate(self._var_names)
        }

        self._var_checks: dict[str, tk.BooleanVar] = {
            name: tk.BooleanVar(value=(name in _DEFAULT_ON))
            for name in self._var_names
        }

        self._sel_start: Optional[float] = None
        self._sel_end: Optional[float] = None
        self._active_sel_id: Optional[int] = None
        self._sel_buttons: dict[int, ctk.CTkButton] = {}
        self._span_selector: Optional[SpanSelector] = None
        self._main_ax = None
        self._fig: Optional[Figure] = None
        self._zoom_var = tk.BooleanVar(value=False)
        self._zoom_chk: Optional[ctk.CTkCheckBox] = None
        self._canvas: Optional[FigureCanvasTkAgg] = None
        self._toolbar = None

        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=1, minsize=160)
        self.grid_rowconfigure(0, weight=1)

        self._build_plot_area()
        self._build_right_panel(aero_test.selections)
        self._redraw_plot()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------ layout builders ------

    def _build_plot_area(self):
        left = ctk.CTkFrame(self, corner_radius=0)
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(0, weight=1)
        left.grid(row=0, column=0, sticky="nsew")

        canvas_frame = ctk.CTkFrame(left, corner_radius=0)
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid(row=0, column=0, sticky="nsew")

        self._fig = Figure()
        self._canvas = FigureCanvasTkAgg(self._fig, master=canvas_frame)
        self._canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self._toolbar = NavigationToolbar2Tk(self._canvas, canvas_frame, pack_toolbar=False)
        self._toolbar.update()
        self._toolbar.grid(row=1, column=0, sticky="ew")

        toggle_frame = ctk.CTkFrame(left, corner_radius=0, fg_color=("gray85", "gray15"))
        toggle_frame.grid(row=1, column=0, sticky="ew")

        cols_per_row = 7
        for i, name in enumerate(self._var_names):
            color = self._var_colors[name]
            cb = ctk.CTkCheckBox(
                toggle_frame,
                text=name,
                variable=self._var_checks[name],
                command=self._redraw_plot,
                fg_color=color,
                hover_color=color,
                border_color=color,
                text_color=color,
                checkbox_width=18, checkbox_height=18,
                font=ctk.CTkFont(size=12),
            )
            cb.grid(row=i // cols_per_row, column=i % cols_per_row, padx=10, pady=10, sticky="w")

    def _build_right_panel(self, selections: list):
        right = ctk.CTkFrame(self, corner_radius=0)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(8, weight=1)
        right.grid(row=0, column=1, sticky="nsew")

        # Active selection name -- large, centered
        self._active_name_lbl = ctk.CTkLabel(
            right, text="-",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="center")
        self._active_name_lbl.grid(row=0, column=0, padx=10, pady=(12, 4), sticky="ew")

        # Time range inputs
        time_frame = ctk.CTkFrame(right)
        time_frame.grid_columnconfigure(1, weight=1)
        time_frame.grid(row=1, column=0, padx=10, pady=(0, 4), sticky="ew")
        ctk.CTkLabel(time_frame, text="Start (s):").grid(
            row=0, column=0, padx=(8, 4), pady=(6, 2), sticky="w")
        self._start_ent = ctk.CTkEntry(time_frame, width=60)
        self._start_ent.grid(row=0, column=1, padx=(0, 4), pady=(6, 2), sticky="ew")
        ctk.CTkLabel(time_frame, text="End (s):").grid(
            row=1, column=0, padx=(8, 4), pady=(2, 6), sticky="w")
        self._end_ent = ctk.CTkEntry(time_frame, width=60)
        self._end_ent.grid(row=1, column=1, padx=(0, 4), pady=(2, 6), sticky="ew")
        ctk.CTkButton(time_frame, text="Apply", width=50,
                      command=self._apply_time_range).grid(
            row=0, column=2, rowspan=2, padx=(0, 8), pady=6)

        # Zoom to selection toggle
        self._zoom_chk = ctk.CTkCheckBox(
            right, text="Zoom to Selection",
            variable=self._zoom_var,
            command=self._on_zoom_toggle,
            checkbox_width=18, checkbox_height=18,
            font=ctk.CTkFont(size=12),
        )
        self._zoom_chk.grid(row=2, column=0, padx=15, pady=(0, 4), sticky="w")

        # Stats
        stats_frame = ctk.CTkFrame(right)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid(row=3, column=0, padx=10, pady=4, sticky="ew")

        stat_rows = [
            ("_duration_val", "Duration:"),
            ("_distance_val", "Distance:"),
            ("_avg_power_val", "Avg Power:"),
            ("_avg_speed_val", "Avg Speed:"),
            ("_speed_range_val", "Speed Range:"),
            ("_speed_delta_val", "Avg Accel:"),
        ]
        for i, (attr, label) in enumerate(stat_rows):
            ctk.CTkLabel(stats_frame, text=label, anchor="w").grid(
                row=i, column=0, padx=(10, 4), pady=2, sticky="w")
            val_lbl = ctk.CTkLabel(stats_frame, text="-", anchor="w")
            val_lbl.grid(row=i, column=1, padx=(0, 10), pady=2, sticky="w")
            setattr(self, attr, val_lbl)

        # Name entry
        name_frame = ctk.CTkFrame(right, fg_color="transparent")
        name_frame.grid_columnconfigure(0, weight=1)
        name_frame.grid(row=4, column=0, padx=10, pady=(6, 2), sticky="ew")
        ctk.CTkLabel(name_frame, text="Name:").grid(row=0, column=0, sticky="w")
        self._name_entry = ctk.CTkEntry(name_frame, placeholder_text="Selection name")
        self._name_entry.grid(row=1, column=0, sticky="ew")

        # Save button -- natural width, horizontal padding only
        ctk.CTkButton(right, text="Save Selection",
                      fg_color="green", hover_color="dark green",
                      command=self._save_selection).grid(
            row=5, column=0, padx=20, pady=6)

        # Divider
        ctk.CTkFrame(right, height=2, corner_radius=0,
                     fg_color=("dark slate gray", "gray60")).grid(
            row=6, column=0, sticky="ew", padx=10, pady=4)

        SectionLabel(right, "Saved Selections").grid(
            row=7, column=0, padx=10, pady=(4, 2), sticky="w")

        self._sel_scroll = ctk.CTkScrollableFrame(right, corner_radius=0)
        self._sel_scroll.grid_columnconfigure(0, weight=1)
        self._sel_scroll.grid(row=8, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self._refresh_selections_list(selections)

    # ------ plot ------

    def _redraw_plot(self):
        self._fig.clf()
        enabled = [n for n in self._var_names if self._var_checks[n].get()]

        if not enabled:
            self._canvas.draw()
            return

        ax0 = self._fig.add_subplot(111)
        axes = [ax0]
        for _ in range(len(enabled) - 1):
            axes.append(ax0.twinx())

        # All patches invisible -- figure background shows through, all lines visible.
        # ax0 stays at the highest zorder so it receives SpanSelector mouse events.
        n_right = len(axes) - 1
        for i, ax in enumerate(axes[1:], 1):
            ax.spines['right'].set_position(('outward', (i - 1) * 40))
            ax.set_zorder(1)
            ax.patch.set_visible(False)

        ax0.set_zorder(10)
        ax0.patch.set_visible(False)

        # Tighten margins to fit axis labels without wasting space.
        right_margin = max(0.72, 1.0 - 0.07 * n_right)
        self._fig.subplots_adjust(left=0.10, right=right_margin)

        for i, name in enumerate(enabled):
            ax = axes[i]
            color = self._var_colors[name]
            data = self._fit_data[name] * _MPS_TO_KPH if name in _SPEED_FIELDS else self._fit_data[name]
            ax.plot(self._time, data, color=color, linewidth=0.8)
            unit = _UNITS.get(name, '')
            y_label = f"{name} ({unit})" if unit else name
            ax.set_ylabel(y_label, color=color, fontsize=8, labelpad=2)
            ax.tick_params(axis='y', labelcolor=color, labelsize=7)
            if i == 0:
                ax.spines['left'].set_color(color)
            else:
                ax.spines['right'].set_color(color)

        ax0.set_xlabel("Time (s)")

        self._span_selector = SpanSelector(
            ax0, self._on_span_select, 'horizontal',
            useblit=True,
            props=dict(alpha=0.25, facecolor='#FFD700'),
            interactive=True,
            drag_from_anywhere=True,
        )

        if self._sel_start is not None and self._sel_end is not None:
            try:
                self._span_selector.extents = (self._sel_start, self._sel_end)
            except Exception:
                pass

        self._main_ax = ax0
        xlim = self._zoom_xlim()
        if xlim is not None:
            ax0.set_xlim(*xlim)
        elif len(self._time) > 0:
            ax0.set_xlim(self._time.min(), self._time.max())
        self._canvas.draw()

    # ------ span selection ------

    def _on_span_select(self, xmin: float, xmax: float):
        if self._toolbar.mode:
            return
        if abs(xmax - xmin) < 0.5:
            return

        if len(self._time) > 0:
            xmin = max(xmin, float(self._time.min()))
            xmax = min(xmax, float(self._time.max()))
        if xmin >= xmax:
            return

        self._sel_start = xmin
        self._sel_end = xmax

        self._start_ent.delete(0, 'end')
        self._start_ent.insert(0, f"{xmin:.1f}")
        self._end_ent.delete(0, 'end')
        self._end_ent.insert(0, f"{xmax:.1f}")

        mask = (self._time >= xmin) & (self._time <= xmax)
        if mask.any():
            self._update_stats_display(self._compute_stats(mask))

        name = self._name_entry.get().strip()
        self._active_name_lbl.configure(text=name or "-")

        self._update_zoom_state()
        if self._zoom_var.get():
            self._apply_zoom()

    def _apply_time_range(self):
        try:
            xmin = float(self._start_ent.get())
            xmax = float(self._end_ent.get())
        except ValueError:
            return
        if xmin >= xmax:
            return

        if len(self._time) > 0:
            t_min = float(self._time.min())
            t_max = float(self._time.max())
            xmin = max(xmin, t_min)
            xmax = min(xmax, t_max)

        self._start_ent.delete(0, 'end')
        self._start_ent.insert(0, f"{xmin:.1f}")
        self._end_ent.delete(0, 'end')
        self._end_ent.insert(0, f"{xmax:.1f}")

        if xmin >= xmax:
            return

        self._sel_start = xmin
        self._sel_end = xmax

        if self._span_selector is not None:
            try:
                self._span_selector.extents = (xmin, xmax)
            except Exception:
                pass

        mask = (self._time >= xmin) & (self._time <= xmax)
        if mask.any():
            self._update_stats_display(self._compute_stats(mask))

        self._update_zoom_state()
        self._apply_zoom()

    # ------ zoom ------

    def _update_zoom_state(self):
        pass

    def _on_zoom_toggle(self):
        self._apply_zoom()

    def _zoom_xlim(self) -> tuple[float, float] | None:
        """Return (xlo, xhi) for zoomed view, or None if zoom is off or no selection."""
        if not (self._zoom_var.get() and self._sel_start is not None and self._sel_end is not None):
            return None
        padding = 0.05 * (self._sel_end - self._sel_start)
        t_min = float(self._time.min()) if len(self._time) > 0 else self._sel_start
        t_max = float(self._time.max()) if len(self._time) > 0 else self._sel_end
        return max(self._sel_start - padding, t_min), min(self._sel_end + padding, t_max)

    def _apply_zoom(self):
        if self._main_ax is None:
            return
        xlim = self._zoom_xlim()
        if xlim is not None:
            self._main_ax.set_xlim(*xlim)
        elif len(self._time) > 0:
            self._main_ax.set_xlim(self._time.min(), self._time.max())
        self._canvas.draw_idle()

    # ------ stats computation / display ------

    def _compute_stats(self, mask: np.ndarray) -> dict:
        time_sel = self._time[mask]
        duration = float(time_sel[-1] - time_sel[0]) if len(time_sel) > 1 else 0.0

        speed = self._fit_data.get('speed')
        power = self._fit_data.get('power')
        speed_sel = speed[mask] if speed is not None else None  # m/s from raw data
        power_sel = power[mask] if power is not None else None

        # distance: trapz over raw m/s * seconds -> metres
        distance = (float(np.trapz(speed_sel, time_sel))
                    if speed_sel is not None and len(time_sel) > 1 else None)
        avg_power = float(np.mean(power_sel)) if power_sel is not None else None

        # speed stats displayed in km/h
        speed_kph = speed_sel * _MPS_TO_KPH if speed_sel is not None else None
        avg_speed = float(np.mean(speed_kph)) if speed_kph is not None else None
        max_speed = float(np.max(speed_kph)) if speed_kph is not None else None
        min_speed = float(np.min(speed_kph)) if speed_kph is not None else None

        # avg acceleration: (end - start) in raw m/s / duration in s -> m/s^2
        avg_accel = None
        if speed_sel is not None and len(speed_sel) > 0 and duration > 0:
            avg_accel = float((speed_sel[-1] - speed_sel[0]) / duration)

        return dict(duration=duration, distance=distance, avg_power=avg_power,
                    avg_speed=avg_speed, max_speed=max_speed, min_speed=min_speed,
                    avg_accel=avg_accel)

    @staticmethod
    def _fmt(value, unit: str, decimals: int = 2) -> str:
        return "-" if value is None else f"{value:.{decimals}f} {unit}"

    def _update_stats_display(self, stats: dict):
        dur = stats.get('duration')
        if dur is not None:
            mins, secs = int(dur // 60), dur % 60
            self._duration_val.configure(text=f"{mins}:{secs:05.2f}")
        else:
            self._duration_val.configure(text="-")

        self._distance_val.configure(text=self._fmt(stats.get('distance'), "m"))
        self._avg_power_val.configure(text=self._fmt(stats.get('avg_power'), "W", 1))
        self._avg_speed_val.configure(text=self._fmt(stats.get('avg_speed'), "km/h"))

        mx, mn = stats.get('max_speed'), stats.get('min_speed')
        self._speed_range_val.configure(
            text=self._fmt(mx - mn if mx is not None and mn is not None else None, "km/h"))

        self._speed_delta_val.configure(
            text=self._fmt(stats.get('avg_accel'), "m/s\N{SUPERSCRIPT TWO}", decimals=4))

    # ------ save / load / delete selections ------

    def _save_selection(self):
        if self._sel_start is None or self._sel_end is None:
            return
        name = self._name_entry.get().strip() or "Selection"
        self._active_name_lbl.configure(text=name)
        mask = (self._time >= self._sel_start) & (self._time <= self._sel_end)
        stats = self._compute_stats(mask) if mask.any() else {}
        if not self.controller:
            return
        if self._active_sel_id is not None:
            self.controller.update_aero_test_selection(
                self.aero_test_id, self._active_sel_id,
                name, self._sel_start, self._sel_end, **stats)
        else:
            self.controller.save_aero_test_selection(
                self.aero_test_id, name, self._sel_start, self._sel_end, **stats)

    def _clear_selection(self):
        self._sel_start = None
        self._sel_end = None
        self._active_sel_id = None
        self._update_active_sel_button()
        self._active_name_lbl.configure(text="-")
        self._name_entry.delete(0, 'end')
        self._start_ent.delete(0, 'end')
        self._end_ent.delete(0, 'end')
        for attr in ('_duration_val', '_distance_val', '_avg_power_val',
                     '_avg_speed_val', '_speed_range_val', '_speed_delta_val'):
            getattr(self, attr).configure(text="-")
        self._update_zoom_state()
        self._redraw_plot()

    def _load_selection(self, sel: AeroTestSelection):
        if sel.selection_id == self._active_sel_id:
            self._clear_selection()
            return

        self._sel_start = sel.start_time
        self._sel_end = sel.end_time
        self._active_sel_id = sel.selection_id
        self._update_active_sel_button()

        self._active_name_lbl.configure(text=sel.name)
        self._name_entry.delete(0, 'end')
        self._name_entry.insert(0, sel.name)
        self._start_ent.delete(0, 'end')
        self._start_ent.insert(0, f"{sel.start_time:.1f}")
        self._end_ent.delete(0, 'end')
        self._end_ent.insert(0, f"{sel.end_time:.1f}")

        mask = (self._time >= sel.start_time) & (self._time <= sel.end_time)
        if mask.any():
            self._update_stats_display(self._compute_stats(mask))

        self._update_zoom_state()
        self._redraw_plot()

    def _delete_selection(self, selection_id: int):
        if selection_id == self._active_sel_id:
            self._active_sel_id = None
        if self.controller:
            self.controller.delete_aero_test_selection(self.aero_test_id, selection_id)

    def _update_active_sel_button(self):
        for sid, btn in self._sel_buttons.items():
            if sid == self._active_sel_id:
                btn.configure(border_width=2, border_color=_ACTIVE_SEL_BORDER)
            else:
                btn.configure(border_width=0)

    def _refresh_selections_list(self, selections: list):
        for w in self._sel_scroll.winfo_children():
            w.destroy()
        self._sel_buttons.clear()
        for sel in selections:
            row_frame = ctk.CTkFrame(self._sel_scroll, corner_radius=4)
            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid(sticky="ew", pady=2)
            btn = ctk.CTkButton(
                row_frame, text=sel.name, anchor="w",
                command=partial(self._load_selection, sel),
            )
            btn.grid(row=0, column=0, padx=(4, 0), pady=4, sticky="ew")
            ctk.CTkButton(
                row_frame, text="x", width=28,
                fg_color="red", hover_color="dark red",
                command=partial(self._delete_selection, sel.selection_id),
            ).grid(row=0, column=1, padx=(2, 4), pady=4)
            self._sel_buttons[sel.selection_id] = btn
        self._update_active_sel_button()

    def refresh_selections(self, selections: list):
        """Called by controller after the selections list on the AeroTest changes."""
        self._refresh_selections_list(selections)

    # ------ close ------

    def _on_close(self):
        plt.close(self._fig)
        self.destroy()
