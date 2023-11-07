import pickle
from typing import List, Dict
from pathlib import Path


# TODO check file stuff
# file paths for persistant data storage
defaultStorageDir = Path.home() / "Library/Application Support/wott_project"
ridersFile = "riders_data"
envirsFile = "envirs_data"
simsFile = "sims_data"
metaFile = "meta_data"

""" ------ Rider ------ """
class Rider(object):
    # valid keys for setting Rider attributes
    class attributes:
        RIDERID = "riderID"
        FIRSTNAME = "firstName"
        LASTNAME = "lastName"
        WEIGHT = "weight"
        FTP = "FTP"
        WPRIME = "wPrime"
        CDA = "CdA"
        POWERRESULTS = "powerResults"

    keyList = [
        attributes.RIDERID,
        attributes.FIRSTNAME,
        attributes.LASTNAME,
        attributes.WEIGHT,
        attributes.FTP,
        attributes.WPRIME,
        attributes.CDA,
        attributes.POWERRESULTS
    ]

    def __init__(self,
                 riderID: int,
                 firstName: str = "",
                 lastName: str = "",
                 weight: float = None,
                 FTP: float = None,
                 wPrime: float = None,
                 CdA: float = None,
                 powerResults: Dict[float, float] = {},
                 attributeDict: Dict[str, object] = {}) -> None:
        self.riderID = riderID
        self.firstName = firstName
        self.lastName = lastName
        self.weight = weight
        self.FTP = FTP
        self.wPrime = wPrime
        self.CdA = CdA
        self.powerResults = powerResults

        if attributeDict:
            self.setProperty(attributeDict, nullAllowed=True)

    # TODO check that the values are appropriate type and value
    # TODO I think there's a more pythonic way to do this, but it works
    def setProperty(self, attributeDict: Dict[str, object], nullAllowed: bool = False):
        # get the current attributes
        tmp_riderID = self.riderID
        tmp_firstName = self.firstName
        tmp_lastName = self.lastName
        tmp_weight = self.weight
        tmp_FTP = self.FTP
        tmp_wPrime = self.wPrime
        tmp_CdA = self.CdA
        tmp_powerResults = self.powerResults

        for attribute, value in attributeDict.items():
            try:
                match attribute:
                    case self.attributes.RIDERID:
                        tmp_riderID = int(value)
                    case self.attributes.FIRSTNAME:
                        tmp_firstName = str(value)
                    case self.attributes.LASTNAME:
                        tmp_lastName = str(value)
                    case self.attributes.WEIGHT:
                        tmp_weight = float(value)
                    case self.attributes.FTP:
                        tmp_FTP = float(value)
                    case self.attributes.WPRIME:
                        tmp_wPrime = float(value)
                    case self.attributes.CDA:
                        tmp_CdA = float(value)
                    case self.attributes.POWERRESULTS:
                        # TODO parse power results
                        tmp_powerResults = value
                    case _:
                        raise AttributeError(f"'{attribute}' is not a property of the Rider class")
            except (TypeError,ValueError) as e:
                raise TypeError(f"'{attribute}' entry is not valid")

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
            Rider.attributes.RIDERID: self.riderID,
            Rider.attributes.FIRSTNAME: self.firstName,
            Rider.attributes.LASTNAME: self.lastName,
            Rider.attributes.WEIGHT: str(self.weight) if self.weight else "",
            Rider.attributes.FTP: str(self.FTP) if self.FTP else "",
            Rider.attributes.CDA: str(self.CdA) if self.CdA else "",
            Rider.attributes.WPRIME: str(self.wPrime) if self.wPrime else "",
            Rider.attributes.POWERRESULTS: self.powerResults
        }
        return attributes

""" ------ Environment ------ """
class Environment(object):
    # valid keys for setting Rider attributes
    class attributes:
        ENVIRID = "envirID"
        ENVIRNAME = "envirName"
        AIRDENSITY = "airDensity"
        CRR = "Crr"
        MECHLOSSES = "mechLosses"

    keyList = [
        attributes.ENVIRID,
        attributes.ENVIRNAME,
        attributes.AIRDENSITY,
        attributes.CRR,
        attributes.MECHLOSSES
    ]

    def __init__(self,
                 envirID: int,
                 envirName: str = "",
                 airDensity: float = None,
                 Crr: float = None,
                 mechLosses: float = None,
                 attributeDict: Dict[str, object] = {}) -> None:
        self.envirID = envirID
        self.envirName = envirName
        self.airDensity = airDensity
        self.Crr = Crr
        self.mechLosses = mechLosses

        if attributeDict:
            self.setProperty(attributeDict, nullAllowed=True)

    # TODO check that the values are appropriate type and value
    # TODO I think there's a more pythonic way to do this, but it works
    def setProperty(self, attributeDict: Dict[str, object], nullAllowed: bool = False):
        # get the current attributes
        tmp_envirID = self.envirID
        tmp_envirName = self.envirName
        tmp_airDensity = self.airDensity
        tmp_Crr = self.Crr
        tmp_mechLosses = self.mechLosses

        for attribute, value in attributeDict.items():
            try:
                match attribute:
                    case self.attributes.ENVIRID:
                        tmp_envirID = int(value)
                    case self.attributes.ENVIRNAME:
                        tmp_envirName = str(value)
                    case self.attributes.AIRDENSITY:
                        tmp_airDensity = float(value)
                    case self.attributes.CRR:
                        tmp_Crr = float(value)
                    case self.attributes.MECHLOSSES:
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
            Environment.attributes.ENVIRID: self.envirID,
            Environment.attributes.ENVIRNAME: self.envirName,
            Environment.attributes.AIRDENSITY: str(self.airDensity) if self.airDensity else "",
            Environment.attributes.CRR: str(self.Crr) if self.Crr else "",
            Environment.attributes.MECHLOSSES: str(self.mechLosses) if self.mechLosses else ""
        }
        return attributes

""" ------ Simulation ------ """
class Simulation(object):
    class attributes:
        SIMID = "simID"
        SIMNAME = "simName"
        RIDER = "rider"
        ENVIR = "envir"
        RIDERLIST = "riderList"
        ENVIRLIST = "envirList"
        MODEL = "model"

    keyList = [
        attributes.SIMID,
        attributes.SIMNAME,
        attributes.RIDER,
        attributes.ENVIR,
        attributes.RIDERLIST,
        attributes.ENVIRLIST,
        attributes.MODEL
    ]

    def __init__(self,
                 simID: int,
                 simName: str = "",
                 rider: Rider = None,
                 envir: Environment = None,
                 model = None,
                 attributeDict: Dict[str, object] = {}) -> None:
        self.simID = simID
        self.model = model
        self.simName = simName
        self.rider = rider
        self.envir = envir

        if attributeDict:
            self.setProperty(attributeDict, nullAllowed=True)

        # TODO pacing strategy is a list of something, probably its own object, maybe even its own file

    def setProperty(self, attributeDict: Dict[str, object], nullAllowed: bool = False):
        # get the current attributes
        tmp_simID = self.simID
        tmp_simName = self.simName
        tmp_rider = self.rider
        tmp_envir = self.envir
        tmp_model = self.model

        for attribute, value in attributeDict.items():
            try:
                match attribute:
                    case self.attributes.SIMID:
                        tmp_simID = int(value)
                    case self.attributes.SIMNAME:
                        tmp_simName = str(value)
                    case self.attributes.RIDER:
                        if (type(value)==Rider):
                            tmp_rider = value
                        elif (type(value)==tuple and type(value[1])==int):
                            if self.model:
                                tmp_rider = self.model.getRider(value[1])
                            else:
                                raise ValueError(f"no model to look up rider '{value}'")
                        else:
                            raise TypeError(f"'{attribute}' must be of Rider type")
                    case self.attributes.ENVIR:
                        if (type(value)==Environment):
                            tmp_envir = value
                        elif (type(value)==tuple and type(value[1])==int):
                            if self.model:
                                tmp_envir = self.model.getEnvir(value[1])
                            else:
                                raise ValueError(f"no model to look up environment '{value}'")
                        else:
                            raise TypeError(f"'{attribute}' must be of Environment type")
                    case self.attributes.MODEL:
                        if (type(value)==Model):
                            tmp_model = value
                        else:
                            raise TypeError(f"'{attribute}' must be of Model type")
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

    """ ------ getters and setters ------ """
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

    def getStrAttributeDict(self) -> Dict[str,object]:
        attributes = {
            Simulation.attributes.SIMID: self.simID,
            Simulation.attributes.SIMNAME: self.simName,
            Simulation.attributes.RIDER: self.rider.getNameID() if self.rider else ("",-1),
            Simulation.attributes.ENVIR: self.envir.getNameID() if self.envir else ("",-1),
            Simulation.attributes.RIDERLIST: self.getRiderList(),
            Simulation.attributes.ENVIRLIST: self.getEnvirList()
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
    def addRider(self, attributeDict: Dict[str, object] = None) -> Rider:
        # get next riderID from metadata
        riderID = self.metaData.newRiderID()

        # make new rider and append to model list
        rider = Rider(riderID, attributeDict=attributeDict)
        self.riders.append(rider)
        # TODO maybe sort the list of riders (or insert above)

        return rider

    # add new environment. Returns the new environment
    def addEnvironment(self, attributeDict: Dict[str, object] = None) -> Rider:
        # get next envirID from metadata
        envirID = self.metaData.newEnvirID()

        # make new environment and append to model list
        envir = Environment(envirID, attributeDict=attributeDict)
        self.envirs.append(envir)
        # TODO maybe sort the list of environments (or insert above)

        return envir

    # add new simulation. Returns the new simulation
    def addSimulation(self, attributeDict: Dict[str, object] = None) -> Simulation:
        # get next simID from metadata
        simID = self.metaData.newSimID()

        # make new simulation and append to model list
        sim = Simulation(simID, model=self, attributeDict=attributeDict)
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
