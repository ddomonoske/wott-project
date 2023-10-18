import customtkinter as ctk
from wottmodel import *
from wottview import *
from wottcontroller import *

# run all tests
if __name__ == '__main__':
    ctk.set_default_color_theme("blue")
    app = ctk.CTk()
    app.wm_state("zoomed")
    app.grid_columnconfigure(0,weight=1)
    app.grid_rowconfigure(0,weight=1)

    testDirectory = Path.cwd() / "wott_testcontroller_main"
    model = Model(str(testDirectory))
    view = View(app)
    controller = Controller(model, view)

    view.setController(controller)

    view.grid(row=0, column=0, sticky="NSEW")

    app.mainloop()
    
     # delete file and directory
    testDirectory.rmdir()

