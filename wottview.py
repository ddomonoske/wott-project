import tkinter as tk
import customtkinter as ctk
from typing import List
from functools import partial

class View(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.controller = None

        # set up grid scaling
        self.grid_columnconfigure((0,1), weight=0)
        self.grid_columnconfigure(0, minsize=200)
        self.grid_columnconfigure(1, minsize=150)
        self.grid_columnconfigure(2, weight=1, minsize=200)
        self.grid_rowconfigure(0,weight=1)

        # top selection frame
        self.topSelect_frm = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray60", "black"))
        self.topSelect_frm.grid_columnconfigure(0, weight=1)

        # logo
        self.logo_lbl = ctk.CTkLabel(self.topSelect_frm, text="WOTTProject", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_lbl.grid(row=0, column=0, padx=20, pady=(20, 10))

        # top selection buttons
        self.rider_btn = ctk.CTkButton(self.topSelect_frm,
                                       text="Rider Profiles",
                                       command=self.riderBtnPress)
        self.rider_btn.grid(row=1, column=0, pady=5)
        self.envir_btn = ctk.CTkButton(self.topSelect_frm,
                                       text="Environments",
                                       command=self.envirBtnPress)
        self.envir_btn.grid(row=2, column=0, pady=5)
        self.sim_btn = ctk.CTkButton(self.topSelect_frm,
                                     text="Simulations",
                                     command=self.simBtnPress)
        self.sim_btn.grid(row=3, column=0, pady=5)

        self.topSelect_frm.grid(row=0, column=0, padx=0, pady=0, sticky="news")

        # sub selection frame, empty at first
        self.subSelect_frm = ctk.CTkFrame(self, corner_radius=0)
        self.subSelect_frm.grid(row=0, column=1, padx=0, pady=0, sticky="news")

        # main content frame, empty at first
        self.mainContent_frm = ctk.CTkFrame(self, corner_radius=0)
        self.mainContent_frm.grid(row=0, column=2, padx=0, pady=0, sticky="news")

        # rider frame
        self.rider_frm = RiderProfilesFrame(self)

        # create environment frame
        self.envir_frm = EnvironmentProfilesFrame(self)

        # create simulations frame
        self.sim_frm = SimulationProfilesFrame(self)

    """ ------ connect controller ------ """
    def setController(self, controller):
        self.controller = controller

    """ ------ button handlers ------ """
    def riderBtnPress(self):
        if self.controller:
            self.controller.riderBtnPress()

    def envirBtnPress(self):
        if self.controller:
            self.controller.envirBtnPress()

    def simBtnPress(self):
        if self.controller:
            self.controller.simBtnPress()

    """ ------ update view methods ------ """

    # TODO give this column a title, which would require different methods for rider, envir, and sim
    # to update entire view when top level buttons are clicked
    def updateSubSelectionFrame(self, list: List[str]):
        # show list of riders in sub selection frame
        self.subSelect_frm = SubSelectFrame(self, list, self.controller)
        self.subSelect_frm.grid(row=0, column=1, padx=0, pady=0, sticky="NSEW")
        # TODO clear main content frame

    def showRiderDetail(rider):
        # TODO show rider details in main content frame
        rider

    def showEnvirDetail(envir):
        # TODO show environment details in main content frame
        envir

    def showSimDetail(sim):
        # TODO show sim details in main content frame
        sim

# TODO split SubSelectFrame into a more general scrollable list of buttons
# General scrollable frame for riders, environments, or simulations
class SubSelectFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, names: List[str], controller=None):
        super().__init__(parent, fg_color=("gray70", "gray10"), width=1, corner_radius=0)

        self.controller = controller

        self.grid_columnconfigure(0, weight=1)

        # list of btns for each name
        self.name_btns = []

        # Add button
        self.add_btn = ctk.CTkButton(self, text="Add New", fg_color="green", hover_color="dark green", width=50)
        self.add_btn.grid(row=0, column=0, pady=(30,10))

        # get frame color for "transparent" border
        fg_color = self.cget("fg_color")

        # Create a btn for each name and append to list
        for i, name in enumerate(names, start=1):
            btn = ctk.CTkButton(self, text=name, corner_radius=0, border_width=1, border_color=fg_color,
                                command=partial(self.subSelectBtnPress, name))
            self.name_btns.append(btn)
            btn.grid(row=i, column=0, sticky="EW")

    """ ------ connect controller ------ """
    def setController(self, controller):
        self.controller = controller

    def subSelectBtnPress(self, name: str):
        if self.controller:
            self.controller.subSelectBtnPress(name)

# Rider Profiles main content frame
class RiderProfilesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

# Environment Profiles main content frame
class EnvironmentProfilesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

# Simulation Profiles main content frame
class SimulationProfilesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
