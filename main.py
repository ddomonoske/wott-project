import customtkinter as ctk
from model.storage import Storage
from view.panels import View
from controller import Controller


def main():
    ctk.set_default_color_theme("blue")
    ctk.set_appearance_mode("system")

    app = ctk.CTk()
    app.wm_state("zoomed")
    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(0, weight=1)

    storage = Storage()
    view = View(app)
    controller = Controller(storage, view)
    view.set_controller(controller)

    view.grid(row=0, column=0, sticky="nsew")

    app.mainloop()

    storage.save()


if __name__ == '__main__':
    main()
