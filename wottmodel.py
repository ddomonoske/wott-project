import pickle
from typing import List, Dict, Set, Tuple, Union
from pathlib import Path
from wottattributes import *
from wottcalcs import *


# TODO check file stuff
# file paths for persistant data storage
defaultStorageDir = Path.home() / "Library/Application Support/wott_project"
ridersFile = "riders_data"
envirsFile = "envirs_data"
simsFile = "sims_data"
metaFile = "meta_data"


""" ------ Helper Objects ------ """
class PowerPlanPoint(object):
    def __init__(self, start: float, power: float, duration: float):
        self._start = start
        self._power = power
        self._duration = duration

    def asTuple(self) -> Tuple[float,float,float]:
        return (self.getStart(), self.getPower(), self.getDuration())

    """ getters and setters """
    def setStart(self, start: float):
        self._start = start

    def setPower(self, power: float):
        self._power = power

    def setDuration(self, duration: float):
        self._duration = duration

    def getStart(self) -> float:
        return self._start

    def getPower(self) -> float:
        return self._power

    def getDuration(self) -> float:
        return self._duration


class PowerPlan(object):
    def __init__(self, powerPointList: List[Tuple[float,float,float]]=None):
        self.plan: List[PowerPlanPoint] = []
        self.duration = 0

        if powerPointList:
            for point in powerPointList:
                self.plan.append(PowerPlanPoint(start=point[0], power=point[1], duration=point[2]))
            self.updateDurations()

    def addPoint(self):
        newPoint = PowerPlanPoint(start=self.duration, power=0, duration=0)
        self.plan.append(newPoint)

    def updatePoint(self, index: int, power: float, duration: float):
        self.plan[index].setPower(power)
        self.plan[index].setDuration(duration)
        self.updateDurations()

    def swapPoints(self, i: int, j: int):
        l = len(self.plan)
        if (i<l and i>=0 and j<l and j>=0):
            self.plan[i], self.plan[j] = self.plan[j], self.plan[i]
            self.updateDurations()

    def deletePoint(self, index: int):
        if (index<len(self.plan) and index>=0):
            self.plan.pop(index)

    def updateDurations(self):
        cumulativeDuration = 0
        for point in self.plan:
            point.setStart(cumulativeDuration)
            cumulativeDuration +=  point.getDuration()
        self.duration = cumulativeDuration

    def asTupleList(self):
        return [point.asTuple() for point in self.plan]


""" ------ Rider ------ """
class Rider(object):
    def __init__(self, riderID: int, **kwargs) -> None:
        # init riderID, everything else gets defaults
        self.riderID = riderID
        self.firstName = ""
        self.lastName = ""
        self.weight = None
        self.FTP = None
        self.wPrime = None
        self.CdA = None
        self.powerResults = {}

        self.setProperty(nullAllowed=True, **kwargs)

    # TODO do more thorough value checking
    def setProperty(self, nullAllowed: bool = False, **kwargs):
        # get the current attributes
        tmp_riderID = self.riderID
        tmp_firstName = self.firstName
        tmp_lastName = self.lastName
        tmp_weight = self.weight
        tmp_FTP = self.FTP
        tmp_wPrime = self.wPrime
        tmp_CdA = self.CdA
        tmp_powerResults = self.powerResults

        for keyword, value in kwargs.items():
            try:
                match keyword:
                    case RiderAttributes.RIDERID:
                        tmp_riderID = int(value)
                    case RiderAttributes.FIRSTNAME:
                        tmp_firstName = str(value)
                    case RiderAttributes.LASTNAME:
                        tmp_lastName = str(value)
                    case RiderAttributes.WEIGHT:
                        tmp_weight = float(value)
                    case RiderAttributes.FTP:
                        tmp_FTP = float(value)
                    case RiderAttributes.WPRIME:
                        tmp_wPrime = float(value)
                    case RiderAttributes.CDA:
                        tmp_CdA = float(value)
                    case RiderAttributes.POWERRESULTS:
                        # TODO parse power results
                        tmp_powerResults = value
                    case _:
                        raise AttributeError(f"'{keyword}' is not a property of the Rider class")
            except (TypeError,ValueError) as e:
                raise TypeError(f"'{keyword}' entry is not valid")

        if not (nullAllowed or tmp_firstName or tmp_lastName):
            raise AttributeError("firstName or lastName must be set")

        # if no errors thrown, save to model
        self.riderID = tmp_riderID
        self.firstName = tmp_firstName
        self.lastName = tmp_lastName
        self.weight = tmp_weight
        self.FTP = tmp_FTP
        self.wPrime = tmp_wPrime
        self.CdA = tmp_CdA
        self.powerResults = tmp_powerResults

    # calculate threshold and w' from set of power results

    """ ------ getters ------ """
    def getName(self) -> str:
        name = self.firstName + " " + self.lastName
        return name.strip()

    def getID(self) -> int:
        return self.riderID

    def getNameID(self) -> tuple[str,int]:
        return (self.getName(), self.getID())

    def isRider(self, id: int):
        return self.riderID == id

    def getStrAttributeDict(self) -> Dict[str,object]:
        attributes = {
            RiderAttributes.RIDERID: self.riderID,
            RiderAttributes.FIRSTNAME: self.firstName,
            RiderAttributes.LASTNAME: self.lastName,
            RiderAttributes.WEIGHT: str(self.weight) if self.weight else "",
            RiderAttributes.FTP: str(self.FTP) if self.FTP else "",
            RiderAttributes.CDA: str(self.CdA) if self.CdA else "",
            RiderAttributes.WPRIME: str(self.wPrime) if self.wPrime else "",
            RiderAttributes.POWERRESULTS: self.powerResults
        }
        return attributes

    def getDataAttributeDict(self) -> Dict[str,object]:
        attributes = {
            RiderAttributes.RIDERID: int(self.riderID),
            RiderAttributes.FIRSTNAME: self.firstName,
            RiderAttributes.LASTNAME: self.lastName,
            RiderAttributes.WEIGHT: float(self.weight) if self.weight else 0,
            RiderAttributes.FTP: float(self.FTP) if self.FTP else 0,
            RiderAttributes.CDA: float(self.CdA) if self.CdA else 0,
            RiderAttributes.WPRIME: float(self.wPrime) if self.wPrime else 0,
            RiderAttributes.POWERRESULTS: self.powerResults
        }
        return attributes

""" ------ Environment ------ """
class Environment(object):
    def __init__(self, envirID: int, **kwargs) -> None:
        # init envirID, everything else gets defaults
        self.envirID = envirID
        self.envirName = ""
        self.airDensity = None
        self.Crr = None
        self.mechLosses = None

        self.setProperty(nullAllowed=True, **kwargs)

    # TODO check that the values are appropriate type and value
    def setProperty(self, nullAllowed: bool = False, **kwargs):
        # get the current attributes
        tmp_envirID = self.envirID
        tmp_envirName = self.envirName
        tmp_airDensity = self.airDensity
        tmp_Crr = self.Crr
        tmp_mechLosses = self.mechLosses

        for attribute, value in kwargs.items():
            try:
                match attribute:
                    case EnvirAttributes.ENVIRID:
                        tmp_envirID = int(value)
                    case EnvirAttributes.ENVIRNAME:
                        tmp_envirName = str(value)
                    case EnvirAttributes.AIRDENSITY:
                        tmp_airDensity = float(value)
                    case EnvirAttributes.CRR:
                        tmp_Crr = float(value)
                    case EnvirAttributes.MECHLOSSES:
                        tmp_mechLosses = float(value)
                    case _:
                        raise AttributeError(f"'{attribute}' is not a property of the Environment class")
            except (TypeError,ValueError) as e:
                raise TypeError(f"'{attribute}' entry is not valid")

        if not (nullAllowed or tmp_envirName):
            raise AttributeError("envirName must be set")

        # if no errors thrown, save to model
        self.envirID = tmp_envirID
        self.envirName = tmp_envirName
        self.airDensity = tmp_airDensity
        self.Crr = tmp_Crr
        self.mechLosses = tmp_mechLosses

    """ ------ getters ------ """
    def getName(self) -> str:
        return self.envirName

    def getID(self) -> int:
        return self.envirID

    def getNameID(self) -> tuple[str,int]:
        return (self.getName(), self.getID())

    def isEnvir(self, id: int):
        return self.envirID == id

    def getStrAttributeDict(self) -> Dict[str,object]:
        attributes = {
            EnvirAttributes.ENVIRID: self.envirID,
            EnvirAttributes.ENVIRNAME: self.envirName,
            EnvirAttributes.AIRDENSITY: str(self.airDensity) if self.airDensity else "",
            EnvirAttributes.CRR: str(self.Crr) if self.Crr else "",
            EnvirAttributes.MECHLOSSES: str(self.mechLosses) if self.mechLosses else ""
        }
        return attributes

    def getDataAttributeDict(self) -> Dict[str, object]:
        attributes = {
            EnvirAttributes.ENVIRID: int(self.envirID),
            EnvirAttributes.ENVIRNAME: self.envirName,
            EnvirAttributes.AIRDENSITY: float(self.airDensity) if self.airDensity else 0,
            EnvirAttributes.CRR: float(self.Crr) if self.Crr else 0,
            EnvirAttributes.MECHLOSSES: float(self.mechLosses) if self.mechLosses else 0
        }
        return attributes

""" ------ Simulation ------ """
class Simulation(object):
    def __init__(self, simID: int, **kwargs) -> None:
        self.simID = simID
        self.simName = ""
        self.rider: Rider = None
        self.envir: Environment = None
        self.model: Model = None
        self.powerPlan: PowerPlan = PowerPlan()

        self.setProperty(nullAllowed=True, **kwargs)

    # TODO do more thorough value checking
    def setProperty(self, nullAllowed: bool = False, **kwargs):
        # get the current attributes
        tmp_simID = self.simID
        tmp_simName = self.simName
        tmp_rider = self.rider
        tmp_envir = self.envir
        tmp_model = self.model
        tmp_powerPlan = self.powerPlan

        for attribute, value in kwargs.items():
            try:
                match attribute:
                    case SimAttributes.SIMID:
                        tmp_simID = int(value)
                    case SimAttributes.SIMNAME:
                        tmp_simName = str(value)
                    case SimAttributes.RIDER:
                        if (type(value)==Rider):
                            tmp_rider = value
                        elif (type(value)==tuple and type(value[1])==int):
                            if self.model:
                                tmp_rider = self.model.getRider(value[1])
                            else:
                                raise ValueError(f"no model to look up rider '{value}'")
                        else:
                            raise TypeError(f"'{attribute}' must be of Rider type")
                    case SimAttributes.ENVIR:
                        if (type(value)==Environment):
                            tmp_envir = value
                        elif (type(value)==tuple and type(value[1])==int):
                            if self.model:
                                tmp_envir = self.model.getEnvir(value[1])
                            else:
                                raise ValueError(f"no model to look up environment '{value}'")
                        else:
                            raise TypeError(f"'{attribute}' must be of Environment type")
                    case SimAttributes.MODEL:
                        if (type(value)==Model):
                            tmp_model = value
                        else:
                            raise TypeError(f"'{attribute}' must be of Model type")
                    case SimAttributes.POWERPLAN:
                        if (type(value==PowerPlan)):
                            tmp_powerPlan = value
                    case _:
                        raise AttributeError(f"'{attribute}' is not a property of the Simulation class")
            except (TypeError,ValueError) as error:
                raise TypeError(f"{error}; '{attribute}' entry is not valid")

        if not (nullAllowed or tmp_simName):
            raise AttributeError("simName must be set")

        # if no errors thrown, save to model
        self.simID = tmp_simID
        self.simName = tmp_simName
        self.rider = tmp_rider
        self.envir = tmp_envir
        self.model = tmp_model
        self.powerPlan = tmp_powerPlan

    # remove all keys that aren't part of a set
    def limitAttributes(self, attributeDict: Dict, validKeys: Set):
        newDict = {}

        for key in list(attributeDict.keys()):
            if key in validKeys:
                newDict[key] = attributeDict[key]

        return newDict

    # Run a simulation
    def runSimulation(self) -> Dict[str, object]:
        # combine all the values into a dictionary
        attributeDict = self.limitAttributes(self.rider.getDataAttributeDict(), IPCalcAttributes.set())
        attributeDict.update(self.limitAttributes(self.envir.getDataAttributeDict(), IPCalcAttributes.set()))
        attributeDict.update(self.limitAttributes(self.getDataAttributeDict(), IPCalcAttributes.set()))

        # create calculator and run
        self.calc = IPCalculator(dt=0.1, **attributeDict)
        self.calc.solve()
        self.simResults = self.calc.getSimResults()

        return self.simResults

    """ ------ getters and setters ------ """
    def setModel(self, model):
        self.model = model

    def setRider(self, rider: Rider):
        self.rider = rider

    def setEnvir(self, envir: Environment):
        self.envir = envir

    def getName(self) -> str:
        return self.simName

    def getID(self) -> int:
        return self.simID

    def getNameID(self) -> tuple[str,int]:
        return (self.getName(), self.getID())

    def getRider(self) -> Rider:
        return self.rider

    def getEnvir(self) -> Environment:
        return self.envir

    def isSim(self, id: int) -> bool:
        return self.simID == id

    def getRiderList(self) -> List[tuple[str,int]]:
        return self.model.getRiderNameIDs() if self.model else []

    def getEnvirList(self) -> List[tuple[str,int]]:
        return self.model.getEnvirNameIDs() if self.model else []

    def getPowerPlan(self) -> PowerPlan:
        return self.powerPlan if self.powerPlan else None

    def getStrPowerPlan(self) -> List[tuple[str,str,str]]:
        return self.powerPlan.asTupleList() if self.powerPlan else []

    def getStrAttributeDict(self) -> Dict[str,object]:
        attributes = {
            SimAttributes.SIMID: self.simID,
            SimAttributes.SIMNAME: self.simName,
            SimAttributes.RIDER: self.rider.getNameID() if self.rider else ("",-1),
            SimAttributes.ENVIR: self.envir.getNameID() if self.envir else ("",-1),
            SimAttributes.RIDERLIST: self.getRiderList(),
            SimAttributes.ENVIRLIST: self.getEnvirList(),
            SimAttributes.POWERPLAN: self.getStrPowerPlan()
        }
        return attributes

    def getDataAttributeDict(self) -> Dict[str,object]:
        attributes = {
            SimAttributes.SIMID: int(self.simID),
            SimAttributes.SIMNAME: self.simName,
            SimAttributes.RIDER: self.rider.getNameID() if self.rider else ("",-1),
            SimAttributes.ENVIR: self.envir.getNameID() if self.envir else ("",-1),
            SimAttributes.RIDERLIST: self.getRiderList(),
            SimAttributes.ENVIRLIST: self.getEnvirList(),
            SimAttributes.POWERPLAN: self.getStrPowerPlan()
        }
        return attributes

    # simulate race

""" ------ Meta Data ------ """
class WottMetaData(object):
    def __init__(self,
                 nextRiderID: int = 0,
                 nextEnvirID: int = 0,
                 nextSimID: int = 0) -> None:
        self.nextRiderID = nextRiderID
        self.nextEnvirID = nextEnvirID
        self.nextSimID = nextSimID

    def newRiderID(self) -> int:
        self.nextRiderID += 1
        return self.nextRiderID - 1

    def newEnvirID(self) -> int:
        self.nextEnvirID += 1
        return self.nextEnvirID - 1

    def newSimID(self) -> int:
        self.nextSimID += 1
        return self.nextSimID - 1

""" ------ Wott Model ------ """
class Model(object):
    def __init__(self, storageDir: str = str(defaultStorageDir)):
        self.storageDir = Path(storageDir)

        self.loadModel()

        # update the model stored in sims to self
        for sim in self.sims:
            sim.setModel(self)

        # TODO should I have a save flag that represents if the data has been changed since it was last saved?

    """ ------ Load methods ------ """
    # load all model data
    def loadModel(self):
        # create application directory if it doesn't exist
        Path(self.storageDir).mkdir(parents=True, exist_ok=True)

        self.loadRiders()
        self.loadEnvirs()
        self.loadSims()
        self.loadMetaData()

    # safely load riders
    def loadRiders(self):
        filePath = self.storageDir / ridersFile

        # load raw data
        data = self.loadObject(filePath)

        # init as empty list of riders
        self.riders: List[Rider] = []

        # if data represents list of riders, save to self.riders
        if isinstance(data, List):
            if data and isinstance(data[0], Rider):
                self.riders = data

    # safely load environments
    def loadEnvirs(self):
        filePath = self.storageDir / envirsFile

        # load raw data
        data = self.loadObject(filePath)

        # init as empty list of environments
        self.envirs: List[Environment] = []

        # if data represents list of environments, save to self.envirs
        if isinstance(data, List):
            if data and isinstance(data[0], Environment):
                self.envirs = data

    # safely load simulations(self):
    def loadSims(self):
        filePath = self.storageDir / simsFile

        # load raw data
        data = self.loadObject(filePath)

        # init as empty list of simulations
        self.sims: List[Simulation] = []

        # if data represents list of simulations, save to self.sims
        if isinstance(data, List):
            if data and isinstance(data[0], Simulation):
                self.sims = data

    # safely load meta data
    def loadMetaData(self):
        filePath = self.storageDir / metaFile

        # load raw data
        data = self.loadObject(filePath)

        # init as empty list of riders
        self.metaData = WottMetaData()

        # if data represents meta data, save to self.metaData
        if isinstance(data, WottMetaData):
            self.metaData = data


    # check file, load contents and return object. If file DNE, then return None
    def loadObject(self, filePath: Path) -> object:
        if filePath.exists():
            f=open(filePath,"rb")
            # TODO check file is valid python object
            data = pickle.load(f)
            f.close()
        else:
            data = None
        return data

    """ ------ Save methods ------ """
    # save all model data
    def saveModel(self):
        # create application directory if it doesn't exist
        Path(self.storageDir).mkdir(parents=True, exist_ok=True)

        # remove the links to model stored in sims (to save space)
        for sim in self.sims:
            sim.model = None

        self.saveRiders()
        self.saveEnvirs()
        self.saveSims()
        self.saveMetaData()

    # save riders to file
    def saveRiders(self):
        filePath = self.storageDir / ridersFile
        self.saveObject(filePath, self.riders)

    # save environments to file
    def saveEnvirs(self):
        filePath = self.storageDir / envirsFile
        self.saveObject(filePath, self.envirs)

    # save simulations to file
    def saveSims(self):
        filePath = self.storageDir / simsFile
        self.saveObject(filePath, self.sims)

    # save meta data to file
    def saveMetaData(self):
        filePath = self.storageDir / metaFile
        self.saveObject(filePath, self.metaData)

    # save an object to a binary file using Pickle. Deletes and replaces the file if it exists
    def saveObject(self, filePath: str, obj: object):
        # delete existing file
        if Path(filePath).exists():
            Path(filePath).unlink()

        # TODO check that file opened correctly
        f=open(filePath,"wb")

        # TODO check that this worked
        pickle.dump(obj, f)

    """ ------ rider/envir/sim getters ------ """
    # get specific rider, given a riderID
    def getRider(self, riderID: int) -> Rider:
        for rider in self.riders:
            if rider.isRider(riderID):
                return rider
        return None

    # get specific environment, given a string
    def getEnvir(self, envirID: int) -> Environment:
        for envir in self.envirs:
            if envir.isEnvir(envirID):
                return envir
        return None

    # get specific simulation, given a string
    def getSim(self, simID: int) -> Simulation:
        for sim in self.sims:
            if sim.isSim(simID):
                return sim
        return None

    """ ------ Add/Delete methods ------ """
    # add new rider. Returns the new rider
    def addRider(self, **kwargs) -> Rider:
        # get next riderID from metadata
        riderID = self.metaData.newRiderID()

        # make new rider and append to model list
        rider = Rider(riderID, **kwargs)
        self.riders.append(rider)
        # TODO maybe sort the list of riders (or insert above)

        return rider

    # add new environment. Returns the new environment
    def addEnvironment(self, **kwargs) -> Rider:
        # get next envirID from metadata
        envirID = self.metaData.newEnvirID()

        # make new environment and append to model list
        envir = Environment(envirID, **kwargs)
        self.envirs.append(envir)
        # TODO maybe sort the list of environments (or insert above)

        return envir

    # add new simulation. Returns the new simulation
    def addSimulation(self, **kwargs) -> Simulation:
        # get next simID from metadata
        simID = self.metaData.newSimID()

        # make new simulation and append to model list
        sim = Simulation(simID, model=self, **kwargs)
        self.sims.append(sim)
        # TODO maybe sort the list of simulations (or insert above)

        return sim

    # get list of name-ID tuples for riders
    def getRiderNameIDs(self) -> List[tuple[str,int]]:
        return [rider.getNameID() for rider in self.riders]

    def getEnvirNameIDs(self) -> List[tuple[str,int]]:
        return [envir.getNameID() for envir in self.envirs]

    def getSimNameIDs(self) -> List[tuple[str,int]]:
        return [sim.getNameID() for sim in self.sims]

    # get list of strings for environments
    # get list of strings for simulations
