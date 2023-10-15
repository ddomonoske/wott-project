from wottview import *
import tkinter as tk
import customtkinter as ctk

fruitStr = ["apple",
            "banana",
            "cherry",
            "dragon fruit",
            "elderberry",
            "fig",
            "grapes"]

riderStr = ["David",
            "Anders",
            "Grant",
            "Brendan",
            "Colby",
            "Viggo",
            "Eddy"]

envirStr = ["LA",
            "COS",
            "San Juan",
            "Paris"]

simStr = ["10/8/23 COS Testing",
          "8/8/23 Worlds"]

class BasicController():
    def __init__(self, view: ctk.CTkFrame = None) -> None:
        self.view = view

    def subSelectBtnPress(self, name: str):
        print(f"{name} button pressed")

    def riderBtnPress(self):
        if self.view:
            self.view.updateSubSelectionFrame(riderStr)

    def envirBtnPress(self):
        if self.view:
            self.view.updateSubSelectionFrame(envirStr)

    def simBtnPress(self):
        if self.view:
            self.view.updateSubSelectionFrame(simStr)

# test SubSelectFrame with individual callbacks
def test_SubSelectFrame(parent: ctk.CTkToplevel):
    parent.title("SubSelectFrame Test")
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    controller = BasicController()

    ss_frame = SubSelectFrame(parent, fruitStr, controller)
    ss_frame.grid(row=0, column=0, sticky="news")

# test the Rider Frame
def test_RiderProfileFrame(parent: ctk.CTkToplevel):
    parent.title("Rider Frame Test")
    parent.grid_columnconfigure(0,weight=1)
    parent.grid_rowconfigure(0,weight=1)

    controller = BasicController()

    rp_frame = RiderProfileFrame(parent)
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


test_list = [test_SubSelectFrame,
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
