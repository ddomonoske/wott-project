import tkinter as tk
import customtkinter as ctk
from typing import List, Callable, Optional, Union, Tuple
from functools import partial


class ScrollableBtnList(ctk.CTkScrollableFrame):
    def __init__(self, parent, name_ids: List[tuple[str, int]],
                 callback: Callable[[int], None] = None, *args, **kwargs):
        super().__init__(parent, fg_color=("gray70", "gray10"), width=1, corner_radius=0, *args, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.name_btns = []
        fg_color = self.cget("fg_color")

        for i, (name, id_) in enumerate(name_ids, start=1):
            btn = ctk.CTkButton(self, text=name, corner_radius=0, border_width=1,
                                border_color=fg_color, command=partial(callback, id_))
            self.name_btns.append(btn)
            btn.grid(row=i, column=0, sticky="EW")


class CustomTable(ctk.CTkFrame):
    def __init__(self, parent,
                 table_values: List[List[str]],
                 column_widths: List[int] = None,
                 border_color: Union[str, Tuple[str, str]] = ("dark slate gray", "gray60"),
                 border_width: int = 1,
                 outside_border_width: int = 1,
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 **kwargs):
        super().__init__(parent, corner_radius=0, fg_color=border_color, border_width=0, **kwargs)

        self.border = ctk.CTkFrame(self, corner_radius=0, fg_color=border_color, border_width=0, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.border.grid(row=0, column=0, padx=outside_border_width, pady=outside_border_width, sticky="nsew")

        if fg_color is None:
            fg_color = parent.cget("fg_color")

        for row, cells in enumerate(table_values):
            for col, value in enumerate(cells):
                try:
                    width = column_widths[col]
                except (TypeError, IndexError):
                    width = None
                if row == 0:
                    cell = ctk.CTkLabel(self.border, text=str(value),
                                        font=ctk.CTkFont(weight="bold"), fg_color=fg_color)
                    cell.grid(row=row, column=col, sticky="nsew",
                              padx=border_width, pady=(border_width, border_width + 1),
                              ipadx=5, ipady=2)
                else:
                    cell = ctk.CTkLabel(self.border, text=str(value), fg_color=fg_color)
                    cell.grid(row=row, column=col, sticky="nsew",
                              padx=border_width, pady=border_width,
                              ipadx=5, ipady=2)


class NameIDOptionMenu(ctk.CTkOptionMenu):
    def __init__(self, parent,
                 name_ids: List[tuple[str, int]],
                 selection: tuple[str, int] = ("", -1),
                 callback: Callable[[int], None] = None,
                 **kwargs):
        self.name_ids = name_ids
        self.callback = callback
        self.selection = selection

        # Build a unique string→id map (append integer suffix for duplicate names)
        self.name_id_map: dict[str, int] = {}
        for name, id_ in name_ids:
            suffix = 0
            while True:
                key = name + (str(suffix) if suffix else "")
                if key not in self.name_id_map:
                    break
                suffix += 1
            self.name_id_map[key] = id_
            if selection[1] == id_:
                self.selection = (key, id_)

        super().__init__(parent, values=list(self.name_id_map.keys()),
                         command=self._menu_callback, **kwargs)
        self.set(self.selection[0])

    def _menu_callback(self, name: str):
        if self.callback:
            self.callback(self.name_id_map[name])

    def get(self) -> tuple[str, int]:
        name = super().get()
        return (name, self.name_id_map.get(name, -1))


class SectionLabel(ctk.CTkLabel):
    def __init__(self, parent, text: str = ""):
        super().__init__(parent, text=text, font=ctk.CTkFont(size=15, weight="bold"))


class RiderEnvirDropdownFrame(ctk.CTkFrame):
    def __init__(self, parent, rider_list, selected_rider, envir_list, selected_envir):
        super().__init__(parent)
        self.grid_columnconfigure(4, weight=1)
        SectionLabel(self, "Rider and Environment").grid(
            row=0, column=0, columnspan=2, padx=(10, 0), sticky="NW")
        ctk.CTkLabel(self, text="Rider:").grid(row=1, column=0, padx=(15, 5), pady=(10, 10))
        self.rider_opt = NameIDOptionMenu(self, rider_list, selected_rider)
        self.rider_opt.grid(row=1, column=1, padx=(5, 25), pady=(10, 10))
        ctk.CTkLabel(self, text="Envir:").grid(row=1, column=2, padx=(25, 5), pady=(10, 10))
        self.envir_opt = NameIDOptionMenu(self, envir_list, selected_envir)
        self.envir_opt.grid(row=1, column=3, padx=(5, 25), pady=(10, 10))

    def get_rider(self) -> tuple[str, int]:
        return self.rider_opt.get()

    def get_envir(self) -> tuple[str, int]:
        return self.envir_opt.get()


class PowerPlanPointView(ctk.CTkFrame):
    _PAD = 10
    _ENTRY_W = 60
    _BTN_SZ = 10

    def __init__(self, parent, point: tuple[str, str, str],
                 save_callback: Callable = None,
                 up_callback: Callable = None,
                 down_callback: Callable = None,
                 delete_callback: Callable = None):
        super().__init__(parent)
        self.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Start (seconds): ").grid(row=0, column=0, sticky="w", padx=(self._PAD, 0))
        self.start_ent = ctk.CTkEntry(self, width=self._ENTRY_W)
        self.start_ent.insert(0, point[0])
        self.start_ent.configure(state="disabled")
        self.start_ent.grid(row=0, column=1, sticky="w", padx=(0, self._PAD))

        ctk.CTkLabel(self, text="Power (Watts): ").grid(row=0, column=2, padx=(self._PAD, 0))
        self.power_ent = ctk.CTkEntry(self, width=self._ENTRY_W)
        self.power_ent.insert(0, point[1])
        self.power_ent.grid(row=0, column=3, padx=(0, self._PAD))

        ctk.CTkLabel(self, text="Duration (seconds): ").grid(row=0, column=4, padx=(self._PAD, 0))
        self.duration_ent = ctk.CTkEntry(self, width=self._ENTRY_W)
        self.duration_ent.insert(0, point[2])
        self.duration_ent.grid(row=0, column=5, padx=(0, self._PAD))

        ctk.CTkButton(self, width=20, text="Save", command=save_callback).grid(
            row=0, column=6, padx=self._PAD)
        ctk.CTkButton(self, width=self._BTN_SZ, height=self._BTN_SZ,
                      text="\N{DOWNWARDS ARROW}", command=down_callback).grid(
            row=0, column=7, padx=(self._PAD, 0))
        ctk.CTkButton(self, width=self._BTN_SZ, height=self._BTN_SZ,
                      text="\N{UPWARDS ARROW}", command=up_callback).grid(
            row=0, column=8, padx=(0, self._PAD))
        ctk.CTkButton(self, width=self._BTN_SZ, height=self._BTN_SZ,
                      text="\N{LATIN CAPITAL LETTER X}", command=delete_callback).grid(
            row=0, column=9, padx=self._PAD)

    def get_entries(self) -> tuple[float, float, float]:
        return (float(self.start_ent.get()),
                float(self.power_ent.get()),
                float(self.duration_ent.get()))


class PowerPlanFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, power_plan: list[tuple], sim_id: int = -1, controller=None):
        super().__init__(parent, height=400)
        self.controller = controller
        self.sim_id = sim_id
        self.rows: list[PowerPlanPointView] = []
        n = len(power_plan) if power_plan else 0

        SectionLabel(self, "Power Plan").grid(row=0, column=0, columnspan=2, padx=(10, 0), sticky="NW")

        for i, point in enumerate(power_plan):
            row = PowerPlanPointView(
                self, point,
                save_callback=partial(self._save, i),
                up_callback=partial(self._move_up, i),
                down_callback=partial(self._move_down, i),
                delete_callback=partial(self._delete, i),
            )
            row.grid(row=i + 1, column=0, padx=10, pady=3, ipady=3)
            self.rows.append(row)

        ctk.CTkButton(self, width=20, text="Add \N{FULLWIDTH PLUS SIGN}",
                      command=self._add).grid(row=n + 1, column=0, pady=5)

    def _save(self, i: int):
        if self.controller:
            self.controller.save_power_point(self.sim_id, i, self.rows[i].get_entries())

    def _move_up(self, i: int):
        if i > 0 and self.controller:
            self.controller.swap_power_points(self.sim_id, i, i - 1)

    def _move_down(self, i: int):
        if i < len(self.rows) - 1 and self.controller:
            self.controller.swap_power_points(self.sim_id, i, i + 1)

    def _delete(self, i: int):
        if self.controller:
            self.controller.delete_power_point(self.sim_id, i)

    def _add(self):
        if self.controller:
            self.controller.add_power_point(self.sim_id)
