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
        return self.firstName + " " + self.lastName

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
    def __init__(self) -> None:

        pass

""" ------ Simulation ------ """
class Simulation(object):
    def __init__(self) -> None:
        # distance
        self.rider: Rider = None
        self.envir: Environment = None
        # pacing strategy is a list of something
        pass

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


    # get specific rider, given a riderID
    def getRider(self, riderID: int) -> Rider:
        for rider in self.riders:
            if rider.isRider(riderID):
                return rider
        return None

    # get specific environment, given a string
    # get specific simulation, given a string

    """ ------ Add/Delete methods ------ """
    # add new rider. Returns the new rider
    def addRider(self, attributeDict: Dict[str, object] = None) -> Rider:
        # get next riderID from metadata
        riderID = self.metaData.newRiderID()

        # make new rider and append to model list
        rider = Rider(riderID, attributeDict=attributeDict)
        self.riders.append(rider)
        # TODO maybe sort the list of riders (or instert above)

        return rider

    # add environment
    # add simulation

    # get list of name-ID tuples for riders
    def getRiderNameIDs(self) -> List[tuple[str,int]]:
        return [rider.getNameID() for rider in self.riders]

    # get list of strings for environments
    # get list of strings for simulations
