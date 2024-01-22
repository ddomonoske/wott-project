import customtkinter as ctk
from wottview import *
from wottmodel import *
from wottattributes import *
from functools import partial

fruitStr = [("apple", 1),
            ("banana", 2),
            ("cherry", 5),
            ("dragon fruit", 4),
            ("elderberry", 3),
            ("fig", 90),
            ("grapes", 12),
            ("apple", 7)]

riderStr = [("David", 0),
            ("Anders", 2),
            ("Grant", 4),
            ("Brendan", 6),
            ("Colby", 8),
            ("Viggo", 10),
            ("Eddy", 12),
            ("", 13)]

envirStr = [("LA", 10),
            ("COS", 9),
            ("San Juan", 8),
            ("Paris", 7)]

simStr = [("10/8/23 COS Testing", 2),
          ("8/8/23 Worlds", 4)]

testRiderAttributes = {
    RiderAttributes.FIRSTNAME: "David",
    RiderAttributes.LASTNAME: "Domonoske",
    RiderAttributes.CDA: 0.195,
    RiderAttributes.FTP: 418,
    RiderAttributes.WEIGHT: 89,
    RiderAttributes.WPRIME: 28
}

testEnvirAttributes = {
    EnvirAttributes.ENVIRNAME: "COS",
    EnvirAttributes.AIRDENSITY: 0.995,
    EnvirAttributes.CRR: 0.002,
    EnvirAttributes.MECHLOSSES: .01
}

testSimAttributes = {
    SimAttributes.SIMNAME: "David in COS",
    SimAttributes.POWERPLAN: PowerPlan([(0,500,1),
                                        (1,988,14),
                                        (15,550,20),
                                        (35,458,100),
                                        (135,523,120)])
}

tpSplitsTable = [["Distance", "Lap Split", "Total Time"],
                [125,12.50,12.50],
                [250,8.50,21.00],
                [375,7.40,28.40],
                [500,7.20,35.60],
                [625,7.10,42.70],
                [750,7.20,49.90],
                [875,7.40,57.30],
                [1000,7.26,64.56],
                [1125,7.28,71.84],
                [1250,7.33,79.17],
                [1375,7.26,86.43],
                [1500,7.48,93.90],
                [1625,6.92,100.83],
                [1750,7.11,107.93],
                [1875,6.98,114.92],
                [2000,7.01,121.93],
                [2125,7.37,129.30],
                [2250,7.23,136.53],
                [2375,7.27,143.80],
                [2500,7.26,151.06],
                [2625,6.93,157.99],
                [2750,7.36,165.35],
                [2875,6.98,172.33],
                [3000,7.43,179.77],
                [3125,7.44,187.20],
                [3250,7.47,194.68],
                [3375,7.15,201.83],
                [3500,7.00,208.82],
                [3625,6.97,215.79],
                [3750,6.96,222.75],
                [3875,7.47,230.22],
                [4000,6.96,237.19]]

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

    def saveRiderBtnPress(self, riderID=-1, **kwargs):
        print(f"rider {riderID} updated:" + str(kwargs))

    def saveEnvirBtnPress(self, envirID=-1, **kwargs):
        print(f"environment {envirID} updated:" + str(kwargs))

    def saveSimBtnPress(self, simID=-1, **kwargs):
        print(f"simulation {simID} updated:" + str(kwargs))

def printSuccess(text: str = "success"):
    print(f"{bcolors.OKGREEN}{text}{bcolors.ENDC}")

def printFailure(text: str = "failure"):
    print(f"{bcolors.FAIL}{text}{bcolors.ENDC}")

def repeatSuccessAlert(detail_frame: RiderProfileFrame|EnvironmentProfileFrame):
    detail_frame.showAlertSuccess("Success Alert Message", 1000)
    detail_frame.after(2000, partial(repeatErrorAlert, detail_frame))

def repeatErrorAlert(detail_frame: RiderProfileFrame|EnvironmentProfileFrame):
    detail_frame.showAlertError("Error Alert Message", 1000)
    detail_frame.after(2000, partial(repeatSuccessAlert, detail_frame))