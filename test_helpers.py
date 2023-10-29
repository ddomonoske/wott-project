import customtkinter as ctk
from typing import Dict
from wottview import *
from functools import partial

fruitStr = [("apple", 1),
            ("banana", 2),
            ("cherry", 5),
            ("dragon fruit", 4),
            ("elderberry", 3),
            ("fig", 90),
            ("grapes", 12)]

riderStr = [("David", 0),
            ("Anders", 2),
            ("Grant", 4),
            ("Brendan", 6),
            ("Colby", 8),
            ("Viggo", 10),
            ("Eddy", 12),
            (" ", 13)]

envirStr = [("LA", 10),
            ("COS", 9),
            ("San Juan", 8),
            ("Paris", 7)]

simStr = [("10/8/23 COS Testing", 2),
          ("8/8/23 Worlds", 4)]

# colors from blender
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    EMPH = BOLD+UNDERLINE

class BasicController():
    def __init__(self, view: ctk.CTkFrame = None) -> None:
        self.view = view

    def addRiderBtnPress(self):
        print("add rider button pressed")

    def addEnvirBtnPress(self):
        print("add environment button pressed")

    def addSimBtnPress(self):
        print("add simulation button pressed")

    def riderSelectBtnPress(self, id: int):
        print(f"rider {id} button pressed")

    def envirSelectBtnPress(self, id: int):
        print(f"environment {id} button pressed")

    def simSelectBtnPress(self, id: int):
        print(f"simulation {id} button pressed")

    def riderBtnPress(self):
        if self.view:
            self.view.showRiderSelectionList(riderStr)

    def envirBtnPress(self):
        if self.view:
            self.view.showEnvirSelectionList(envirStr)

    def simBtnPress(self):
        if self.view:
            self.view.showSimSelectionList(simStr)

    def saveRiderBtnPress(self, riderID=-1, attributeDict: Dict[str, str] = {}):
        print(f"rider {riderID} updated:" + str(attributeDict))

def printSuccess(text: str = "success"):
    print(f"{bcolors.OKGREEN}{text}{bcolors.ENDC}")

def printFailure(text: str = "failure"):
    print(f"{bcolors.FAIL}{text}{bcolors.ENDC}")

def repeatSuccessAlert(rp_frame: RiderProfileFrame):
    rp_frame.showAlertSuccess("Success Alert Message", 1000)
    rp_frame.after(2000, partial(repeatErrorAlert, rp_frame))

def repeatErrorAlert(rp_frame: RiderProfileFrame):
    rp_frame.showAlertError("Error Alert Message", 1000)
    rp_frame.after(2000, partial(repeatSuccessAlert, rp_frame))