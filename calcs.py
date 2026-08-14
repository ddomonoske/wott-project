from typing import List, Dict, Optional
import numpy as np
from scipy.integrate import cumulative_trapezoid, solve_ivp
from scipy.ndimage import uniform_filter1d
import fitdecode


class IPCalculator:
    GRAVITY = 9.80665
    # Below this speed, the corner energy feedback term is treated as zero
    # (avoids a division-by-near-zero in _energy_accel; lean angle is already
    # ~0 at low speed anyway, so the term is physically negligible there).
    V_EPS = 0.1

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
                 v0: float = 0,
                 com_height_m: Optional[float] = None,
                 track_length: Optional[float] = None,
                 corners: Optional[float] = None) -> None:
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
        self.com_height_m = com_height_m
        self.track_length = track_length
        self.corners = corners
        self.position = None
        self.velocity = None
        self._has_track = False
        self._track_s = self._track_kappa = self._track_dkappa_ds = None

    def solve(self, t_max: float = 300) -> None:
        n = int(np.ceil(t_max / self.dt))
        self.time = np.linspace(0, t_max, n, endpoint=False)
        self._setup_track()

        def race_distance_event(t, y):
            return y[1] - self.race_distance
        race_distance_event.terminal = True
        race_distance_event.direction = 1

        # Corner curvature (kappa(s)) has sharp ramps -- a corner's transition
        # zone can be crossed in under a second at speed. RK45's default adaptive
        # step size is chosen from the smooth power/drag dynamics and can grow
        # to several seconds, stepping clean over a transition zone with no idea
        # it happened; the dense-output values reported inside that skipped
        # step are then a smooth polynomial guess, not the real corner-influenced
        # motion -- this is what produces spiky/jagged output. Capping the step
        # at dt forces the solver to actually resolve each transition.
        max_step = self.dt if self._has_track else np.inf

        sol = solve_ivp(self._ode_rhs, (0, t_max), [self.v0, 0.0],
                         t_eval=self.time, events=race_distance_event, max_step=max_step)

        if sol.t_events[0].size == 0:
            raise ValueError(
                f"Rider did not reach race_distance ({self.race_distance} m) within "
                f"{t_max}s (max position reached: {sol.y[1][-1]:.1f} m). "
                "Increase t_max or check the power plan."
            )

        # solve_ivp's t_eval grid stops at the last sampled point before the
        # event fires; append the precisely root-found crossing point so
        # position[-1] reaches race_distance exactly (matching the old
        # trim-based behavior downstream code / tests rely on).
        t_evt = sol.t_events[0][0]
        v_evt, s_evt = sol.y_events[0][0]
        self.time = np.append(sol.t, t_evt)
        self.velocity = np.append(sol.y[0], v_evt)
        self.position = np.append(sol.y[1], max(s_evt, self.race_distance))

        # Actual power output is capped at max_force * velocity (the maximum wattage
        # the drivetrain can transmit at that speed); below that cap, plan power is used.
        self._power_plan_array = self._plan_to_array()
        self.power = np.where(self.max_force * self.velocity < self._power_plan_array,
                              self.max_force * self.velocity,
                              self._power_plan_array)

    def _setup_track(self) -> None:
        self._has_track = (self.track_length is not None and self.corners is not None
                            and self.track_length > 0)
        if self._has_track:
            track = TrackShape(track_length=self.track_length, corners=self.corners).compute()
            self._track_s = track["s"]
            self._track_kappa = track["kappa"]
            self._track_dkappa_ds = np.gradient(self._track_kappa, self._track_s)
        else:
            self._track_s = self._track_kappa = self._track_dkappa_ds = None

    def _kappa_at(self, s: float) -> float:
        if not self._has_track:
            return 0.0
        s_mod = s % self.track_length
        return float(np.interp(s_mod, self._track_s, self._track_kappa))

    def _dkappa_ds_at(self, s: float) -> float:
        if not self._has_track:
            return 0.0
        s_mod = s % self.track_length
        return float(np.interp(s_mod, self._track_s, self._track_dkappa_ds))

    @staticmethod
    def _lean_angle(v: float, kappa: float, g: float = GRAVITY) -> float:
        # tan(theta) = v^2 / (g*r) == v^2*kappa/g; kappa=0 (straight) or v=0 -> theta=0.
        return float(np.arctan((v ** 2) * kappa / g))

    @staticmethod
    def _wheel_speed(v: float, kappa: float, theta: float,
                      com_height_m: Optional[float]) -> float:
        # Geometric coning: the CoM sits h*sin(theta) inside the wheels' turn
        # radius, so for the same angular sweep the wheels cover more ground.
        if not com_height_m:
            return v
        denom = max(1.0 - kappa * com_height_m * np.sin(theta), 0.01)
        return v / denom

    @staticmethod
    def _dtheta_ds(v: float, kappa: float, dkappa_ds: float, g: float = GRAVITY) -> float:
        # Partial d(theta)/ds from arctan(v^2*kappa/g), holding v fixed -- the
        # contribution to dtheta/dt from moving through the track's curvature.
        # (The other contribution, from v itself changing, is handled
        # separately by _energy_feedback_coeff below, since it couples back
        # into dv/dt and must be solved for rather than looked up.)
        x = (v ** 2) * kappa / g
        return (1.0 / (1.0 + x ** 2)) * (v ** 2 / g) * dkappa_ds

    @staticmethod
    def _energy_accel(v: float, com_height_m: Optional[float], theta: float,
                       dtheta_ds: float, v_wheel: float, g: float = GRAVITY,
                       v_eps: float = V_EPS) -> float:
        # Energy conservation on CoM vertical motion: d/dt(1/2 v^2) = g*h*sin(theta)*dtheta/dt.
        # This is the part of dtheta/dt driven by moving through the corner
        # (dtheta_ds * ds/dt); the part driven by v itself changing is added
        # separately in _ode_rhs via _energy_feedback_coeff.
        if not com_height_m or v < v_eps:
            return 0.0
        return (g * com_height_m * np.sin(theta) / v) * dtheta_ds * v_wheel

    @staticmethod
    def _energy_feedback_coeff(v: float, kappa: float, theta: float,
                                com_height_m: Optional[float], g: float = GRAVITY,
                                v_eps: float = V_EPS) -> float:
        # theta also depends on v (tan(theta) = v^2*kappa/g), so as v changes,
        # theta -- and therefore CoM height -- changes too, feeding back into
        # dv/dt. Left out, that omission silently leaks energy every corner
        # (verified: lean angle and speed compounded upward lap after lap in
        # testing). Coefficient of dv/dt in a_energy, derived via chain rule:
        #   dv/dt = a_power + (g*h*sin(theta)/v) * dtheta/dt
        #   dtheta/dt = dtheta_ds*ds/dt + [1/(1+x^2)]*(2*v*kappa/g)*dv/dt
        # Solving for dv/dt explicitly gives dv/dt = (a_power + D) / (1 - C)
        # (see _ode_rhs), with C = this coefficient (v and g cancel out of it).
        if not com_height_m or v < v_eps:
            return 0.0
        x = (v ** 2) * kappa / g
        return (2.0 * com_height_m * kappa * np.sin(theta)) / (1.0 + x ** 2)

    @staticmethod
    def _banked_rolling_resistance(mass_kg: float, crr: float, theta: float,
                                    g: float = GRAVITY) -> float:
        # Perfect banking at angle theta means no lateral friction is needed,
        # but the normal force increases: N = m*g/cos(theta).
        return -1.0 * (g * mass_kg * crr) / np.cos(theta)

    def _ode_rhs(self, t: float, y: np.ndarray) -> list:
        v, s = y
        kappa = self._kappa_at(s)
        theta = self._lean_angle(v, kappa)
        v_wheel = self._wheel_speed(v, kappa, theta, self.com_height_m)

        # f_rr: rolling resistance (always opposes motion, hence negative)
        # f_ad: aerodynamic drag (proportional to v^2, always negative)
        # f_p:  pedaling force reduced by drivetrain mechanical losses
        f_rr = self._banked_rolling_resistance(self.mass_kg, self.crr, theta)
        f_ad = -1 * (self.cda * self.air_density * (v ** 2)) / 2
        f_p = self.calc_pedal_force(v, t) * (1 - self.mech_losses)
        a_power = (f_rr + f_ad + f_p) / self.mass_kg

        dkappa_ds = self._dkappa_ds_at(s)
        dtheta_ds = self._dtheta_ds(v, kappa, dkappa_ds)
        a_energy_ds = self._energy_accel(v, self.com_height_m, theta, dtheta_ds, v_wheel)
        feedback = self._energy_feedback_coeff(v, kappa, theta, self.com_height_m)

        # dv/dt = a_power + a_energy_ds + feedback*dv/dt (self-referential through
        # theta's own dependence on v) -- solved explicitly, see _energy_feedback_coeff.
        dv_dt = (a_power + a_energy_ds) / max(1.0 - feedback, 0.1)

        return [dv_dt, v_wheel]

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
            reached = self.position >= split_dist
            if not np.any(reached):
                raise ValueError(
                    f"Rider did not reach split distance {split_dist:.0f} m "
                    f"(max position reached: {self.position[-1]:.1f} m). "
                    "Increase t_max or check the power plan."
                )
            index = np.argmax(reached)
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
            "velocity": (3600 / 1000 * self.velocity).tolist(),  # convert m/s to kph
            "splits": self.get_lap_splits(),
            "split_table": self.build_split_table(),
        }


class TrackShape:
    def __init__(self, track_length: float = 250.0, corners: float = 0.60,
                 transition: float = 30.0, dx: float = 0.1):
        self.track_length = track_length
        self.corners = corners
        self.transition = transition
        self.dx = dx

    def compute(self) -> dict:
        straight = self.track_length * (1 - self.corners) / 2
        corner = self.track_length * self.corners / 2
        radius = corner / np.pi

        s = np.arange(0, self.track_length + self.dx, self.dx)
        kappa = self._curvature(s, straight, corner, radius)

        heading = cumulative_trapezoid(kappa, s, initial=0)
        x = cumulative_trapezoid(np.cos(heading), s, initial=0)
        y = cumulative_trapezoid(np.sin(heading), s, initial=0)

        return {"s": s, "kappa": kappa, "x": x, "y": y, "radius": radius}

    def _curvature(self, d: np.ndarray, straight: float,
                   corner: float, radius: float) -> np.ndarray:
        p = d % (straight + corner)
        c_beg = straight / 2
        kappa = np.zeros(len(d))
        kappa[(p > c_beg) & (p <= c_beg + corner)] = 1.0 / radius
        window = int(np.ceil(self.transition / self.dx))
        return uniform_filter1d(kappa, size=window, mode='nearest')


def read_fit_file_data(file_path: str) -> dict[str, np.ndarray]:
    """Read all numeric record fields from a FIT file.

    Returns a dict of field_name -> 1-D numpy array. Always includes
    'elapsed_time' (seconds from session start) when a session record is found.
    Non-numeric fields and None values are excluded. Missing values for a given
    field on a particular record are stored as NaN.
    """
    start_time = None
    with fitdecode.FitReader(file_path) as fit:
        for frame in fit:
            if frame.frame_type == fitdecode.FIT_FRAME_DATA and frame.name == 'session':
                try:
                    start_time = frame.get_field('start_time').value
                except Exception:
                    pass
                break

    rows: list[dict] = []
    with fitdecode.FitReader(file_path) as fit:
        for frame in fit:
            if frame.frame_type != fitdecode.FIT_FRAME_DATA or frame.name != 'record':
                continue
            row: dict[str, float] = {}
            for fdata in frame.fields:
                if fdata.name == 'timestamp':
                    if start_time is not None:
                        try:
                            row['elapsed_time'] = (fdata.value - start_time).total_seconds()
                        except (TypeError, AttributeError):
                            pass
                elif fdata.value is not None and isinstance(fdata.value, (int, float)):
                    row[fdata.name] = float(fdata.value)
            rows.append(row)

    if not rows:
        return {}

    all_keys: set[str] = set()
    for row in rows:
        all_keys.update(row.keys())

    n = len(rows)
    result: dict[str, np.ndarray] = {}
    for key in all_keys:
        arr = np.empty(n)
        for i, row in enumerate(rows):
            arr[i] = row.get(key, np.nan)
        result[key] = arr

    return result


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
