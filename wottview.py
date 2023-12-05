import tkinter as tk
import customtkinter as ctk
from typing import List, Dict, Callable, Union, Tuple, Optional
from functools import partial
from wottattributes import *

# for plotting
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

matplotlib.use('TkAgg') # setup plotting to use tkinter background

# use plt style that works for light and dark theme
plt.style.use('bmh')
plt.rcParams.update({
    "figure.facecolor": "LightGray"
})

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

class CustomTable(ctk.CTkFrame):
    def __init__(self, parent,
                 table_values: List[List[str]],
                 column_widths: List[int] = None,
                 border_color: Union[str, Tuple[str, str]] = ("dark slate gray","gray60"),
                 border_width: int = 1,
                 outside_border_width: int = 1,
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 **kwargs):
        super().__init__(parent,
                         corner_radius=0,
                         fg_color=border_color,
                         border_width=0,
                         **kwargs)

        # hacky frame in frame to get the border I want
        self.border = ctk.CTkFrame(self,
                                   corner_radius=0,
                                   fg_color=border_color,
                                   border_width=0,
                                   **kwargs)
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.border.grid(row=0,column=0,padx=outside_border_width, pady=outside_border_width, sticky="nsew")

        # try to get the parent color
        if fg_color is None:
            fg_color = parent.cget("fg_color")

        for row, cells in enumerate(table_values):
            for col, value in enumerate(cells):
                try:
                    width = column_widths[col]
                except:
                    width = None
                if row==0:
                    cell = ctk.CTkLabel(self.border, text=str(value), font=ctk.CTkFont(weight="bold"), fg_color=fg_color)
                    # self.border.grid_columnconfigure(col, weight=1)
                    cell.grid(row=row, column=col, sticky="nsew",
                              padx=border_width, pady=(border_width, border_width+1),
                              ipadx=5, ipady=2)
                else:
                    cell = ctk.CTkLabel(self.border, text=str(value), fg_color=fg_color)
                    cell.grid(row=row, column=col, sticky="nsew",
                              padx=border_width, pady=border_width,
                              ipadx=5, ipady=2)

# Generalized optionmenu. Calls the provided callback
class NameIDOptionMenu(ctk.CTkOptionMenu):
    def __init__(self, parent,
                 nameIDs: List[tuple[str,int]],
                 selection: tuple[str,int] = ("",-1),
                 callback: Callable[[int],None]=None,
                 **kwargs):

        self.nameIDs = nameIDs
        self.callback = callback
        self.selection = selection

        # IDs are guaranteed to be unique, but names aren't. So append a unique integer for name duplicates
        self.nameIDsMap: Dict[str,int] = {}
        for nameID in nameIDs:
            appendInt = 0
            while (True):
                nameStr = nameID[0] + (str(appendInt) if appendInt else "")
                if nameStr in self.nameIDsMap:
                    appendInt = appendInt + 1
                    continue
                else:
                    break
            self.nameIDsMap[nameStr] = nameID[1]

            # set the selection to updated str/id pair
            if selection[1] == nameID[1]:
                self.selection = (nameStr, selection[1])

        # TODO check this is the correct way to use args/kwargs
        super().__init__(parent, values=list(self.nameIDsMap.keys()), command=self.menuCallback, **kwargs)
        self.set(self.selection[0])

    def menuCallback(self, name: str):
        if self.callback:
            self.callback(self.nameIDsMap[name])

    def get(self) -> tuple[str,int]:
        name = super().get()
        id = self.nameIDsMap.get(name)

        return (name,id)


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

class SectionLabel(ctk.CTkLabel):
    def __init__(self, parent, text: str = ""):
        super().__init__(parent, text=text, font=ctk.CTkFont(size=15, weight="bold"))

# Rider Profiles main content frame
class RiderProfileFrame(ctk.CTkFrame):
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
        self.firstNameEnt = ctk.CTkEntry(self.nameFrm)
        self.firstNameEnt.insert(0,self.firstName)
        self.firstNameEnt.grid(row=1, column=1, padx=(5,25), pady=(10,10))
        self.lastNameLbl = ctk.CTkLabel(self.nameFrm, text="Last Name:")
        self.lastNameLbl.grid(row=1, column=2, padx=(25,5), pady=(10,10))
        self.lastNameEnt = ctk.CTkEntry(self.nameFrm)
        self.lastNameEnt.insert(0, self.lastName)
        self.lastNameEnt.grid(row=1, column=3, padx=(5,25), pady=(10,10))

        # Physical stats section
        self.statsFrm = ctk.CTkFrame(self)
        self.statsFrm.grid(row=1, column=0, padx=(10,10), pady=(10,10), sticky="NSEW")
        self.statsLbl = SectionLabel(self.statsFrm, "Physical Characteristics")
        self.statsLbl.grid(row=0, column=0, columnspan=2, padx=(10,0), sticky="NW")
        self.weightLbl = ctk.CTkLabel(self.statsFrm, text="Weight (kg):")
        self.weightLbl.grid(row=1, column=0, padx=(15,5), pady=(10,10))
        self.weightEnt = ctk.CTkEntry(self.statsFrm)
        self.weightEnt.insert(0, self.weight)
        self.weightEnt.grid(row=1, column=1, padx=(5,25), pady=(10,10))
        self.CdALbl = ctk.CTkLabel(self.statsFrm, text=f"CdA (m\N{SUPERSCRIPT TWO}):")
        self.CdALbl.grid(row=1, column=2, padx=(25,5), pady=(10,10))
        self.CdAEnt = ctk.CTkEntry(self.statsFrm)
        self.CdAEnt.insert(0, self.CdA)
        self.CdAEnt.grid(row=1, column=3, padx=(5,25), pady=(10,10))

        # FTP and wPrime section
        self.powerFrm = ctk.CTkFrame(self)
        self.powerFrm.grid(row=2, column=0, padx=(10,10), pady=(10,10), sticky="NSEW")
        self.powerLbl = SectionLabel(self.powerFrm, "Physiological Characteristics")
        self.powerLbl.grid(row=0, column=0, columnspan=2, padx=(10,0), sticky="NW")
        self.FTPLbl = ctk.CTkLabel(self.powerFrm, text="FTP (Watts):")
        self.FTPLbl.grid(row=1, column=0, padx=(15,5), pady=(10,10))
        self.FTPEnt = ctk.CTkEntry(self.powerFrm)
        self.FTPEnt.insert(0, self.FTP)
        self.FTPEnt.grid(row=1, column=1, padx=(5,25), pady=(10,10))
        self.wPrimeLbl = ctk.CTkLabel(self.powerFrm, text="wPrime (kJ):")
        self.wPrimeLbl.grid(row=1, column=2, padx=(25,5), pady=(10,10))
        self.wPrimeEnt = ctk.CTkEntry(self.powerFrm)
        self.wPrimeEnt.insert(0, self.wPrime)
        self.wPrimeEnt.grid(row=1, column=3, padx=(5,25), pady=(10,10))

        # Save Rider button
        self.saveBtn = ctk.CTkButton(self, text="Save", fg_color="green", hover_color="dark green",
                                     command=self.saveRiderBtnPress)
        self.saveBtn.grid(row=3, column=0, padx=(10,10), pady=(10,10))

        # success/warning alert label
        self.alertLbl = ctk.CTkLabel(self, text="")
        self.alertLbl.grid(row=4, column=0, padx=(10,10), pady=(5,10))

    # exactly the same as wottmodel.Rider.setProperty
    def setAttribute(self, attributeDict: Dict[str, object]):
        for attribute, value in attributeDict.items():
            match attribute:
                # TODO change all of these to
                case RiderAttributes.RIDERID:
                    self.riderID = int(value)
                case RiderAttributes.FIRSTNAME:
                    self.firstName = str(value)
                case RiderAttributes.LASTNAME:
                    self.lastName = str(value)
                case RiderAttributes.WEIGHT:
                    self.weight = str(value)
                case RiderAttributes.FTP:
                    self.FTP = str(value)
                case RiderAttributes.WPRIME:
                    self.wPrime = str(value)
                case RiderAttributes.CDA:
                    self.CdA = str(value)
                case RiderAttributes.POWERRESULTS:
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
            attributeDict = {RiderAttributes.FIRSTNAME: self.firstName,
                             RiderAttributes.LASTNAME: self.lastName,
                             RiderAttributes.WEIGHT: self.weight,
                             RiderAttributes.FTP: self.FTP,
                             RiderAttributes.WPRIME: self.wPrime,
                             RiderAttributes.CDA: self.CdA,
                             RiderAttributes.POWERRESULTS: self.powerResults}

            self.controller.saveRiderBtnPress(self.riderID, **attributeDict)

    """ ------ alert label methods ------ """
    def hideAlert(self):
        self.alertLbl.configure(text = "")

    def showAlertError(self, message: str = "Error", ms: int = 3000):
        self.alertLbl.configure(text = message, text_color = 'red')
        self.alertLbl.after(ms, self.hideAlert)

    def showAlertSuccess(self, message: str = "Success", ms: int = 3000):
        self.alertLbl.configure(text = message, text_color = 'green')
        self.alertLbl.after(ms, self.hideAlert)

# Environment Profiles main content frame
class EnvironmentProfileFrame(ctk.CTkFrame):
    def __init__(self, parent, controller = None,
                 envirID: int = -1,
                 envirName: str = "",
                 airDensity: str = "",
                 Crr: str = "",
                 mechLosses: str = "",
                 attributeDict: Dict[str, object] = {}):
        super().__init__(parent)

        self.controller = controller

        self.grid_columnconfigure(0, weight=1)

        self.envirID = envirID
        self.envirName = envirName
        self.airDensity = airDensity
        self.Crr = Crr
        self.mechLosses = mechLosses

        if attributeDict:
            self.setAttribute(attributeDict)

        """ ------ set up the geometry ------ """
        # Name section
        self.nameFrm = ctk.CTkFrame(self)
        self.nameFrm.columnconfigure(4, weight=1)
        self.nameFrm.grid(row=0, column=0, padx=(10,10), pady=(10,10), sticky="NSEW")
        self.nameLbl = SectionLabel(self.nameFrm, "Environment Name")
        self.nameLbl.grid(row=0, column=0, columnspan=2, padx=(10,0), sticky="NW")
        self.envirNameEnt = ctk.CTkEntry(self.nameFrm, width=300)
        self.envirNameEnt.insert(0,self.envirName)
        self.envirNameEnt.grid(row=1, column=1, padx=(10,25), pady=(10,10))

        # Atmospheric conditions section
        self.atmosFrm = ctk.CTkFrame(self)
        self.atmosFrm.grid(row=1, column=0, padx=(10,10), pady=(10,10), sticky="NSEW")
        self.atmosLbl = SectionLabel(self.atmosFrm, "Atmospheric Conditions")
        self.atmosLbl.grid(row=0, column=0, columnspan=2, padx=(10,0), sticky="NW")
        self.airDensityLbl = ctk.CTkLabel(self.atmosFrm, text=f"Air Density (kg/m\N{SUPERSCRIPT THREE}):")
        self.airDensityLbl.grid(row=1, column=0, padx=(15,5), pady=(10,10))
        self.airDensityEnt = ctk.CTkEntry(self.atmosFrm)
        self.airDensityEnt.insert(0, self.airDensity)
        self.airDensityEnt.grid(row=1, column=1, padx=(5,25), pady=(10,10))

        # Equipment section
        self.equipmentFrm = ctk.CTkFrame(self)
        self.equipmentFrm.grid(row=2, column=0, padx=(10,10), pady=(10,10), sticky="NSEW")
        self.EquipmentLbl = SectionLabel(self.equipmentFrm, "Equipment Characteristics")
        self.EquipmentLbl.grid(row=0, column=0, columnspan=2, padx=(10,0), sticky="NW")
        self.CrrLbl = ctk.CTkLabel(self.equipmentFrm, text="Crr:")
        self.CrrLbl.grid(row=1, column=0, padx=(15,5), pady=(10,10))
        self.CrrEnt = ctk.CTkEntry(self.equipmentFrm)
        self.CrrEnt.insert(0, self.Crr)
        self.CrrEnt.grid(row=1, column=1, padx=(5,25), pady=(10,10))
        self.mechLossesLbl = ctk.CTkLabel(self.equipmentFrm, text="Mechanical Losses:")
        self.mechLossesLbl.grid(row=1, column=2, padx=(25,5), pady=(10,10))
        self.mechLossesEnt = ctk.CTkEntry(self.equipmentFrm)
        self.mechLossesEnt.insert(0, self.mechLosses)
        self.mechLossesEnt.grid(row=1, column=3, padx=(5,25), pady=(10,10))

        # Save Environment button
        self.saveBtn = ctk.CTkButton(self, text="Save", fg_color="green", hover_color="dark green",
                                     command=self.saveEnvirBtnPress)
        self.saveBtn.grid(row=3, column=0, padx=(10,10), pady=(10,10))

        # success/warning alert label
        self.alertLbl = ctk.CTkLabel(self, text="")
        self.alertLbl.grid(row=4, column=0, padx=(10,10), pady=(5,10))

    # exactly the same as wottmodel.Environment.setProperty
    def setAttribute(self, attributeDict: Dict[str, object]):
        for attribute, value in attributeDict.items():
            match attribute:
                # TODO change all of these to
                case EnvirAttributes.ENVIRID:
                    self.envirID = int(value)
                case EnvirAttributes.ENVIRNAME:
                    self.envirName = str(value)
                case EnvirAttributes.AIRDENSITY:
                    self.airDensity = str(value)
                case EnvirAttributes.CRR:
                    self.Crr = str(value)
                case EnvirAttributes.MECHLOSSES:
                    self.mechLosses = str(value)
                case _:
                    pass

    def saveEnvirBtnPress(self):
        # update the internal variables
        self.envirName = self.envirNameEnt.get()
        self.airDensity = self.airDensityEnt.get()
        self.Crr = self.CrrEnt.get()
        self.mechLosses = self.mechLossesEnt.get()

        # send to controller
        if self.controller:
            attributeDict = {EnvirAttributes.ENVIRNAME: self.envirName,
                             EnvirAttributes.AIRDENSITY: self.airDensity,
                             EnvirAttributes.CRR: self.Crr,
                             EnvirAttributes.MECHLOSSES: self.mechLosses}

            self.controller.saveEnvirBtnPress(self.envirID, **attributeDict)

    """ ------ alert label methods ------ """
    def hideAlert(self):
        self.alertLbl.configure(text = "")

    def showAlertError(self, message: str = "Error", ms: int = 3000):
        self.alertLbl.configure(text = message, text_color = 'red')
        self.alertLbl.after(ms, self.hideAlert)

    def showAlertSuccess(self, message: str = "Success", ms: int = 3000):
        self.alertLbl.configure(text = message, text_color = 'green')
        self.alertLbl.after(ms, self.hideAlert)

# Simulation Profiles main content frame
class SimulationProfileFrame(ctk.CTkFrame):
    def __init__(self, parent, controller = None,
                 simID: int = -1,
                 simName: str = "",
                 rider: tuple[str,int] = ("",-1),
                 riderList: List[tuple[str,int]] = [],
                 envir: tuple[str,int] = ("",-1),
                 envirList: List[tuple[str,int]] = [],
                 attributeDict: Dict[str, object] = {}):
        super().__init__(parent)

        self.controller = controller

        self.grid_columnconfigure(0, weight=1)

        self.simID = simID
        self.simName = simName
        self.rider = rider
        self.riderList = riderList
        self.envir = envir
        self.envirList = envirList

        if attributeDict:
            self.setAttribute(attributeDict)

        """ ------ set up the geometry ------ """
        # Name section
        self.nameFrm = ctk.CTkFrame(self)
        self.nameFrm.columnconfigure(4, weight=1)
        self.nameFrm.grid(row=0, column=0, padx=(10,10), pady=(10,10), sticky="NSEW")
        self.nameLbl = SectionLabel(self.nameFrm, "Simulation Name")
        self.nameLbl.grid(row=0, column=0, columnspan=2, padx=(10,0), sticky="NW")
        self.simNameEnt = ctk.CTkEntry(self.nameFrm, width=300)
        self.simNameEnt.insert(0,self.simName)
        self.simNameEnt.grid(row=1, column=1, padx=(10,25), pady=(10,10))

        # Rider and Environment section
        self.selectFrm = ctk.CTkFrame(self)
        self.selectFrm.columnconfigure(4, weight=1)
        self.selectFrm.grid(row=1, column=0, padx=(10,10), pady=(10,10), sticky="NSEW")
        self.titleLbl = SectionLabel(self.selectFrm, "Rider and Environment")
        self.titleLbl.grid(row=0, column=0, columnspan=2, padx=(10,0), sticky="NW")
        self.riderLbl = ctk.CTkLabel(self.selectFrm, text="Rider:")
        self.riderLbl.grid(row=1, column=0, padx=(15,5), pady=(10,10))
        self.riderOpt = NameIDOptionMenu(self.selectFrm, self.riderList, self.rider)
        self.riderOpt.grid(row=1, column=1, padx=(5,25), pady=(10,10))
        self.envirLbl = ctk.CTkLabel(self.selectFrm, text="Envir:")
        self.envirLbl.grid(row=1, column=2, padx=(25,5), pady=(10,10))
        self.envirOpt = NameIDOptionMenu(self.selectFrm, self.envirList, self.envir)
        self.envirOpt.grid(row=1, column=3, padx=(5,25), pady=(10,10))

        # Save and Run Simulation buttons section
        self.buttonFrm = ctk.CTkFrame(self, fg_color="transparent")
        self.buttonFrm.columnconfigure((0,3), weight=1)
        self.buttonFrm.grid(row=2, column=0, padx=(10,10), pady=(10,10), sticky="NSEW")
        self.saveBtn = ctk.CTkButton(self.buttonFrm, text="Save", fg_color="green", hover_color="dark green",
                                     command=self.saveSimBtnPress)
        self.saveBtn.grid(row=0, column=1, padx=(10,10), pady=(10,10))
        self.runBtn = ctk.CTkButton(self.buttonFrm, text = "Run", fg_color="green", hover_color="dark green",
                                    command=self.runSimBtnPress)
        self.runBtn.grid(row=0, column=2, padx=(10,10), pady=(10,10))

        # success/warning alert label
        self.alertLbl = ctk.CTkLabel(self, text="")
        self.alertLbl.grid(row=3, column=0, padx=(10,10), pady=(5,10))

    # exactly the same as wottmodel.Environment.setProperty
    def setAttribute(self, attributeDict: Dict[str, object]):
        for attribute, value in attributeDict.items():
            match attribute:
                # TODO change all of these to
                case SimAttributes.SIMID:
                    self.simID = int(value)
                case SimAttributes.SIMNAME:
                    self.simName = str(value)
                case SimAttributes.RIDER:
                    self.rider = value
                case SimAttributes.ENVIR:
                    self.envir = value
                case SimAttributes.RIDERLIST:
                    self.riderList = value
                case SimAttributes.ENVIRLIST:
                    self.envirList = value
                case _:
                    pass

    def saveSimBtnPress(self):
        # update the internal variables
        self.simName = self.simNameEnt.get()
        self.rider = self.riderOpt.get()
        self.envir = self.envirOpt.get()

        # send to controller
        if self.controller:
            attributeDict = {SimAttributes.SIMNAME: self.simName,
                             SimAttributes.RIDER: self.rider,
                             SimAttributes.ENVIR: self.envir}

            self.controller.saveSimBtnPress(self.simID, **attributeDict)

    def runSimBtnPress(self):
        # send to controller
        if self.controller:
            # TODO uncomment this when the controller implements this method
            #self.controller.runSimBtnPress(self.simID)
            pass

    """ ------ alert label methods ------ """
    def hideAlert(self):
        self.alertLbl.configure(text = "")

    def showAlertError(self, message: str = "Error", ms: int = 3000):
        self.alertLbl.configure(text = message, text_color = 'red')
        self.alertLbl.after(ms, self.hideAlert)

    def showAlertSuccess(self, message: str = "Success", ms: int = 3000):
        self.alertLbl.configure(text = message, text_color = 'green')
        self.alertLbl.after(ms, self.hideAlert)

class SimulationWindow(ctk.CTkToplevel):
    def __init__(self, root,
                 simName = "Simulation Name",
                 time = [],
                 power = [],
                 velocity = [],
                 splits = [],
                 splittable = []):
        super().__init__(root)

        # set up grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # name at top
        nameLbl = ctk.CTkLabel(self, text=simName, font=ctk.CTkFont(size=20, weight="bold"))
        nameLbl.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10))

        # plot frame protects the plots from weird scaling
        plot_frm = ctk.CTkFrame(self)
        plot_frm.grid_columnconfigure(0,weight=1, minsize=300)
        plot_frm.grid_rowconfigure((0,1),weight=1, minsize=200)
        plot_frm.grid(row=1, column=0, sticky="nsew")

        # velocity and power vs time figure/axes
        self.velocity_fig = plt.figure()
        power_ax = self.velocity_fig.gca()
        velocity_ax = power_ax.twinx()
        velocity_power_widget = FigureCanvasTkAgg(self.velocity_fig, master=plot_frm).get_tk_widget()

        # get plot color list
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

        # velocity plot
        color = colors[0]
        velocity_ln = velocity_ax.plot(time, velocity, color=color, label='Velocity')
        velocity_ax.tick_params(axis='y', labelcolor=color)
        velocity_ax.set_ylabel("kph", color=color)
        velocity_ax.set_ylim(bottom=0)
        velocity_ax.grid(True, axis='y', color=color)

        # power plot
        color = colors[1]
        power_ln = power_ax.plot(time, power, color=color, label="Power")
        power_ax.tick_params(axis='y', labelcolor=color)
        power_ax.set_ylabel("Wotts", color=color)
        power_ax.set_ylim(bottom=0)
        power_ax.grid(True, axis='y', color=color)

        # title and x shared between axes
        velocity_ax.set_title("Velocity & Power")
        velocity_ax.set_xlabel("time (s)")
        velocity_ax.set_xlim(left=-1,right=time[-1]+1)
        velocity_ax.grid(True, axis='x')
        lines = velocity_ln + power_ln
        labels = [l.get_label() for l in lines]
        velocity_ax.legend(lines, labels, framealpha=1)

        velocity_power_widget.grid(row=0,column=0, sticky="nsew")

        # lap split graph
        self.split_fig = plt.figure()
        split_ax = self.split_fig.gca()
        lap_split_widget = FigureCanvasTkAgg(self.split_fig, master=plot_frm).get_tk_widget()
        color = colors[2]
        split_ax.plot(splits, color=color, marker='.')
        split_ax.tick_params(axis='y', color=color)
        split_ax.grid(True)
        split_ax.set_title("Lap Times")
        split_ax.set_xlabel("Lap")
        split_ax.set_ylabel("time (seconds)", color=color)
        lap_split_widget.grid(row=1, column=0, sticky="nsew")

        # table of half-lap splits
        splits_frm = ctk.CTkScrollableFrame(self, width=1000, corner_radius=0)
        splits_frm.grid_columnconfigure(0,weight=1)
        splits_frm.grid_rowconfigure(0,weight=1)
        splits_tbl = CustomTable(splits_frm, table_values=splittable, outside_border_width=2)
        splits_frm.grid(row=1,column=1, sticky="nsew")
        extra_x_pad = 5
        splits_tbl.grid(row=0,column=0, padx=extra_x_pad)

        # size scrollframe to table width
        self.update_idletasks()
        splits_frm.configure(width=splits_tbl.winfo_width()+2*extra_x_pad)

        # patch for matplotlib-tkinter bug
        self.protocol("WM_DELETE_WINDOW", self.plt_destroy)

    # fix maplotlib-tkinter bug by manually closing figures before destroying window
    def plt_destroy(self):
        plt.close(self.velocity_fig)
        plt.close(self.split_fig)
        self.destroy()

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

    def showRiderDetail(self, riderID: int, attributeDict: Dict[str,object]):
        self.mainContent_frm = RiderProfileFrame(self, self.controller, riderID, attributeDict=attributeDict)
        self.mainContent_frm.grid(row=0, column=2, padx=0, pady=0, sticky="nsew")

    def showEnvirDetail(self, envirID: int, attributeDict: Dict[str,object]):
        self.mainContent_frm = EnvironmentProfileFrame(self, self.controller, envirID, attributeDict=attributeDict)
        self.mainContent_frm.grid(row=0, column=2, padx=0, pady=0, sticky="nsew")

    def showSimDetail(self, simID: int, attributeDict: Dict[str,object]):
        self.mainContent_frm = SimulationProfileFrame(self, self.controller, simID, attributeDict=attributeDict)
        self.mainContent_frm.grid(row=0, column=2, padx=0, pady=0, sticky="nsew")

    def showDetailSaveError(self, message: str):
        self.mainContent_frm.showAlertError(message)

    def showDetailSaveSuccess(self, message: str):
        self.mainContent_frm.showAlertSuccess(message)

    def showSimWindow(self, simID, **kwargs):
        # destroy the window if it already exists
        if self.simWindows[simID]:
            window: SimulationWindow = self.simWindows[simID]
            window.plt_destroy()

        # create and save the window
        window = SimulationWindow(self)
        self.simWindows[simID] = window
