from wottmodel import *
from wottview import *

class Controller(object):
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
        # TODO have some sort of state machine that remembers which page we're looking at

    """ ------ Top Level Btn Callbacks ------ """
    def riderBtnPress(self):
        riderNameIDs = self.model.getRiderNameIDs()
        self.view.updateSubSelectionFrame(riderNameIDs)

    def envirBtnPress(self):
        # TODO get the list of envirs from the model
        envirStrList: List[tuple[str,id]] = []
        self.view.updateSubSelectionFrame(envirStrList)

    def simBtnPress(self):
        # TODO get the list of sims from the model
        simStrList: List[tuple[str,id]] = []
        self.view.updateSubSelectionFrame(simStrList)

    """ ------ Add Data Btn Callbacks ------ """
    def addRiderBtnPress(self):
        # TODO create a new rider in the model
        # TODO display the new (empty) rider in the view
        print("add Rider button pressed")

    def addEnvirBtnPress(self):
        # TODO create a new environment in the model
        # TODO display the new (empty) environment in the view
        print("add Environment button pressed")

    def addSimBtnPress(self):
        # TODO create a new simulation in the model
        # TODO display the new (empty) simulation in the view
        print("add Simulation button pressed")

    """ ------ Scroll List Btn Callbacks ------ """
    def riderSelectBtnPress(self, id: int):
        # TODO get rider from the model
        # TODO display rider in the view
        print(f"rider {id} selected")

    def envirSelectBtnPress(self, id: int):
        # TODO get environment from the model
        # TODO display environment in the view
        print(f"envir {id} selected")

    def simSelectBtnPress(self, id: int):
        # TODO get simulation from the model
        # TODO display simulation in the view
        print(f"sim {id} selected")

    """ ------ Save Data Callbacks ------ """
    def saveRiderBtnPress(self, attributeDict: Dict[str, str] = {}):
        # TODO check that the attributes are good?
        # TODO add a new rider to the model's list of riders
        # TODO call a view method that says either rider saved, updated, or invalid. look at the tutorial for how to do this
        print(attributeDict)
