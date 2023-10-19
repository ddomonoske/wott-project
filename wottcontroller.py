from wottmodel import *
from wottview import *

class Controller(object):
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
        # TODO have some sort of state machine that remembers which page we're looking at

    """ ------ View Action Callbacks ------ """
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

    def subSelectBtnPress(self, name: str):
        print(f"{name} button pressed")
        # TODO use the state machine and the

    def saveRiderBtnPress(self, attributeDict: Dict[str, str] = {}):
        # TODO check that the attributes are good?
        # TODO add a new rider to the model's list of riders
        # TODO call a view method that says either rider saved, updated, or invalid. look at the tutorial for how to do this
        print(attributeDict)
