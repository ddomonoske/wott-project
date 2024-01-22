from typing import List, Dict
import numpy as np
from scipy.integrate import odeint
from wottattributes import *


class IPCalculator(object):
    GRAVITY = 9.80665

    def __init__(self,
                 CdA: float,
                 airDensity: float,
                 massKG: float,
                 Crr: float,
                 mechLosses: float,
                 powerPlan: List[tuple[float,float,float]],
                 maxForce: float = 200,
                 raceDistance: float = 4000,
                 dt: float = 1,
                 v0: float = 0) -> None:
        self.CdA = CdA
        self.airDensity = airDensity
        self.massKG = massKG
        self.Crr = Crr
        self.mechLosses = mechLosses
        self.powerPlan = powerPlan
        self.maxForce = maxForce
        self.raceDistance = raceDistance
        self.dt = dt
        self.v0 = v0
        self.position = None
        self.velovity = None

    # calculate velocity and position for race
    def solve(self, tMax: float = 300) -> None:
        n = int(np.ceil(tMax / self.dt))
        self.time = np.linspace(0, tMax, n, endpoint=False)

        # solve ode for velocity, integrate for position
        self.velocity: np.ndarray = np.squeeze(odeint(self.dvdt, self.v0, self.time))
        self.position = np.cumsum(self.velocity) * self.dt

        # trim to when race is finished
        index = np.argmax(self.position > self.raceDistance)
        self.time = self.time[:index+1]
        self.velocity = self.velocity[:index+1]
        self.position = self.position[:index+1]

        # calculate final power array
        self.powerPlanArray = self.powerPlan2Array()
        self.power = np.where(self.maxForce*self.velocity<self.powerPlanArray,
                              self.maxForce*self.velocity,
                              self.powerPlanArray)

    def dvdt(self, v: float, t: float) -> float:
        # sum up all forces
        Frr = -1*(self.GRAVITY*self.massKG*self.Crr)    # rolling resistance
        Fad = -1*(self.CdA*self.airDensity*(v**2))/2    # aerodynamic drag
        Fp = self.calcPedalForce(v,t) * (1-self.mechLosses) # pedaling force - mechanical losses

        return (Frr + Fad + Fp) / self.massKG

    # make power vector according to power plan
    def powerPlan2Array(self) -> np.ndarray:
        times, powers, _ = zip(*self.powerPlan)
        powerPlanArray = np.zeros(np.size(self.time))

        max = len(times)
        for i in range(max):
            if i<max-1:
                powerPlanArray = np.where(np.logical_and(self.time>=times[i], self.time<times[i+1]),
                                          powers[i], powerPlanArray)
            else:
                powerPlanArray = np.where(self.time>=times[i], powers[i], powerPlanArray)
                break
        return powerPlanArray

    def getPowerFromPlan(self, t: float) -> float:
        # look up power according to plan
        times, powers, _ = zip(*self.powerPlan)
        power=powers[-1]
        for i,time in enumerate(times):
            if t < time:
                power = powers[i-1]
                break
        return power

    # this can't be vectorized because we don't know that t will be an element of self.time
    def calcPedalForce(self, v: float, t: float) -> float:
        power = self.getPowerFromPlan(t)
        if (self.maxForce*v < power):
            return self.maxForce
        else:
            return power / v

    def getLapSplits(self, interval: float = 125, distance: float = 4000) -> List[float]:
        n = int(np.ceil(distance / interval))
        self.splitDistances = np.linspace(interval, distance, n, endpoint=True)
        self.splitTimes = np.zeros(np.size(self.splitDistances))
        self.lapSplits = np.zeros(np.size(self.splitDistances))

        max = np.size(self.position)

        for i,splitDistance in enumerate(self.splitDistances):
            # get the index of the last position that's less than this
            index = np.argmax(self.position > splitDistance)

            # calculate a precise time by drawing a straight line
            p1 = self.position[index-1]
            p2 = self.position[index]
            t1 = self.time[index-1]
            t2 = self.time[index]
            self.splitTimes[i] = ((splitDistance-p1)/(p2-p1)) * (t2-t1) + t1

            self.lapSplits[i] = self.splitTimes[i] - self.splitTimes[i-1]

        return self.lapSplits.tolist()

    def buildSplitTable(self):
        headers = ["Distance","Lap Split","Total Time"]
        data = [self.splitDistances, self.lapSplits, self.splitTimes]
        data = np.transpose(data)
        self.splitTable = [headers] + data.tolist()
        return self.splitTable

    def getSimResults(self) -> Dict[str, object]:
        simData = {}
        simData[SimWindowAttributes.TIME] = self.time.tolist()
        simData[SimWindowAttributes.POWER] = self.power.tolist()
        simData[SimWindowAttributes.VELOCITY] = self.velocity.tolist()
        simData[SimWindowAttributes.SPLITS] = self.getLapSplits()
        simData[SimWindowAttributes.SPLITTABLE] = self.buildSplitTable()

        return simData
