import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from typing import List, Optional
from pathlib import Path
from functools import partial

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

matplotlib.use('TkAgg')  # must be set before any Figure or FigureCanvas is created
plt.style.use('bmh')
plt.rcParams.update({"figure.facecolor": "LightGray"})

from model.entities import Rider, Environment, Simulation, AeroTest
from view.components import (ScrollableBtnList, CustomTable, SectionLabel,
                              RiderEnvirDropdownFrame, PowerPlanFrame)


# ------ Selection frames (left panel) ------

class RiderSelectFrame(ctk.CTkFrame):
    def __init__(self, parent, name_ids: List[tuple[str, int]], controller=None):
        super().__init__(parent, fg_color=("gray70", "gray10"), width=1, corner_radius=0)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkButton(self, text="Add Rider", fg_color="green", hover_color="dark green",
                      width=50, command=self._add).grid(row=0, column=0, pady=(30, 10))
        ScrollableBtnList(self, name_ids, self._select).grid(row=1, column=0, sticky="nsew")

    def _add(self):
        if self.controller:
            self.controller.add_rider_btn_press()

    def _select(self, id_: int):
        if self.controller:
            self.controller.rider_select_btn_press(id_)


class EnvirSelectFrame(ctk.CTkFrame):
    def __init__(self, parent, name_ids: List[tuple[str, int]], controller=None):
        super().__init__(parent, fg_color=("gray70", "gray10"), width=1, corner_radius=0)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkButton(self, text="Add Environment", fg_color="green", hover_color="dark green",
                      width=50, command=self._add).grid(row=0, column=0, pady=(30, 10))
        ScrollableBtnList(self, name_ids, self._select).grid(row=1, column=0, sticky="nsew")

    def _add(self):
        if self.controller:
            self.controller.add_envir_btn_press()

    def _select(self, id_: int):
        if self.controller:
            self.controller.envir_select_btn_press(id_)


class SimSelectFrame(ctk.CTkFrame):
    def __init__(self, parent, name_ids: List[tuple[str, int]], controller=None):
        super().__init__(parent, fg_color=("gray70", "gray10"), width=1, corner_radius=0)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkButton(self, text="Add Simulation", fg_color="green", hover_color="dark green",
                      width=50, command=self._add).grid(row=0, column=0, pady=(30, 10))
        ScrollableBtnList(self, name_ids, self._select).grid(row=1, column=0, sticky="nsew")

    def _add(self):
        if self.controller:
            self.controller.add_sim_btn_press()

    def _select(self, id_: int):
        if self.controller:
            self.controller.sim_select_btn_press(id_)


class AeroTestSelectFrame(ctk.CTkFrame):
    def __init__(self, parent, name_ids: List[tuple[str, int]], controller=None):
        super().__init__(parent, fg_color=("gray70", "gray10"), width=1, corner_radius=0)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkButton(self, text="Add Aero Test", fg_color="green", hover_color="dark green",
                      width=50, command=self._add).grid(row=0, column=0, pady=(30, 10))
        ScrollableBtnList(self, name_ids, self._select).grid(row=1, column=0, sticky="nsew")

    def _add(self):
        if self.controller:
            self.controller.add_aero_test_btn_press()

    def _select(self, id_: int):
        if self.controller:
            self.controller.aero_test_select_btn_press(id_)


# ------ Profile frames (main content) ------

class _AlertMixin:
    """Mixin that provides show_alert_error / show_alert_success on self.alert_lbl."""

    def show_alert_error(self, message, ms: int = 3000):
        self.alert_lbl.configure(text=str(message), text_color='red')
        self.alert_lbl.after(ms, lambda: self.alert_lbl.configure(text=""))

    def show_alert_success(self, message, ms: int = 3000):
        self.alert_lbl.configure(text=str(message), text_color='green')
        self.alert_lbl.after(ms, lambda: self.alert_lbl.configure(text=""))


class RiderProfileFrame(_AlertMixin, ctk.CTkFrame):
    def __init__(self, parent, rider: Rider, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.rider_id = rider.rider_id

        # Name
        name_frm = ctk.CTkFrame(self)
        name_frm.grid_columnconfigure(4, weight=1)
        name_frm.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        SectionLabel(name_frm, "Rider Name").grid(row=0, column=0, columnspan=2, padx=(10, 0), sticky="NW")
        ctk.CTkLabel(name_frm, text="First Name:").grid(row=1, column=0, padx=(15, 5), pady=10)
        self.first_name_ent = ctk.CTkEntry(name_frm)
        self.first_name_ent.insert(0, rider.first_name or "")
        self.first_name_ent.grid(row=1, column=1, padx=(5, 25), pady=10)
        ctk.CTkLabel(name_frm, text="Last Name:").grid(row=1, column=2, padx=(25, 5), pady=10)
        self.last_name_ent = ctk.CTkEntry(name_frm)
        self.last_name_ent.insert(0, rider.last_name or "")
        self.last_name_ent.grid(row=1, column=3, padx=(5, 25), pady=10)

        # Physical stats
        stats_frm = ctk.CTkFrame(self)
        stats_frm.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        SectionLabel(stats_frm, "Physical Characteristics").grid(row=0, column=0, columnspan=2, padx=(10, 0), sticky="NW")
        ctk.CTkLabel(stats_frm, text="Weight (kg):").grid(row=1, column=0, padx=(15, 5), pady=10)
        self.weight_ent = ctk.CTkEntry(stats_frm)
        self.weight_ent.insert(0, str(rider.weight_kg) if rider.weight_kg is not None else "")
        self.weight_ent.grid(row=1, column=1, padx=(5, 25), pady=10)
        ctk.CTkLabel(stats_frm, text=f"CdA (m\N{SUPERSCRIPT TWO}):").grid(row=1, column=2, padx=(25, 5), pady=10)
        self.cda_ent = ctk.CTkEntry(stats_frm)
        self.cda_ent.insert(0, str(rider.cda) if rider.cda is not None else "")
        self.cda_ent.grid(row=1, column=3, padx=(5, 25), pady=10)

        # Physiological
        power_frm = ctk.CTkFrame(self)
        power_frm.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        SectionLabel(power_frm, "Physiological Characteristics").grid(row=0, column=0, columnspan=2, padx=(10, 0), sticky="NW")
        ctk.CTkLabel(power_frm, text="FTP (Watts):").grid(row=1, column=0, padx=(15, 5), pady=10)
        self.ftp_ent = ctk.CTkEntry(power_frm)
        self.ftp_ent.insert(0, str(rider.ftp) if rider.ftp is not None else "")
        self.ftp_ent.grid(row=1, column=1, padx=(5, 25), pady=10)
        ctk.CTkLabel(power_frm, text="wPrime (kJ):").grid(row=1, column=2, padx=(25, 5), pady=10)
        self.w_prime_ent = ctk.CTkEntry(power_frm)
        self.w_prime_ent.insert(0, str(rider.w_prime) if rider.w_prime is not None else "")
        self.w_prime_ent.grid(row=1, column=3, padx=(5, 25), pady=10)

        # Buttons
        ctk.CTkButton(self, text="Save", fg_color="green", hover_color="dark green",
                      command=self._save).grid(row=3, column=0, padx=10, pady=10)
        ctk.CTkButton(self, text="Delete", fg_color="red", hover_color="dark red",
                      command=self._delete).grid(row=3, column=1, padx=(10, 19), pady=10)
        self.alert_lbl = ctk.CTkLabel(self, text="")
        self.alert_lbl.grid(row=4, column=0, padx=10, pady=(5, 10))

    def _save(self):
        if self.controller:
            self.controller.save_rider_btn_press(
                self.rider_id,
                first_name=self.first_name_ent.get(),
                last_name=self.last_name_ent.get(),
                weight_kg=self.weight_ent.get(),
                ftp=self.ftp_ent.get(),
                w_prime=self.w_prime_ent.get(),
                cda=self.cda_ent.get(),
            )

    def _delete(self):
        if self.controller:
            self.controller.delete_rider_btn_press(self.rider_id)


class EnvironmentProfileFrame(_AlertMixin, ctk.CTkFrame):
    def __init__(self, parent, envir: Environment, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.envir_id = envir.envir_id

        # Name
        name_frm = ctk.CTkFrame(self)
        name_frm.grid_columnconfigure(4, weight=1)
        name_frm.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        SectionLabel(name_frm, "Environment Name").grid(row=0, column=0, columnspan=2, padx=(10, 0), sticky="NW")
        self.name_ent = ctk.CTkEntry(name_frm, width=300)
        self.name_ent.insert(0, envir.name or "")
        self.name_ent.grid(row=1, column=1, padx=(10, 25), pady=10)

        # Atmospheric
        atmos_frm = ctk.CTkFrame(self)
        atmos_frm.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        SectionLabel(atmos_frm, "Atmospheric Conditions").grid(row=0, column=0, columnspan=2, padx=(10, 0), sticky="NW")
        ctk.CTkLabel(atmos_frm, text=f"Air Density (kg/m\N{SUPERSCRIPT THREE}):").grid(row=1, column=0, padx=(15, 5), pady=10)
        self.air_density_ent = ctk.CTkEntry(atmos_frm)
        self.air_density_ent.insert(0, str(envir.air_density) if envir.air_density is not None else "")
        self.air_density_ent.grid(row=1, column=1, padx=(5, 25), pady=10)

        # Equipment
        equip_frm = ctk.CTkFrame(self)
        equip_frm.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        SectionLabel(equip_frm, "Equipment Characteristics").grid(row=0, column=0, columnspan=2, padx=(10, 0), sticky="NW")
        ctk.CTkLabel(equip_frm, text="Crr:").grid(row=1, column=0, padx=(15, 5), pady=10)
        self.crr_ent = ctk.CTkEntry(equip_frm)
        self.crr_ent.insert(0, str(envir.crr) if envir.crr is not None else "")
        self.crr_ent.grid(row=1, column=1, padx=(5, 25), pady=10)
        ctk.CTkLabel(equip_frm, text="Mechanical Losses:").grid(row=1, column=2, padx=(25, 5), pady=10)
        self.mech_losses_ent = ctk.CTkEntry(equip_frm)
        self.mech_losses_ent.insert(0, str(envir.mech_losses) if envir.mech_losses is not None else "")
        self.mech_losses_ent.grid(row=1, column=3, padx=(5, 25), pady=10)

        # Buttons
        ctk.CTkButton(self, text="Save", fg_color="green", hover_color="dark green",
                      command=self._save).grid(row=3, column=0, padx=10, pady=10)
        ctk.CTkButton(self, text="Delete", fg_color="red", hover_color="dark red",
                      command=self._delete).grid(row=3, column=1, padx=(10, 19), pady=10)
        self.alert_lbl = ctk.CTkLabel(self, text="")
        self.alert_lbl.grid(row=4, column=0, padx=10, pady=(5, 10))

    def _save(self):
        if self.controller:
            self.controller.save_envir_btn_press(
                self.envir_id,
                name=self.name_ent.get(),
                air_density=self.air_density_ent.get(),
                crr=self.crr_ent.get(),
                mech_losses=self.mech_losses_ent.get(),
            )

    def _delete(self):
        if self.controller:
            self.controller.delete_envir_btn_press(self.envir_id)


class SimulationProfileFrame(_AlertMixin, ctk.CTkFrame):
    def __init__(self, parent, sim: Simulation,
                 selected_rider: tuple[str, int],
                 selected_envir: tuple[str, int],
                 rider_names: list,
                 envir_names: list,
                 controller=None):
        super().__init__(parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.sim_id = sim.sim_id

        # Name
        name_frm = ctk.CTkFrame(self)
        name_frm.grid_columnconfigure(4, weight=1)
        name_frm.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        SectionLabel(name_frm, "Simulation Name").grid(row=0, column=0, columnspan=2, padx=(10, 0), sticky="NW")
        self.name_ent = ctk.CTkEntry(name_frm, width=300)
        self.name_ent.insert(0, sim.name or "")
        self.name_ent.grid(row=1, column=1, padx=(10, 25), pady=10)

        # Rider/Envir selection
        self.select_frm = RiderEnvirDropdownFrame(
            self, rider_names, selected_rider, envir_names, selected_envir)
        self.select_frm.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Power plan
        self.power_plan_frm = PowerPlanFrame(
            self, sim.power_plan.as_tuple_list(), sim_id=sim.sim_id, controller=controller)
        self.power_plan_frm.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Save/Run buttons
        btn_frm = ctk.CTkFrame(self, fg_color="transparent")
        btn_frm.grid_columnconfigure((0, 3), weight=1)
        btn_frm.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkButton(btn_frm, text="Save", fg_color="green", hover_color="dark green",
                      command=self._save).grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(btn_frm, text="Run", fg_color="green", hover_color="dark green",
                      command=self._run).grid(row=0, column=2, padx=10, pady=10)
        ctk.CTkButton(self, text="Delete", fg_color="red", hover_color="dark red",
                      command=self._delete).grid(row=3, column=1, padx=(10, 19), pady=10)
        self.alert_lbl = ctk.CTkLabel(self, text="")
        self.alert_lbl.grid(row=4, column=0, padx=10, pady=(5, 10))

    def _save(self):
        if self.controller:
            rider = self.select_frm.get_rider()
            envir = self.select_frm.get_envir()
            self.controller.save_sim_btn_press(
                self.sim_id,
                name=self.name_ent.get(),
                rider_id=rider[1] if rider[1] != -1 else None,
                envir_id=envir[1] if envir[1] != -1 else None,
            )

    def _run(self):
        self._save()
        if self.controller:
            self.controller.run_sim_btn_press(self.sim_id)

    def _delete(self):
        if self.controller:
            self.controller.delete_sim_btn_press(self.sim_id)


class AeroTestProfileFrame(_AlertMixin, ctk.CTkFrame):
    def __init__(self, parent, aero_test: AeroTest,
                 selected_rider: tuple[str, int],
                 selected_envir: tuple[str, int],
                 rider_names: list,
                 envir_names: list,
                 controller=None):
        super().__init__(parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.aero_test_id = aero_test.aero_test_id
        self.data_file = aero_test.data_file or ""

        # Name
        name_frm = ctk.CTkFrame(self)
        name_frm.grid_columnconfigure(4, weight=1)
        name_frm.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        SectionLabel(name_frm, "Aero Test Name").grid(row=0, column=0, columnspan=2, padx=(10, 0), sticky="NW")
        self.name_ent = ctk.CTkEntry(name_frm, width=300)
        self.name_ent.insert(0, aero_test.name or "")
        self.name_ent.grid(row=1, column=1, padx=(10, 25), pady=10)

        # Rider/Envir selection
        self.select_frm = RiderEnvirDropdownFrame(
            self, rider_names, selected_rider, envir_names, selected_envir)
        self.select_frm.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # File selector
        file_frm = ctk.CTkFrame(self)
        file_frm.grid_columnconfigure(4, weight=1)
        file_frm.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        SectionLabel(file_frm, "Data File (FIT)").grid(row=0, column=0, columnspan=2, padx=(10, 0), sticky="NW")
        self.file_ent = ctk.CTkEntry(file_frm, width=500)
        self.file_ent.insert(0, Path(self.data_file).name if self.data_file else "")
        self.file_ent.configure(state="disabled")
        self.file_ent.grid(row=1, column=0, padx=(10, 10), pady=10)
        ctk.CTkButton(file_frm, text="Select File",
                      command=self._select_file).grid(row=1, column=1, padx=(10, 10), pady=10)

        # Save/Calculate buttons
        btn_frm = ctk.CTkFrame(self, fg_color="transparent")
        btn_frm.grid_columnconfigure((0, 3), weight=1)
        btn_frm.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkButton(btn_frm, text="Save", fg_color="green", hover_color="dark green",
                      command=self._save).grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(btn_frm, text="Calculate", fg_color="green", hover_color="dark green",
                      command=self._calculate).grid(row=0, column=2, padx=10, pady=10)
        ctk.CTkButton(self, text="Delete", fg_color="red", hover_color="dark red",
                      command=self._delete).grid(row=4, column=1, padx=(10, 19), pady=10)
        self.alert_lbl = ctk.CTkLabel(self, text="")
        self.alert_lbl.grid(row=5, column=0, padx=10, pady=(5, 10))

    def _select_file(self):
        initial_dir = str(Path(self.data_file).parent) if self.data_file else str(Path.home())
        fname = filedialog.askopenfilename(
            title="Select FIT File",
            initialdir=initial_dir,
            filetypes=[("FIT files", "*.fit"), ("All files", "*.*")],
        )
        if fname:
            self.file_ent.configure(state="normal")
            self.file_ent.delete(0, "end")
            self.file_ent.insert(0, Path(fname).name)
            self.file_ent.configure(state="disabled")
            self.data_file = fname

    def _save(self):
        if self.controller:
            rider = self.select_frm.get_rider()
            envir = self.select_frm.get_envir()
            self.controller.save_aero_test_btn_press(
                self.aero_test_id,
                name=self.name_ent.get(),
                rider_id=rider[1] if rider[1] != -1 else None,
                envir_id=envir[1] if envir[1] != -1 else None,
                data_file=self.data_file or None,
            )

    def _calculate(self):
        self._save()
        if self.controller:
            self.controller.calc_aero_test_btn_press(self.aero_test_id)

    def _delete(self):
        if self.controller:
            self.controller.delete_aero_test_btn_press(self.aero_test_id)


# ------ Simulation results window ------

class SimulationWindow(ctk.CTkToplevel):
    def __init__(self, root, sim_name: str = "Simulation",
                 time=None, power=None, velocity=None, splits=None, split_table=None):
        super().__init__(root)
        self.title("Simulation")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text=sim_name, font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=20, pady=(20, 10))

        plot_frm = ctk.CTkFrame(self)
        plot_frm.grid_columnconfigure(0, weight=1, minsize=300)
        plot_frm.grid_rowconfigure((0, 1), weight=1, minsize=200)
        plot_frm.grid(row=1, column=0, sticky="nsew")

        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

        self.velocity_fig = Figure()
        power_ax = self.velocity_fig.gca()
        velocity_ax = power_ax.twinx()  # two y-axes sharing one x-axis

        c = colors[0]
        velocity_ln = velocity_ax.plot(time, velocity, color=c, label='Velocity')
        velocity_ax.tick_params(axis='y', labelcolor=c)
        velocity_ax.set_ylabel("kph", color=c)
        velocity_ax.set_ylim(bottom=0)
        velocity_ax.grid(True, axis='y', color=c)

        c = colors[1]
        power_ln = power_ax.plot(time, power, color=c, label="Power")
        power_ax.tick_params(axis='y', labelcolor=c)
        power_ax.set_ylabel("Watts", color=c)
        power_ax.set_ylim(bottom=0)
        power_ax.grid(True, axis='y', color=c)

        velocity_ax.set_title("Velocity & Power")
        velocity_ax.set_xlabel("time (s)")
        velocity_ax.set_xlim(left=-1, right=time[-1] + 1)
        velocity_ax.grid(True, axis='x')
        lines = velocity_ln + power_ln
        velocity_ax.legend(lines, [l.get_label() for l in lines], framealpha=1)

        FigureCanvasTkAgg(self.velocity_fig, master=plot_frm).get_tk_widget().grid(
            row=0, column=0, sticky="nsew")

        self.split_fig = Figure()
        split_ax = self.split_fig.gca()
        c = colors[2]
        split_ax.plot(splits, color=c, marker='.')
        split_ax.tick_params(axis='y', labelcolor=c)
        split_ax.grid(True, axis='y', color=c)
        split_ax.set_title("Lap Times")
        split_ax.set_xlabel("Lap")
        split_ax.set_ylabel("time (seconds)", color=c)
        FigureCanvasTkAgg(self.split_fig, master=plot_frm).get_tk_widget().grid(
            row=1, column=0, sticky="nsew")

        splits_frm = ctk.CTkScrollableFrame(self, width=1000, corner_radius=0)
        splits_frm.grid_columnconfigure(0, weight=1)
        splits_frm.grid_rowconfigure(0, weight=1)
        tbl = CustomTable(splits_frm, table_values=split_table, outside_border_width=2)
        splits_frm.grid(row=1, column=1, sticky="nsew")
        extra_pad = 5
        tbl.grid(row=0, column=0, padx=extra_pad)

        self.update_idletasks()
        splits_frm.configure(width=tbl.winfo_width() + 2 * extra_pad)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        # Explicitly close matplotlib figures to free memory; they are not freed
        # automatically when the Tkinter widget is destroyed.
        plt.close(self.velocity_fig)
        plt.close(self.split_fig)
        self.destroy()


# ------ Main View ------

class View(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.controller = None

        self.grid_columnconfigure((0, 1), weight=0)
        self.grid_columnconfigure(0, minsize=200)
        self.grid_columnconfigure(1, minsize=150)
        self.grid_columnconfigure(2, weight=1, minsize=200)
        self.grid_rowconfigure(0, weight=1)

        # Left nav panel
        self.top_select_frm = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray60", "black"))
        self.top_select_frm.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.top_select_frm, text="WOTTProject",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        ctk.CTkFrame(self.top_select_frm, corner_radius=0, height=2,
                     fg_color=("dark slate gray", "gray60")).grid(row=1, column=0, pady=(10, 5))

        ctk.CTkButton(self.top_select_frm, text="Rider Profiles",
                      command=self._rider_btn).grid(row=2, column=0, pady=5)
        ctk.CTkButton(self.top_select_frm, text="Environments",
                      command=self._envir_btn).grid(row=3, column=0, pady=5)
        ctk.CTkButton(self.top_select_frm, text="Simulations",
                      command=self._sim_btn).grid(row=4, column=0, pady=5)

        ctk.CTkFrame(self.top_select_frm, corner_radius=0, height=2,
                     fg_color=("dark slate gray", "gray60")).grid(row=5, column=0, pady=5)

        ctk.CTkButton(self.top_select_frm, text="Aero Testing",
                      command=self._aero_test_btn).grid(row=6, column=0, pady=5)

        self.top_select_frm.grid(row=0, column=0, sticky="nsew")

        self.sub_select_frm = ctk.CTkFrame(self, corner_radius=0)
        self.sub_select_frm.grid(row=0, column=1, sticky="nsew")

        self.clear_main_content()

        self.sim_windows: dict = {}

    def set_controller(self, controller):
        self.controller = controller

    def _rider_btn(self):
        if self.controller:
            self.controller.rider_btn_press()

    def _envir_btn(self):
        if self.controller:
            self.controller.envir_btn_press()

    def _sim_btn(self):
        if self.controller:
            self.controller.sim_btn_press()

    def _aero_test_btn(self):
        if self.controller:
            self.controller.aero_test_btn_press()

    # ------ update methods ------

    def clear_main_content(self):
        self.main_content_frm = ctk.CTkFrame(self, corner_radius=0)
        self.main_content_frm.grid(row=0, column=2, sticky="nsew")

    def show_rider_selection_list(self, name_ids: list):
        self.sub_select_frm = RiderSelectFrame(self, name_ids, self.controller)
        self.sub_select_frm.grid(row=0, column=1, sticky="nsew")

    def show_envir_selection_list(self, name_ids: list):
        self.sub_select_frm = EnvirSelectFrame(self, name_ids, self.controller)
        self.sub_select_frm.grid(row=0, column=1, sticky="nsew")

    def show_sim_selection_list(self, name_ids: list):
        self.sub_select_frm = SimSelectFrame(self, name_ids, self.controller)
        self.sub_select_frm.grid(row=0, column=1, sticky="nsew")

    def show_aero_test_selection_list(self, name_ids: list):
        self.sub_select_frm = AeroTestSelectFrame(self, name_ids, self.controller)
        self.sub_select_frm.grid(row=0, column=1, sticky="nsew")

    def show_rider_detail(self, rider: Rider):
        self.main_content_frm = RiderProfileFrame(self, rider, self.controller)
        self.main_content_frm.grid(row=0, column=2, sticky="nsew")

    def show_envir_detail(self, envir: Environment):
        self.main_content_frm = EnvironmentProfileFrame(self, envir, self.controller)
        self.main_content_frm.grid(row=0, column=2, sticky="nsew")

    def show_sim_detail(self, sim: Simulation, selected_rider: tuple,
                        selected_envir: tuple, rider_names: list, envir_names: list):
        self.main_content_frm = SimulationProfileFrame(
            self, sim, selected_rider, selected_envir, rider_names, envir_names, self.controller)
        self.main_content_frm.grid(row=0, column=2, sticky="nsew")

    def show_aero_test_detail(self, aero_test: AeroTest, selected_rider: tuple,
                               selected_envir: tuple, rider_names: list, envir_names: list):
        self.main_content_frm = AeroTestProfileFrame(
            self, aero_test, selected_rider, selected_envir, rider_names, envir_names, self.controller)
        self.main_content_frm.grid(row=0, column=2, sticky="nsew")

    def show_detail_error(self, message):
        # main_content_frm is a plain CTkFrame when no detail panel is open
        # (see clear_main_content), so guard before calling the mixin method.
        if hasattr(self.main_content_frm, 'show_alert_error'):
            self.main_content_frm.show_alert_error(message)

    def show_detail_success(self, message):
        if hasattr(self.main_content_frm, 'show_alert_success'):
            self.main_content_frm.show_alert_success(message)

    def show_sim_window(self, sim_id: int, sim_name: str, results: dict):
        # Close any existing results window for this sim before opening a new one.
        if sim_id in self.sim_windows:
            self.sim_windows[sim_id]._on_close()
        window = SimulationWindow(self, sim_name=sim_name, **results)
        self.sim_windows[sim_id] = window
