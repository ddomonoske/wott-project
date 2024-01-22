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
        simList = self.model.getSimNameIDs()
        simList = Controller.replaceEmptyName(simList, "New Simulation")
        self.view.showSimSelectionList(simList)

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
        # add new simulation and display simulation detail
        sim = self.model.addSimulation()
        self.view.showSimDetail(sim.getID(), sim.getStrAttributeDict())

        # update the selection menu to include new simulation
        self.view.showSimSelectionList(Controller.replaceEmptyName(self.model.getSimNameIDs(), "New Simulation"))

    """ ------ Scroll List Btn Callbacks ------ """
    def riderSelectBtnPress(self, riderID: int):
        rider = self.model.getRider(riderID)
        self.view.showRiderDetail(rider.getID(), rider.getStrAttributeDict())

    def envirSelectBtnPress(self, envirID: int):
        envir = self.model.getEnvir(envirID)
        self.view.showEnvirDetail(envir.getID(), envir.getStrAttributeDict())

    def simSelectBtnPress(self, simID: int):
        sim = self.model.getSim(simID)
        self.view.showSimDetail(sim.getID(), sim.getStrAttributeDict())

    """ ------ Save Data Callbacks ------ """
    def saveRiderBtnPress(self, riderID: int=-1, **kwargs):
        # TODO check that the attributes are good?
        rider = self.model.getRider(riderID)

        try:
            rider.setProperty(**kwargs)

            # update the subselection menu in case the name changed
            self.view.showRiderSelectionList(Controller.replaceEmptyName(self.model.getRiderNameIDs(), "New Rider"))

            # show success message
            self.view.showDetailSaveSuccess("Rider saved")
        except (TypeError,AttributeError) as error:
            # show error message
            self.view.showDetailSaveError(error)

    def saveEnvirBtnPress(self, envirID: int=-1, **kwargs):
        # TODO check that the attributes are good?
        envir = self.model.getEnvir(envirID)

        try:
            envir.setProperty(**kwargs)

            # update the subselection menu in case the name changed
            self.view.showEnvirSelectionList(Controller.replaceEmptyName(self.model.getEnvirNameIDs(), "New Environment"))

            # show success message
            self.view.showDetailSaveSuccess("Environment saved")
        except (TypeError,AttributeError) as error:
            # show error message
            self.view.showDetailSaveError(error)

    def saveSimBtnPress(self, simID: int=-1, **kwargs):
        # TODO check that the attributes are good?
        sim = self.model.getSim(simID)

        try:
            sim.setProperty(**kwargs)

            # update the subselection menu in case the name changed
            self.view.showSimSelectionList(Controller.replaceEmptyName(self.model.getSimNameIDs(), "New Simulation"))

            # show success message
            self.view.showDetailSaveSuccess("Simulation saved")
        except (TypeError,AttributeError) as error:
            # show error message
            self.view.showDetailSaveError(error)

    def runSimBtnPress(self, simID: int=-1):
        sim = self.model.getSim(simID)

        try:
            simResults = sim.runSimulation()
            self.view.showSimWindow(simID, simName=sim.getName(), **simResults)
        except Exception as error:
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

    """ ------ Power Plan Callbacks ------ """
    def savePowerPointPress(self, simID: int, pointID: int, point: Tuple[float,float,float]):
        sim = self.model.getSim(simID)
        sim.getPowerPlan().updatePoint(pointID, point[1], point[2])
        self.view.showSimDetail(sim.getID(), sim.getStrAttributeDict())

    def swapPowerPointPress(self, simID: int, i: int, j: int):
        sim = self.model.getSim(simID)
        sim.getPowerPlan().swapPoints(i,j)
        self.view.showSimDetail(sim.getID(), sim.getStrAttributeDict())

    def deletePowerPointPress(self, simID: int, pointID: int):
        sim = self.model.getSim(simID)
        sim.getPowerPlan().deletePoint(pointID)
        self.view.showSimDetail(sim.getID(), sim.getStrAttributeDict())

    def addPowerPointPress(self, simID: int):
        sim = self.model.getSim(simID)
        sim.getPowerPlan().addPoint()
        self.view.showSimDetail(sim.getID(), sim.getStrAttributeDict())