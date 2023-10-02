import tkinter as tk
import customtkinter as ctk

class View(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # set up grid scaling
        self.columnconfigure((0,1), weight=0)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0,weight=1)

        # top selection frame
        self.topSelect_frm = ctk.CTkFrame(self, width=140, corner_radius=0)
        
        # logo
        self.logo_lbl = ctk.CTkLabel(self.topSelect_frm, text="WOTTProject", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_lbl.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # top selection buttons
        self.riders_btn = ctk.CTkButton(master=self.topSelect_frm, text="Rider Profiles")
        self.riders_btn.grid(row=1, column=0, pady=5)
        self.envir_btn = ctk.CTkButton(master=self.topSelect_frm, text="Environments")
        self.envir_btn.grid(row=2, column=0, pady=5)
        self.sims_btn = ctk.CTkButton(master=self.topSelect_frm, text="Simulations")
        self.sims_btn.grid(row=3, column=0, pady=5)
        
        self.topSelect_frm.grid(row=0, column=0, padx=0, pady=0, sticky="news")

        # sub selection frame

        # main content frame

        # rider frame
        self.rider_frm = RiderProfilesFrame(self)

        # create environment frame
        self.envir_frm = EnvironmentProfilesFrame(self)

        # create simulations frame
        self.sim_frm = SimulationProfilesFrame(self)


# Rider Profiles main content frame
class RiderProfilesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

# Environment Profiles main content frame
class EnvironmentProfilesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

# Simulation Profiles main content frame
class SimulationProfilesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

# for testing
if __name__ == '__main__':
    app = ctk.CTk()
    app.title("WOTT Main View Demo")
    app.state("zoomed")
    
    app.columnconfigure(0,weight=1)
    app.rowconfigure(0,weight=1)

    view = View(app)
    view.grid(row=0, column=0, sticky="news")
    app.mainloop()