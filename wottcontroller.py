from wottmodel import *
from wottview import *

class Controller(object):
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view
        # TODO have some sort of state machine that remembers which page we're looking at

    """ ------ Top Level Btn Callbacks ------ """
    def riderBtnPress(self):
        riderList = self.model.getRiderNameIDs()
        riderList = Controller.replaceEmptyName(riderList, "New Rider")
        self.view.showRiderSelectionList(riderList)
        # TODO clear the main frame

    def envirBtnPress(self):
        envirList = self.model.getEnvirNameIDs()
        envirList = Controller.replaceEmptyName(envirList, "New Environment")
        self.view.showEnvirSelectionList(envirList)
        # TODO clear the main frame

    def simBtnPress(self):
        # TODO get the list of sims from the model
        simStrList: List[tuple[str,int]] = []
        self.view.showSimSelectionList(simStrList)

    """ ------ Add Data Btn Callbacks ------ """
    def addRiderBtnPress(self):
        # add new rider and display rider detial
        rider = self.model.addRider()
        self.view.showRiderDetail(rider.getID(), rider.getStrAttributeDict())

        # update the selection menu to include new rider
        self.view.showRiderSelectionList(Controller.replaceEmptyName(self.model.getRiderNameIDs(), "New Rider"))

    def addEnvirBtnPress(self):
        # add new environment and display environment detail
        envir = self.model.addEnvironment()
        self.view.showEnvirDetail(envir.getID(), envir.getStrAttributeDict())

        # update the selection menu to include new environment
        self.view.showEnvirSelectionList(Controller.replaceEmptyName(self.model.getEnvirNameIDs(), "New Environment"))

    def addSimBtnPress(self):
        # TODO create a new simulation in the model
        # TODO display the new (empty) simulation in the view
        print("add Simulation button pressed")

    """ ------ Scroll List Btn Callbacks ------ """
    def riderSelectBtnPress(self, riderID: int):
        rider = self.model.getRider(riderID)
        self.view.showRiderDetail(rider.getID(), rider.getStrAttributeDict())

    def envirSelectBtnPress(self, envirID: int):
        envir = self.model.getEnvir(envirID)
        self.view.showEnvirDetail(envir.getID(), envir.getStrAttributeDict())

    def simSelectBtnPress(self, id: int):
        # TODO get simulation from the model
        # TODO display simulation in the view
        print(f"sim {id} selected")

    """ ------ Save Data Callbacks ------ """
    def saveRiderBtnPress(self, riderID: int=-1, attributeDict: Dict[str, str] = {}):
        # TODO check that the attributes are good?
        rider = self.model.getRider(riderID)

        try:
            rider.setProperty(attributeDict)

            # update the subselection menu in case the name changed
            self.view.showRiderSelectionList(Controller.replaceEmptyName(self.model.getRiderNameIDs(), "New Rider"))

            # show success message
            self.view.showDetailSaveSuccess("Rider saved")
        except (TypeError,AttributeError) as error:
            # show error message
            self.view.showDetailSaveError(error)

    def saveEnvirBtnPress(self, envirID: int=-1, attributeDict: Dict[str, str] = {}):
        # TODO check that the attributes are good?
        envir = self.model.getEnvir(envirID)

        try:
            envir.setProperty(attributeDict)

            # update the subselection menu in case the name changed
            self.view.showEnvirSelectionList(Controller.replaceEmptyName(self.model.getEnvirNameIDs(), "New Environment"))

            # show success message
            self.view.showDetailSaveSuccess("Environment saved")
        except (TypeError,AttributeError) as error:
            # show error message
            self.view.showDetailSaveError(error)

    def replaceEmptyName(nameIDs: List[tuple[str,int]], replacement: str = "Empty") -> List[tuple[str,int]]:
        newNameIDs: List[tuple[str,int]] = []
        for nameID in nameIDs:
            if nameID[0] == "":
                newNameID = (replacement, nameID[1])
                newNameIDs.append(newNameID)
            else:
                newNameIDs.append(nameID)
        return newNameIDs