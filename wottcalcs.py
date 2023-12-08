from typing import List
import numpy as np
from scipy.integrate import odeint


class IPCalculator(object):
    GRAVITY = 9.80665

    def __init__(self,
                 CdA: float,
                 airDensity: float,
                 massKG: float,
                 Crr: float,
                 mechLoss: float,
                 powerPlan: List[tuple[float,float]],
                 maxForce: float = 200,
                 raceDistance: float = 4000,
                 dt: float = 1,
                 v0: float = 0) -> None:
        self.CdA = CdA
        self.airDensity = airDensity
        self.massKG = massKG
        self.Crr = Crr
        self.mechLoss = mechLoss
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
        self.velocity = odeint(self.dvdt, self.v0, self.time)
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
        Fp = self.calcPedalForce(v,t) * (1-self.mechLoss) # pedaling force - mechanical losses

        return (Frr + Fad + Fp) / self.massKG

    # make power vector according to power plan
    def powerPlan2Array(self) -> np.ndarray:
        times, powers = zip(*self.powerPlan)
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
        times, powers = zip(*self.powerPlan)
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


