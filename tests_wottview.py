from wottview import *
import tkinter as tk
import customtkinter as ctk

class BasicController():
    def __init__(self) -> None:
        pass

    def subSelectBtnPress(self, name: str):
        print(f"{name} button pressed")

# test SubSelectFrame with individual callbacks
def test_SubSelectFrame(parent: ctk.CTkToplevel):
    parent.title("SubSelectFrame Test")
    parent.columnconfigure(0,weight=1)
    parent.rowconfigure(0,weight=1)

    controller = BasicController()

    names = ["apple",
             "banana",
             "cherry",
             "dragon fruit",
             "elderberry",
             "fig",
             "grapes"]

    ss_frame = SubSelectFrame(parent, names, controller)
    ss_frame.grid(row=0, column=0, sticky="news")

# test the entire View
def test_View(parent: ctk.CTkToplevel):
    parent.title("View Test")
    parent.wm_state("zoomed")  # this only works on the main window (ctk.CTk), not toplevel windows (ctk.CTkTopLevel)
    parent.columnconfigure(0,weight=1)
    parent.rowconfigure(0,weight=1)

    view = View(parent)
    view.grid(row=0, column=0, sticky="news")

test_list = [test_SubSelectFrame]

# run all tests
if __name__ == '__main__':
    ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # ["blue", "green", "dark-blue", "sweetkind"]

    # run the main View fullscreen
    root = ctk.CTk()
    test_View(root)

    # run every other test in its own window
    for test in test_list:
        top = ctk.CTkToplevel(root)
        test(top)

    root.mainloop()
