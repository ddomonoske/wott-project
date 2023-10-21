from wottview import *
import tkinter as tk
import customtkinter as ctk
from typing import Dict

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
            ("Eddy", 12)]

envirStr = [("LA", 10),
            ("COS", 9),
            ("San Juan", 8),
            ("Paris", 7)]

simStr = [("10/8/23 COS Testing", 2),
          ("8/8/23 Worlds", 4)]

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

    def saveRiderBtnPress(self, attributeDict: Dict[str, str] = {}):
        print(attributeDict)

# test RiderSelectFrame with individual callbacks
def test_RiderSelectFrame(parent: ctk.CTkToplevel):
    parent.title("RiderSelectFrame Test")
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    controller = BasicController()

    ss_frame = RiderSelectFrame(parent, fruitStr, controller)
    ss_frame.grid(row=0, column=0, sticky="news")

# test the Rider Frame
def test_RiderProfileFrame(parent: ctk.CTkToplevel):
    parent.title("Rider Frame Test")
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    controller = BasicController()

    rp_frame = RiderProfileFrame(parent, controller)
    rp_frame.grid(row=0, column=0, sticky="NSEW")

# test the entire View
def test_View(parent: ctk.CTkToplevel):
    parent.title("View Test")
    parent.wm_state("zoomed")  # this only works on the main window (ctk.CTk), not toplevel windows (ctk.CTkTopLevel)
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    view = View(parent)
    view.grid(row=0, column=0, sticky="news")

    controller = BasicController(view)
    view.setController(controller)


test_list = [test_RiderSelectFrame,
             test_RiderProfileFrame]

# run all tests
if __name__ == '__main__':
    ctk.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # ["blue", "green", "dark-blue", "sweetkind"]

    # run the main View fullscreen
    root = ctk.CTk()
    test_View(root)

    # run every other test in its own window
    for test in test_list:
        top = ctk.CTkToplevel(root)
        test(top)

    root.mainloop()
