import pickle
from typing import List
from pathlib import Path


# TODO check file stuff
# file paths for persistant data storage
defaultStorageDir = "~/Library/Application Support/wott_project"
ridersFile = "riders_data"
envirsFile = "envirs_data"
simsFile = "sims_data"

class Model(object):
    def __init__(self, storageDir: str = defaultStorageDir):
        self.storageDir = storageDir

        self.loadModel()

        # TODO should I have a save flag that represents if the data has been changed since it was last stored?

    """ ------ Load methods ------ """
    # load all model data
    def loadModel(self):
        # create application directory if it doesn't exist
        Path(self.storageDir).mkdir(parents=True, exist_ok=True)

        self.loadRiders()
        self.loadEnvirs()
        self.loadSims()

    # safely load riders
    def loadRiders(self):
        filePath = self.storageDir + "/" + ridersFile

        # load raw data
        data = self.loadObject(filePath)

        # init as empty list of riders
        self.riders = List[Rider]

        # if data represents list of riders, save to self.riders
        if isinstance(data, List):
            if data and isinstance(data[0], Rider):
                self.riders = data

    # safely load environments
    def loadEnvirs(self):
        filePath = self.storageDir + "/" + envirsFile

        # load raw data
        data = self.loadObject(filePath)

        # init as empty list of environments
        self.envirs = List[Environment]

        # if data represents list of environments, save to self.envirs
        if isinstance(data, List):
            if data and isinstance(data[0], Environment):
                self.envirs = data

    # safely load simulations(self):
    def loadSims(self):
        filePath = self.storageDir + "/" + simsFile

        # load raw data
        data = self.loadObject(filePath)

        # init as empty list of simulations
        self.sims = List[Simulation]

        # if data represents list of simulations, save to self.sims
        if isinstance(data, List):
            if data and isinstance(data[0], Simulation):
                self.sims = data


    # check file, load contents and return object. If file DNE, then return None
    def loadObject(self, filePath: str) -> object:
        if Path(filePath).exists():
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

    # save riders to file
    def saveRiders(self):
        filePath = self.storageDir + "/" + ridersFile
        self.saveObject(filePath, self.riders)

    # save environments to file
    def saveEnvirs(self):
        filePath = self.storageDir + "/" + envirsFile
        self.saveObject(filePath, self.envirs)

    # save simulations to file
    def saveSims(self):
        filePath = self.storageDir + "/" + simsFile
        self.saveObject(filePath, self.sims)

    # save an object to a binary file using Pickle. Deletes and replaces the file if it exists
    def saveObject(self, filePath: str, obj: object):
        # delete existing file
        if Path(filePath).exists():
            Path(filePath).unlink()

        # TODO check that file opened correctly
        f=open(filePath,"wb")

        # TODO check that this worked
        pickle.dump(obj, f)


    # get specific rider, given a string
    # get specific environment, given a string
    # get specific simulation, given a string

    # add rider
    # add environment
    # add simulation

    # get list of strings for names
    # get list of strings for environments
    # get list of strings for simulations

class Rider(object):
    def __init__(self) -> None:
        # name, weight, threshold, w', cda,
        # power results are a list of something
        pass

    # calculate threshold and w' from set of power results

    # get name

class Environment(object):
    def __init__(self) -> None:

        pass

class Simulation(object):
    def __init__(self) -> None:
        # distance
        self.rider: Rider = None
        self.envir: Environment = None
        # pacing strategy is a list of something
        pass

    # simulate race

# TODO these are stupid. The check can't be internal. The check has to be outside
class RiderList(object):
    def __init__(self, riders: List[Rider] = None):
        self.isRider = True
        self.riders = riders

    def safeGetRiders(self):
        if self.isRider:
            return self.riders
        else:
            return List[Rider]

class EnvirList(object):
    def __init__(self, envirs: List[Environment] = None):
        self.isEnvir = True
        self.envirs = envirs

    def safeGetEnvirs(self):
        if self.isEnvir:
            return self.envirs
        else:
            return List[Environment]

class SimList(object):
    def __init__(self, sims: List[Simulation] = None):
        self.isSim = True
        self.sims = sims

    def safeGetSims(self):
        if self.isSim:
            return self.sims
        else:
            return List[Simulation]
