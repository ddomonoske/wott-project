from typing import List
from numpy import linspace
from scipy.integrate import odeint
import matplotlib.pyplot as plot


class IPCalculator(object):
    GRAVITY = 9.81

    def __init__(self,
                 CdA: float,
                 airDensity: float,
                 massKG: float,
                 Crr: float,
                 mechLoss: float,
                 powerPlan: List[tuple[float,float]],
                 maxForce: float = 200,
                 distance: float = 4000,
                 dt: float = 1,
                 v0: float = 0) -> None:
        self.CdA = CdA
        self.airDensity = airDensity
        self.massKG = massKG
        self.Crr = Crr
        self.mechLoss = mechLoss
        self.powerPlan = powerPlan
        self.maxForce = maxForce
        self.distance = distance
        self.dt = dt
        self.v0 = v0

    # break into chunks because we're solving until a position is reached, not a time
    def solve(self,
              maxT: float = 480,
              chunkT: float = 10) -> None:
        # TODO probably initialize my output arrays here
        # TODO probably initialize chunking things too
        while (True):
            # TODO set up things for this chunk
            # create time vector for this chunk
            t = self.timeVector()

            # TODO solve for next chunk and add/append to output arrays

            # TODO exit if we've reached self.distance or maxT

        # TODO return output array(s)


    def timeVector(self, start: float, stop: float, dt: float = 1.0):
        n = int((stop - start) / dt)
        return linspace(start, stop, n, endpoint=False)

    def powerVector(self, timeVector, powerPlan: List[tuple[float,float]]):
        times, powers = zip(*powerPlan)
        # TODO create an array of powers for each time in timeVector, as indicated by the powerPlan

    def dvdt(self, v: float, t: float) -> float:
        # sum up all forces
        Frr = -1*(self.GRAVITY*self.massKG*self.Crr)    # rolling resistance
        Fad = -1*(self.CdA*self.airDensity*(v**2))/2    # aerodynamic drag
        Fp = self.calcPowerForce(self, v, t) * (1-self.mechLoss) # pedaling force - mechanical losses

        return ((Frr + Fad + Fp) / self.massKG)

    def calcPowerForce(self, v: float, t: float) -> float:
        # look up power according to plan
        times, powers = zip(*self.powerPlan)
        power = powers[-1]
        for i,time in enumerate(times):
            # print(f"t={t}, time={time}")
            if t < time:
                power = powers[i-1]
                break
        # print(f"t={t}, v={v}, p={power}")
        # limit force to max force
        if (self.maxForce*v < power):
            return self.maxForce
        else:
            return power / v
