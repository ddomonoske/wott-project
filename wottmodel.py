import pickle
from typing import List


# TODO check file stuff
# file paths for persistant data storage
storageDir = "/Users/daviddomonoske/Library/Application Support/wott_project"
ridersFile = "riders_data"
evirsFile = "envirs_data"
simsFile = "sims_data"

class Model(object):
    def __init__(self):
        self.riders = List[Rider]
        self.envirs = List[Environment]
        self.sims = List[Simulation]

        # TODO should I have a save flag that represents if the data has been changed since it was last stored?

    # load all model data
    def loadModel(self):
        # TODO directory check

        self.loadRiders()
        self.loadEnvirs()
        self.loadSims()

    # TODO figure out an actually safe way to load this data, and apply to each list
    # load riders
    def loadRiders(self):
        filePath = storageDir + "/" + ridersFile
        
        # load raw data
        data = self.loadObject(filePath)

        # TODO this actually makes no sense
        # check that data represents Riders
        self.riders = data.safeGetRiders()

    # load environments
    def loadEnvirs(self):
        data = self.loadObject()

    # load simulations(self):
    def loadSims(self):
        data = self.loadObject()

    # check file, load contents and return object
    def loadObject(self, filePath: str) -> object:
        # TODO check file path exists / is valid
        f=open(filePath,"rb")
        return pickle.load(f)


    # be able to save data

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
