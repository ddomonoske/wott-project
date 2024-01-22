from wottview import *
import tkinter as tk
import customtkinter as ctk
from typing import Dict
from test_helpers import *
from wottattributes import *

import numpy as np


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
    ss_frame.grid(row=0, column=0, sticky="nsew")

# test the Rider Frame
def test_RiderProfileFrame(parent: ctk.CTkToplevel):
    parent.title("Rider Frame Test")
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    controller = BasicController()

    rp_frame = RiderProfileFrame(parent, controller, riderID=3)
    rp_frame.grid(row=0, column=0, sticky="nsew")

def test_RiderProfileFrame_Alert(parent: ctk.CTkToplevel):
    parent.title("Rider Frame Alert Test")
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    controller = BasicController()

    rp_frame = RiderProfileFrame(parent, controller,riderID=2)
    rp_frame.grid(row=0, column=0, sticky="nsew")

    repeatSuccessAlert(rp_frame)

# test the Environment Frame
def test_EnvironmentProfileFrame(parent: ctk.CTkToplevel):
    parent.title("Environment Frame Test")
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    controller = BasicController()

    rp_frame = EnvironmentProfileFrame(parent, controller, envirID=3)
    rp_frame.grid(row=0, column=0, sticky="nsew")

def test_EnvironmentProfileFrame_Alert(parent: ctk.CTkToplevel):
    parent.title("Environment Frame Alert Test")
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    controller = BasicController()

    ep_frame = EnvironmentProfileFrame(parent, controller, envirID=3)
    ep_frame.grid(row=0, column=0, sticky="nsew")

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
    sp_frame.grid(row=0, column=0, sticky="nsew")

# test Simulation Window
def test_SimulationWindow(parent: ctk.CTkToplevel):
    n = 1000
    maxT = 240
    time = np.linspace(0,maxT,n,endpoint=False)
    attributes = {
        SimWindowAttributes.SIMNAME: "Test Simulation Name",
        SimWindowAttributes.TIME: time,
        SimWindowAttributes.POWER: 500*time*np.exp(-0.2*time)+450*(1-np.exp(-0.2*time))-0.2*time,
        SimWindowAttributes.VELOCITY: 60*(1-np.exp(-.1*time))-0.02*time,
        SimWindowAttributes.SPLITS: [22,20,15,14.5,14.5,14.5,14.5,14.5,14.4,14.6,14.8,15.1],
        SimWindowAttributes.SPLITTABLE: tpSplitsTable
        }

    # place under grandparent so we can delete parent
    SimulationWindow(parent.master, **attributes)

    # destroy parent because SimulationWindow opens it's own window
    parent.destroy()

# test the entire View
def test_View(parent: ctk.CTkToplevel):
    parent.title("View Test")
    parent.wm_state("zoomed")  # this only works on the main window (ctk.CTk), not toplevel windows (ctk.CTkTopLevel)
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    view = View(parent)
    view.grid(row=0, column=0, sticky="nsew")

    controller = BasicController(view)
    view.setController(controller)


test_list = [test_NameIDOptionMenu,
             test_CustomTable,
             test_RiderSelectFrame,
             test_RiderProfileFrame,
             test_RiderProfileFrame_Alert,
             test_EnvironmentProfileFrame,
             test_EnvironmentProfileFrame_Alert,
             test_SimulationProfileFrame,
             test_SimulationWindow]

# run all tests
def main():
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # ["blue", "green", "dark-blue", "sweetkind"]

    # run the main View fullscreen
    root = ctk.CTk()
    test_View(root)

    # patch for the plt tcl bug
    root.protocol("WM_DELETE_WINDOW", partial(test_wattview_plt_destroy, root))

    # run every other test in its own window
    for test in test_list:
        top = ctk.CTkToplevel(root)
        test(top)

    root.mainloop()

def test_wattview_plt_destroy(root):
    plt.close("all")
    root.quit()

if __name__ == '__main__':
    main()
