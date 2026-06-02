from typing import List, Dict
import numpy as np
from scipy.integrate import odeint
import fitdecode


class IPCalculator:
    GRAVITY = 9.80665

    def __init__(self,
                 cda: float,
                 air_density: float,
                 mass_kg: float,
                 crr: float,
                 mech_losses: float,
                 power_plan: List[tuple[float, float, float]],
                 max_force: float = 200,
                 race_distance: float = 4000,
                 dt: float = 1,
                 v0: float = 0) -> None:
        self.cda = cda
        self.air_density = air_density
        self.mass_kg = mass_kg
        self.crr = crr
        self.mech_losses = mech_losses
        self.power_plan = power_plan
        self.max_force = max_force
        self.race_distance = race_distance
        self.dt = dt
        self.v0 = v0
        self.position = None
        self.velocity = None

    def solve(self, t_max: float = 300) -> None:
        n = int(np.ceil(t_max / self.dt))
        self.time = np.linspace(0, t_max, n, endpoint=False)

        self.velocity = np.squeeze(odeint(self._dvdt, self.v0, self.time))
        self.position = np.cumsum(self.velocity) * self.dt

        # Trim arrays to the first moment position exceeds race_distance.
        # argmax returns the index of the first True, which is one step past the finish.
        index = np.argmax(self.position > self.race_distance)
        self.time = self.time[:index + 1]
        self.velocity = self.velocity[:index + 1]
        self.position = self.position[:index + 1]

        # Actual power output is capped at max_force * velocity (the maximum wattage
        # the drivetrain can transmit at that speed); below that cap, plan power is used.
        self._power_plan_array = self._plan_to_array()
        self.power = np.where(self.max_force * self.velocity < self._power_plan_array,
                              self.max_force * self.velocity,
                              self._power_plan_array)

    def _dvdt(self, v: float, t: float) -> float:
        # Newton's second law: a = F_net / m.
        # f_rr: rolling resistance (always opposes motion, hence negative)
        # f_ad: aerodynamic drag (proportional to v², always negative)
        # f_p:  pedaling force reduced by drivetrain mechanical losses
        f_rr = -1 * (self.GRAVITY * self.mass_kg * self.crr)
        f_ad = -1 * (self.cda * self.air_density * (v ** 2)) / 2
        f_p = self.calc_pedal_force(v, t) * (1 - self.mech_losses)
        return (f_rr + f_ad + f_p) / self.mass_kg

    def _plan_to_array(self) -> np.ndarray:
        times, powers, _ = zip(*self.power_plan)
        arr = np.zeros(np.size(self.time))
        n = len(times)
        for i in range(n):
            if i < n - 1:
                arr = np.where(np.logical_and(self.time >= times[i], self.time < times[i + 1]),
                               powers[i], arr)
            else:
                arr = np.where(self.time >= times[i], powers[i], arr)
                break
        return arr

    def get_power_from_plan(self, t: float) -> float:
        times, powers, _ = zip(*self.power_plan)
        power = powers[-1]
        for i, time in enumerate(times):
            if t < time:
                power = powers[i - 1]
                break
        return power

    def calc_pedal_force(self, v: float, t: float) -> float:
        power = self.get_power_from_plan(t)
        # At low speed, power/v would exceed what the drivetrain can physically produce,
        # so we cap force at max_force (torque limit) rather than targeting exact wattage.
        if self.max_force * v < power:
            return self.max_force
        else:
            return power / v if v > 0 else 0

    def get_lap_splits(self, interval: float = 125, distance: float = 4000) -> List[float]:
        n = int(np.ceil(distance / interval))
        self.split_distances = np.linspace(interval, distance, n, endpoint=True)
        self.split_times = np.zeros(np.size(self.split_distances))
        self.lap_splits = np.zeros(np.size(self.split_distances))

        for i, split_dist in enumerate(self.split_distances):
            index = np.argmax(self.position > split_dist)
            p1, p2 = self.position[index - 1], self.position[index]
            t1, t2 = self.time[index - 1], self.time[index]
            # Linear interpolation between the two position samples that straddle
            # the split distance, giving sub-timestep accuracy for split times.
            self.split_times[i] = ((split_dist - p1) / (p2 - p1)) * (t2 - t1) + t1
            self.lap_splits[i] = self.split_times[i] - self.split_times[i - 1]

        return self.lap_splits.tolist()

    def build_split_table(self) -> list:
        headers = ["Distance (m)", "Half Lap Splits", "Total Time"]
        data = np.transpose([self.split_distances, self.lap_splits, self.split_times]).tolist()
        rows = [[f"{r[0]:.0f}", f"{r[1]:.2f}", f"{r[2] // 60:.0f}:{r[2] % 60:{0}6.3f}"]
                for r in data]
        return [headers] + rows

    def get_results(self) -> Dict[str, object]:
        return {
            "time": self.time.tolist(),
            "power": self.power.tolist(),
            "velocity": (3600 / 1000 * self.velocity).tolist(),  # convert m/s → kph
            "splits": self.get_lap_splits(),
            "split_table": self.build_split_table(),
        }


class CdACalculator:
    GRAVITY = 9.80665

    def __init__(self,
                 file_path: str,
                 air_density: float,
                 mass_kg: float,
                 crr: float,
                 mech_losses: float) -> None:
        self.file_path = file_path
        self.air_density = air_density
        self.mass_kg = mass_kg
        self.crr = crr
        self.mech_losses = mech_losses

    def read_fit_file(self):
        with fitdecode.FitReader(self.file_path) as fit:
            for frame in fit:
                if frame.frame_type == fitdecode.FIT_FRAME_DATA and frame.name == 'session':
                    self.n = np.ceil(frame.get_field('total_moving_time').value).astype(int)
                    self.start_time = frame.get_field('start_time').value
                    break

        self.t = np.zeros(self.n)
        self.v = np.zeros(self.n)
        self.p = np.zeros(self.n)
        self.c = np.zeros(self.n)
        self.d = np.zeros(self.n)

        with fitdecode.FitReader(self.file_path) as fit:
            i = 0
            for frame in fit:
                if frame.frame_type == fitdecode.FIT_FRAME_DATA and frame.name == 'record':
                    self.t[i] = (frame.get_field("timestamp").value - self.start_time).total_seconds()
                    self.v[i] = frame.get_field("speed").value
                    self.p[i] = frame.get_field("power").value
                    self.c[i] = frame.get_field("cadence").value
                    self.d[i] = frame.get_field("distance").value
                    i += 1

        self.start_index = 0
        self.end_index = self._max_index = i - 1

    def set_range(self, start: int, end: int):
        if 0 <= start < self._max_index and start < end <= self._max_index:
            self.start_index = start
            self.end_index = end
        else:
            raise ValueError("inappropriate start and end indices")

    def calc_cda(self, t: np.ndarray, v: np.ndarray, p: np.ndarray) -> float:
        assert np.min(v) > 5
        v_avg = np.mean(v)
        f_power = np.mean(p) / v_avg * (1 - self.mech_losses)
        f_rolling = -1 * self.mass_kg * self.GRAVITY * self.crr
        f_accel = -1 * self.mass_kg * (v[-1] - v[0]) / (t[-1] - t[0])
        return 2 / (self.air_density * v_avg ** 2) * (f_power + f_rolling + f_accel)

    def get_norm_power(self, p: np.ndarray) -> float:
        return float(np.mean(p ** 4) ** 0.25)
