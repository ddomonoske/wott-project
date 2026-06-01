from typing import List, Dict
import numpy as np
from scipy.integrate import odeint
import fitdecode
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
        headers = ["Distance (m)","Half Lap Splits","Total Time"]
        data = [self.splitDistances, self.lapSplits, self.splitTimes]
        data = np.transpose(data).tolist()
        data = [[f"{row[0]:.0f}",f"{row[1]:.2f}",f"{row[2]//60:.0f}:{row[2]%60:{0}6.3f}"] for row in data]
        self.splitTable = [headers] + data
        return self.splitTable

    def getSimResults(self) -> Dict[str, object]:
        simData = {}
        simData[SimWindowAttributes.TIME] = self.time.tolist()
        simData[SimWindowAttributes.POWER] = self.power.tolist()
        simData[SimWindowAttributes.VELOCITY] = (3600/1000 * self.velocity).tolist()
        simData[SimWindowAttributes.SPLITS] = self.getLapSplits()
        simData[SimWindowAttributes.SPLITTABLE] = self.buildSplitTable()

        return simData

class CdACalculator(object):
    GRAVITY = 9.80665

    def __init__(self,
                 filePath: str,
                 airDensity: float,
                 massKG: float,
                 Crr: float,
                 mechLosses: float) -> None:
        self.filePath = filePath
        self.airDensity = airDensity
        self.massKG = massKG
        self.Crr = Crr
        self.mechLosses = mechLosses

    def readFitFile(self):
        # find start time and file length
        with fitdecode.FitReader(self.filePath) as fit:
            for frame in fit:
                if (frame.frame_type == fitdecode.FIT_FRAME_DATA) and (frame.name == 'session'):
                    self.n = np.ceil(frame.get_field('total_moving_time').value).astype(int)
                    self.startTime = frame.get_field('start_time').value
                    break

        self.t = np.zeros(self.n)
        self.v = np.zeros(self.n)
        self.p = np.zeros(self.n)
        self.c = np.zeros(self.n)
        self.d = np.zeros(self.n)

        with fitdecode.FitReader(self.filePath) as fit:
            i = 0
            for frame in fit:
                if (frame.frame_type == fitdecode.FIT_FRAME_DATA) and (frame.name == 'record'):
                    self.t[i] = (frame.get_field("timestamp").value - self.startTime).total_seconds()
                    self.v[i] = frame.get_field("speed").value
                    self.p[i] = frame.get_field("power").value
                    self.c[i] = frame.get_field("cadence").value
                    self.d[i] = frame.get_field("distance").value
                    i += 1

        self.startIndex = 0
        self.endIndex = self._maxIndex = i-1

    # set the indices that are to be used for the calculation
    def setRange(self, start, end):
        if (start >= 0 and start < self._maxIndex and
                end > start and end <= self._maxIndex):
            self.startIndex = start
            self.endIndex = end
        else:
            raise ValueError(f"innapropriate start and end indices")

    def calcCdA(self, t: np.ndarray, v: np.ndarray, P: np.ndarray):
        assert np.min(v) > 5

        v_avg = np.mean(v)
        F_power = np.mean(P)/v_avg*(1-self.mechLosses)
        F_rolling = -1*self.massKG*self.GRAVITY*self.Crr
        F_accel = -1*self.massKG*(v[-1]-v[0])/(t[-1]-t[0])

        return 2/(self.airDensity*v_avg**2) * (F_power + F_rolling + F_accel)

    def calcCdASelection(self, chunk):
        # do the rolling chunk thing for the region between self.startIndex and self.stopIndex
        pass
    
    def getNormPower(self, p: np.ndarray) -> float:
        normPow = np.mean(p ** 4) ** 0.25
        return normPow
