from wottmodel import *
from wottview import *
from wottcontroller import *
import customtkinter as ctk


def main():
    # global settings
    ctk.set_default_color_theme("blue")
    ctk.set_appearance_mode("system")

    # create app
    app = ctk.CTk()
    app.wm_state("zoomed")
    app.grid_columnconfigure(0,weight=1)
    app.grid_rowconfigure(0,weight=1)

    # instantiate and connect model, view, and controller
    model = Model()
    view = View(app)
    controller = Controller(model, view)
    view.setController(controller)

    # place view in app
    view.grid(row=0, column=0, sticky="nsew")

    # run GUI
    app.mainloop()

    # save model to files when app is closed
    model.saveModel()

if __name__ == '__main__':
    main()
