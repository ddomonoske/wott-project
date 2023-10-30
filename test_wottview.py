from wottview import *
import tkinter as tk
import customtkinter as ctk
from typing import Dict
from test_helpers import *


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
             test_RiderProfileFrame,
             test_RiderProfileFrame_Alert]

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
