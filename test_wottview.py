from wottview import *
import tkinter as tk
import customtkinter as ctk
from typing import Dict
from test_helpers import *



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

    rp_frame = RiderProfileFrame(parent, controller, riderID=3)
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
