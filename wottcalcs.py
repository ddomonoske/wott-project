from typing import List
import numpy as np
from scipy.integrate import odeint
from scipy.constants import g
import matplotlib.pyplot as plt


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
        n = tMax * self.dt
        self.time = np.linspace(0, tMax, n, endpoint=False)

        # solve ode for velocity, integrate for position
        self.velocity = odeint(self.dvdt, self.v0, self.time)
        self.position = np.cumsum(self.velocity) * self.dt

        # trim to when race is finished
        index = np.argmax(self.position > self.raceDistance)
        self.time = self.time[:index]
        self.velocity = self.velocity[:index]
        self.position = self.position[:index]

    # TODO make this GUI-friendly
    def plot(self):
        plt.figure()
        plt.subplot(2,2,1)
        plt.plot(self.time, self.velocity*3.6)
        plt.xlabel('time (s)')
        plt.ylabel('velocity (kph)')
        plt.grid()

        plt.subplot(2,2,2)
        plt.plot(self.position, self.velocity*3.6)
        plt.xlabel('distance (m)')
        plt.ylabel('velocity (kph)')
        plt.grid()

        plt.subplot(2,2,3)
        plt.plot(self.position, self.time)
        plt.xlabel('distance (m)')
        plt.ylabel('time (s)')
        plt.grid()

        plt.show()

    def dvdt(self, v: float, t: float) -> float:
        # sum up all forces
        Frr = -1*(self.GRAVITY*self.massKG*self.Crr)    # rolling resistance
        Fad = -1*(self.CdA*self.airDensity*(v**2))/2    # aerodynamic drag
        Fp = self.calcPowerForce(v, t) * (1-self.mechLoss) # pedaling force - mechanical losses

        return ((Frr + Fad + Fp) / self.massKG)

    def calcPowerForce(self, v: float, t: float) -> float:
        # look up power according to plan
        times, powers = zip(*self.powerPlan)
        power = powers[-1]
        for i,time in enumerate(times):
            if t < time:
                power = powers[i-1]
                break
        # limit force to max force
        if (self.maxForce*v < power):
            return self.maxForce
        else:
            return power / v
