import pickle
from typing import List

class Model(object):
    def __init__(self):
        self.riders = List[Rider]
        self.envirs = List[Environment]
        self.sims = List[Simulation]
        pass

    # be able to load data
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

    # calculate threshold and kj from set of power results

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

