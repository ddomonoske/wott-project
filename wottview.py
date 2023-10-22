import tkinter as tk
import customtkinter as ctk
from typing import List, Dict, Callable
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
        self.rider_frm = RiderProfileFrame(self)

        # create environment frame
        self.envir_frm = EnvironmentProfileFrame(self)

        # create simulations frame
        self.sim_frm = SimulationProfileFrame(self)

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
    # update entire view when main Rider button is pressed
    def showRiderSelectionList(self, list: List[tuple[str,int]]):
        # show list of riders in sub selection frame
        self.subSelect_frm = RiderSelectFrame(self, list, self.controller)
        self.subSelect_frm.grid(row=0, column=1, padx=0, pady=0, sticky="NSEW")
        # TODO clear main content frame

    # update entire view when main Environment button is pressed
    def showEnvirSelectionList(self, list: List[tuple[str,int]]):
        # show list of environments in sub selection frame
        self.subSelect_frm = EnvirSelectFrame(self, list, self.controller)
        self.subSelect_frm.grid(row=0, column=1, padx=0, pady=0, sticky="NSEW")
        # TODO clear main content frame

    # update entire view when main Simulation button is pressed
    def showSimSelectionList(self, list: List[tuple[str,int]]):
        # show list of simulations in sub selection frame
        self.subSelect_frm = SimSelectFrame(self, list, self.controller)
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

# Generalized scrollable list of buttons
class ScrollableBtnList(ctk.CTkScrollableFrame):
    def __init__(self, parent, nameIDs: List[tuple[str,int]], callback: Callable[[int],None]=None, *args, **kwargs):
        # TODO check this is the correct way to use args/kwargs
        super().__init__(parent, fg_color=("gray70", "gray10"), width=1, corner_radius=0, *args, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # list of btns for each name
        self.name_btns = []

        # get frame color for "transparent" border
        fg_color = self.cget("fg_color")

        # Create a btn for each name and append to list
        for i, idName in enumerate(nameIDs, start=1):
            name = idName[0]
            id = idName[1]
            btn = ctk.CTkButton(self, text=name, corner_radius=0, border_width=1, border_color=fg_color,
                                command=partial(callback, id))
            self.name_btns.append(btn)
            btn.grid(row=i, column=0, sticky="EW")

class RiderSelectFrame(ctk.CTkFrame):
    def __init__(self, parent, nameIDs: List[tuple[str,int]], controller=None):
        super().__init__(parent, fg_color=("gray70", "gray10"), width=1, corner_radius=0)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Add rider button
        self.add_btn = ctk.CTkButton(self, text="Add Rider", fg_color="green", hover_color="dark green", width=50,
                                     command=self.addRiderBtnPress)
        self.add_btn.grid(row=0, column=0, pady=(30,10))

        # Scroll list of riders
        self.riders_list = ScrollableBtnList(self, nameIDs, self.scrollBtnPress)
        self.riders_list.grid(row=1, column=0, sticky="NSEW")

    """ ------ button callbacks ------ """
    def addRiderBtnPress(self):
        if self.controller:
            self.controller.addRiderBtnPress()

    def scrollBtnPress(self, id: int):
        if self.controller:
            self.controller.riderSelectBtnPress(id)

class EnvirSelectFrame(ctk.CTkFrame):
    def __init__(self, parent, nameIDs: List[tuple[str,int]], controller=None):
        super().__init__(parent, fg_color=("gray70", "gray10"), width=1, corner_radius=0)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Add environment button
        self.add_btn = ctk.CTkButton(self, text="Add Environment", fg_color="green", hover_color="dark green", width=50,
                                     command=self.addEnvirBtnPress)
        self.add_btn.grid(row=0, column=0, pady=(30,10))

        # Scroll list of environments
        self.envirs_list = ScrollableBtnList(self, nameIDs, self.scrollBtnPress)
        self.envirs_list.grid(row=1, column=0, sticky="NSEW")

        """ ------ button callbacks ------ """
    def addEnvirBtnPress(self):
        if self.controller:
            self.controller.addEnvirBtnPress()

    def scrollBtnPress(self, id: int):
        if self.controller:
            self.controller.envirSelectBtnPress(id)

class SimSelectFrame(ctk.CTkFrame):
    def __init__(self, parent, nameIDs: List[tuple[str,int]], controller=None):
        super().__init__(parent, fg_color=("gray70", "gray10"), width=1, corner_radius=0)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Add environment button
        self.add_btn = ctk.CTkButton(self, text="Add Simulation", fg_color="green", hover_color="dark green", width=50,
                                     command=self.addSimBtnPress)
        self.add_btn.grid(row=0, column=0, pady=(30,10))

        # Scroll list of environments
        self.sims_list = ScrollableBtnList(self, nameIDs, self.scrollBtnPress)
        self.sims_list.grid(row=1, column=0, sticky="NSEW")

        """ ------ button callbacks ------ """
    def addSimBtnPress(self):
        if self.controller:
            self.controller.addSimBtnPress()

    def scrollBtnPress(self, id: int):
        if self.controller:
            self.controller.simSelectBtnPress(id)


# Rider Profiles main content frame
class RiderProfileFrame(ctk.CTkFrame):
    # same as wottmodel.Rider.attributes
    class attributes:
        RIDERID = "riderID"
        FIRSTNAME = "firstName"
        LASTNAME = "lastName"
        WEIGHT = "weight"
        FTP = "FTP"
        WPRIME = "wPrime"
        CDA = "CdA"
        POWERRESULTS = "powerResults"

    def __init__(self, parent, controller = None,
                 riderID: int = -1,
                 firstName: str = "",
                 lastName: str = "",
                 weight: str = "",
                 FTP: str = "",
                 wPrime: str = "",
                 CdA: str = "",
                 powerResults: Dict[str, str] = {},
                 attributeDict: Dict[str, object] = {}):
        super().__init__(parent)

        self.controller = controller

        self.grid_columnconfigure(0, weight=1)

        self.riderID = riderID
        self.firstName = firstName
        self.lastName = lastName
        self.weight = weight
        self.FTP = FTP
        self.wPrime = wPrime
        self.CdA = CdA
        self.powerResults = powerResults

        if attributeDict:
            self.setAttribute(attributeDict)


        """ ------ set up the geometry ------ """
        # Name section
        self.nameFrm = ctk.CTkFrame(self)
        self.nameFrm.columnconfigure(4, weight=1)
        self.nameFrm.grid(row=0, column=0, padx=(10,10), pady=(10,10), sticky="NSEW")
        self.nameLbl = SectionLabel(self.nameFrm, "Rider Name")
        self.nameLbl.grid(row=0, column=0, columnspan=2, padx=(10,0), sticky="NW")
        self.firstNameLbl = ctk.CTkLabel(self.nameFrm, text="First Name:")
        self.firstNameLbl.grid(row=1, column=0, padx=(15,5), pady=(10,10))
        self.firstNameEnt = ctk.CTkEntry(self.nameFrm, textvariable=self.firstName)
        self.firstNameEnt.grid(row=1, column=1, padx=(5,25), pady=(10,10))
        self.lastNameLbl = ctk.CTkLabel(self.nameFrm, text="Last Name:")
        self.lastNameLbl.grid(row=1, column=2, padx=(25,5), pady=(10,10))
        self.lastNameEnt = ctk.CTkEntry(self.nameFrm, textvariable=lastName)
        self.lastNameEnt.grid(row=1, column=3, padx=(5,25), pady=(10,10))

        # Physical stats section
        self.statsFrm = ctk.CTkFrame(self)
        self.statsFrm.grid(row=1, column=0, padx=(10,10), pady=(10,10), sticky="NSEW")
        self.statsLbl = SectionLabel(self.statsFrm, "Physical Characteristics")
        self.statsLbl.grid(row=0, column=0, columnspan=2, padx=(10,0), sticky="NW")
        self.weightLbl = ctk.CTkLabel(self.statsFrm, text="Weight (kg):")
        self.weightLbl.grid(row=1, column=0, padx=(15,5), pady=(10,10))
        self.weightEnt = ctk.CTkEntry(self.statsFrm, textvariable=self.weight)
        self.weightEnt.grid(row=1, column=1, padx=(5,25), pady=(10,10))
        self.CdALbl = ctk.CTkLabel(self.statsFrm, text=f"CdA (m\N{SUPERSCRIPT TWO}):")
        self.CdALbl.grid(row=1, column=2, padx=(25,5), pady=(10,10))
        self.CdAEnt = ctk.CTkEntry(self.statsFrm, textvariable=self.CdA)
        self.CdAEnt.grid(row=1, column=3, padx=(5,25), pady=(10,10))

        # FTP and wPrime section
        self.powerFrm = ctk.CTkFrame(self)
        self.powerFrm.grid(row=2, column=0, padx=(10,10), pady=(10,10), sticky="NSEW")
        self.powerLbl = SectionLabel(self.powerFrm, "Physiological Characteristics")
        self.powerLbl.grid(row=0, column=0, columnspan=2, padx=(10,0), sticky="NW")
        self.FTPLbl = ctk.CTkLabel(self.powerFrm, text="FTP (Watts):")
        self.FTPLbl.grid(row=1, column=0, padx=(15,5), pady=(10,10))
        self.FTPEnt = ctk.CTkEntry(self.powerFrm, textvariable=self.FTP)
        self.FTPEnt.grid(row=1, column=1, padx=(5,25), pady=(10,10))
        self.wPrimeLbl = ctk.CTkLabel(self.powerFrm, text="wPrime (kJ):")
        self.wPrimeLbl.grid(row=1, column=2, padx=(25,5), pady=(10,10))
        self.wPrimeEnt = ctk.CTkEntry(self.powerFrm, textvariable=self.wPrime)
        self.wPrimeEnt.grid(row=1, column=3, padx=(5,25), pady=(10,10))

        # Save Rider button
        self.saveBtn = ctk.CTkButton(self, text="Save", fg_color="green", hover_color="dark green",
                                     command=self.saveRiderBtnPress)
        self.saveBtn.grid(row=3, column=0, padx=(10,10), pady=(10,10))

    # exactly the same as wottmodel.Rider.setProperty
    def setAttribute(self, attributeDict: Dict[str, object]):
        for attribute, value in attributeDict.items():
            match attribute:
                # TODO change all of these to
                case self.attributes.RIDERID:
                    self.riderID = value
                case self.attributes.FIRSTNAME:
                    self.firstName = value
                case self.attributes.LASTNAME:
                    self.lastName = value
                case self.attributes.WEIGHT:
                    self.weight = value
                case self.attributes.FTP:
                    self.FTP = value
                case self.attributes.WPRIME:
                    self.wPrime = value
                case self.attributes.CDA:
                    self.CdA = value
                case self.attributes.POWERRESULTS:
                    self.powerResults = value
                case _:
                    pass

    def saveRiderBtnPress(self):
        # update the internal variables
        self.firstName = self.firstNameEnt.get()
        self.lastName = self.lastNameEnt.get()
        self.weight = self.weightEnt.get()
        self.FTP = self.FTPEnt.get()
        self.wPrime = self.wPrimeEnt.get()
        self.CdA = self.CdAEnt.get()
        # TODO get powerresults, or maybe they're already updated elsewhere

        # send to controller
        if self.controller:
            attributeDict = {self.attributes.FIRSTNAME: self.firstName,
                             self.attributes.LASTNAME: self.lastName,
                             self.attributes.WEIGHT: self.weight,
                             self.attributes.FTP: self.FTP,
                             self.attributes.WPRIME: self.wPrime,
                             self.attributes.CDA: self.CdA,
                             self.attributes.POWERRESULTS: self.powerResults}

            self.controller.saveRiderBtnPress(self.riderID, attributeDict)

# Environment Profiles main content frame
class EnvironmentProfileFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

# Simulation Profiles main content frame
class SimulationProfileFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

class SectionLabel(ctk.CTkLabel):
    def __init__(self, parent, text: str = ""):
        super().__init__(parent, text=text, font=ctk.CTkFont(size=15, weight="bold"))
