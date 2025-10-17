from wottmodel import *
from wottview import *

class Controller(object):
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view

    """ ------ Top Level Btn Callbacks ------ """
    def riderBtnPress(self):
        riderList = self.model.getRiderNameIDs()
        riderList = Controller.replaceEmptyName(riderList, "New Rider")
        self.view.showRiderSelectionList(riderList)
        self.view.clearMainContent()

    def envirBtnPress(self):
        envirList = self.model.getEnvirNameIDs()
        envirList = Controller.replaceEmptyName(envirList, "New Environment")
        self.view.showEnvirSelectionList(envirList)
        self.view.clearMainContent()

    def simBtnPress(self):
        simList = self.model.getSimNameIDs()
        simList = Controller.replaceEmptyName(simList, "New Simulation")
        self.view.showSimSelectionList(simList)
        self.view.clearMainContent()

    def aeroTestBtnPress(self):
        aeroTestList = self.model.getAeroTestNameIDs()
        aeroTestList = Controller.replaceEmptyName(aeroTestList, "New Aero Test")
        self.view.showAeroTestSelectionList(aeroTestList)
        self.view.clearMainContent()

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

    def addAeroTestBtnPress(self):
        # add new aero test and display aero test detail
        aeroTest = self.model.addAeroTest()
        self.view.showAeroTestDetail(aeroTest.getID(), aeroTest.getStrAttributeDict())

        # update the selection menu to include new aero test
        self.view.showAeroTestSelectionList(Controller.replaceEmptyName(self.model.getAeroTestNameIDs(), "New Aero Test"))

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

    def aeroTestSelectBtnPress(self, aeroTestID: int):
        aeroTest = self.model.getAeroTest(aeroTestID)
        self.view.showAeroTestDetail(aeroTest.getID(), aeroTest.getStrAttributeDict())

    """ ------ Save Data Callbacks ------ """
    def saveRiderBtnPress(self, riderID: int=-1, **kwargs):
        rider = self.model.getRider(riderID)

        try:
            rider.setProperty(**kwargs)

            # update the subselection menu in case the name changed
            self.view.showRiderSelectionList(Controller.replaceEmptyName(self.model.getRiderNameIDs(), "New Rider"))

            # show success message
            self.view.showDetailSuccessMessage("Rider saved")
        except (TypeError,AttributeError) as error:
            # show error message
            self.view.showDetailErrorMessage(error)

    def saveEnvirBtnPress(self, envirID: int=-1, **kwargs):
        envir = self.model.getEnvir(envirID)

        try:
            envir.setProperty(**kwargs)

            # update the subselection menu in case the name changed
            self.view.showEnvirSelectionList(Controller.replaceEmptyName(self.model.getEnvirNameIDs(), "New Environment"))

            # show success message
            self.view.showDetailSuccessMessage("Environment saved")
        except (TypeError,AttributeError) as error:
            # show error message
            self.view.showDetailErrorMessage(error)

    def saveSimBtnPress(self, simID: int=-1, **kwargs):
        sim = self.model.getSim(simID)

        try:
            sim.setProperty(**kwargs)

            # update the subselection menu in case the name changed
            self.view.showSimSelectionList(Controller.replaceEmptyName(self.model.getSimNameIDs(), "New Simulation"))

            # show success message
            self.view.showDetailSuccessMessage("Simulation saved")
        except (TypeError,AttributeError) as error:
            # show error message
            self.view.showDetailErrorMessage(error)

    def saveAeroTestBtnPress(self, aeroTestID: int=-1, **kwargs):
        aeroTest = self.model.getAeroTest(aeroTestID)

        try:
            aeroTest.setProperty(**kwargs)

            # update the subselection menu in case the name changed
            self.view.showAeroTestSelectionList(Controller.replaceEmptyName(self.model.getAeroTestNameIDs(), "New AeroTest"))

            # show success message
            self.view.showDetailSuccessMessage("Aero Test saved")
        except (TypeError, AttributeError) as error:
            # show error message
            self.view.showDetailErrorMessage(error)

    def runSimBtnPress(self, simID: int=-1):
        sim = self.model.getSim(simID)

        try:
            simResults = sim.runSimulation()
            self.view.showSimWindow(simID, simName=sim.getName(), **simResults)
        except Exception as error:
            self.view.showDetailErrorMessage(error)

    def calcAeroTestBtnPress(self, aeroTestID: int=-1):
        aeroTest = self.model.getAeroTest(aeroTestID)

        try:
            raise Exception("Sorry, this feature isn't implemented yet")
        except Exception as error:
            self.view.showDetailErrorMessage(error)

    def replaceEmptyName(nameIDs: List[tuple[str,int]], replacement: str = "Empty") -> List[tuple[str,int]]:
        newNameIDs: List[tuple[str,int]] = []
        for nameID in nameIDs:
            if nameID[0] == "":
                newNameID = (replacement, nameID[1])
                newNameIDs.append(newNameID)
            else:
                newNameIDs.append(nameID)
        return newNameIDs

    """ ------ Delete Data Callbacks ------ """
    def deleteRiderBtnPress(self, riderID: int):
        self.model.deleteRider(riderID)

        # perform same update as top level rider btn press
        self.riderBtnPress()

    def deleteEnvirBtnPress(self, envirID: int=-1, **kwargs):
        self.model.deleteEnvironment(envirID)

        # perform same update as top level envir btn press
        self.envirBtnPress()

    def deleteSimBtnPress(self, simID: int):
        self.model.deleteSimulation(simID)

        # perform same update as top level sim btn press
        self.simBtnPress()

    def deleteAeroTestBtnPress(self, aeroTestID: int):
        self.model.deleteAeroTest(aeroTestID)

        # perform same update as top level aeroTest btn press
        self.aeroTestBtnPress()

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
