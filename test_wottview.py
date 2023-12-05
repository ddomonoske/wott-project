from wottview import *
import tkinter as tk
import customtkinter as ctk
from typing import Dict
from test_helpers import *


# test NameIDOptionMenu
def test_NameIDOptionMenu(parent: ctk.CTkToplevel):
    parent.title("NameIDOptionMenu Test")

    controller = BasicController()

    menu = NameIDOptionMenu(parent, fruitStr, fruitStr[2], callback=controller.riderSelectBtnPress) # just grab a random entry for the selection
    menu.grid(row=0, column=0, pady=(20,20), padx=(40,40))

# test CustomTable
def test_CustomTable(parent: ctk.CTkToplevel):
    parent.title("CustomTable Test")
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    table = CustomTable(parent, tpSplitsTable[0:10], border_width=1, outside_border_width=3)
    table.grid(row=0,column=0, sticky="", padx=5, pady=5)

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

def test_RiderProfileFrame_Alert(parent: ctk.CTkToplevel):
    parent.title("Rider Frame Alert Test")
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    controller = BasicController()

    rp_frame = RiderProfileFrame(parent, controller,riderID=2)
    rp_frame.grid(row=0, column=0, sticky="NSEW")

    repeatSuccessAlert(rp_frame)

# test the Environment Frame
def test_EnvironmentProfileFrame(parent: ctk.CTkToplevel):
    parent.title("Environment Frame Test")
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    controller = BasicController()

    rp_frame = EnvironmentProfileFrame(parent, controller, envirID=3)
    rp_frame.grid(row=0, column=0, sticky="NSEW")

def test_EnvironmentProfileFrame_Alert(parent: ctk.CTkToplevel):
    parent.title("Environment Frame Alert Test")
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    controller = BasicController()

    ep_frame = EnvironmentProfileFrame(parent, controller, envirID=3)
    ep_frame.grid(row=0, column=0, sticky="NSEW")

    repeatSuccessAlert(ep_frame)

def test_SimulationProfileFrame(parent: ctk.CTkToplevel):
    parent.title("Simulation Frame Test")
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    controller = BasicController()

    sp_frame = SimulationProfileFrame(parent, controller, simID=2,
                                      envirList=envirStr,
                                      riderList=riderStr,
                                      rider = riderStr[2],
                                      envir=envirStr[1])
    sp_frame.grid(row=0, column=0, sticky="NSEW")

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


test_list = [test_NameIDOptionMenu,
             test_CustomTable,
             test_RiderSelectFrame,
             test_RiderProfileFrame,
             test_RiderProfileFrame_Alert,
             test_EnvironmentProfileFrame,
             test_EnvironmentProfileFrame_Alert,
             test_SimulationProfileFrame]

# run all tests
def main():
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # ["blue", "green", "dark-blue", "sweetkind"]

    # run the main View fullscreen
    root = ctk.CTk()
    test_View(root)

    # run every other test in its own window
    for test in test_list:
        top = ctk.CTkToplevel(root)
        test(top)

    root.mainloop()

if __name__ == '__main__':
    main()
