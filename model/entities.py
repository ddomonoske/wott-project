from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PowerPlanPoint:
    start: float
    power: float
    duration: float

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.start, self.power, self.duration)


class PowerPlan:
    def __init__(self, point_list: list[tuple[float, float, float]] = None):
        self.plan: list[PowerPlanPoint] = []
        self.duration: float = 0.0
        if point_list:
            for p in point_list:
                self.plan.append(PowerPlanPoint(start=p[0], power=p[1], duration=p[2]))
            self._update_starts()  # recalculate starts from durations; input starts are ignored

    def add_point(self):
        self.plan.append(PowerPlanPoint(start=self.duration, power=0, duration=0))

    def update_point(self, index: int, power: float, duration: float):
        self.plan[index].power = power
        self.plan[index].duration = duration
        self._update_starts()

    def swap_points(self, i: int, j: int):
        n = len(self.plan)
        if 0 <= i < n and 0 <= j < n:
            self.plan[i], self.plan[j] = self.plan[j], self.plan[i]
            self._update_starts()

    def delete_point(self, index: int):
        if 0 <= index < len(self.plan):
            self.plan.pop(index)

    def _update_starts(self):
        # `start` is always derived from the cumulative sum of durations before it,
        # never stored independently — call this after any mutation.
        cumulative = 0.0
        for point in self.plan:
            point.start = cumulative
            cumulative += point.duration
        self.duration = cumulative

    def as_tuple_list(self) -> list[tuple[float, float, float]]:
        return [p.as_tuple() for p in self.plan]


_RIDER_FLOAT = frozenset({'weight_kg', 'ftp', 'w_prime', 'cda'})


@dataclass
class Rider:
    rider_id: int
    first_name: str = ""
    last_name: str = ""
    weight_kg: Optional[float] = None
    ftp: Optional[float] = None
    w_prime: Optional[float] = None
    cda: Optional[float] = None
    power_results: dict = field(default_factory=dict)

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def update(self, **kwargs) -> None:
        # Validate all fields before applying any — so a partial update never
        # leaves the object in a half-modified state on error.
        validated = {}
        for k, v in kwargs.items():
            if k == 'rider_id' or not hasattr(self, k):
                raise AttributeError(f"Unknown or read-only field {k!r}")
            if k in _RIDER_FLOAT:
                try:
                    validated[k] = float(v) if v not in (None, "") else None
                except (TypeError, ValueError):
                    raise TypeError(f"'{k}' must be a number")
            else:
                validated[k] = v
        new_first = validated.get('first_name', self.first_name)
        new_last = validated.get('last_name', self.last_name)
        if not (new_first or new_last):
            raise AttributeError("first_name or last_name must be set")
        for k, v in validated.items():
            setattr(self, k, v)


_ENVIR_FLOAT = frozenset({'air_density', 'crr', 'mech_losses'})


@dataclass
class Environment:
    envir_id: int
    name: str = ""
    air_density: Optional[float] = None
    crr: Optional[float] = None
    mech_losses: Optional[float] = None

    def update(self, **kwargs) -> None:
        validated = {}
        for k, v in kwargs.items():
            if k == 'envir_id' or not hasattr(self, k):
                raise AttributeError(f"Unknown or read-only field {k!r}")
            if k in _ENVIR_FLOAT:
                try:
                    validated[k] = float(v) if v not in (None, "") else None
                except (TypeError, ValueError):
                    raise TypeError(f"'{k}' must be a number")
            else:
                validated[k] = v
        new_name = validated.get('name', self.name)
        if not new_name:
            raise AttributeError("name must be set")
        for k, v in validated.items():
            setattr(self, k, v)


@dataclass
class Simulation:
    sim_id: int
    name: str = ""
    # Store IDs rather than object references so Simulation can be pickled without
    # embedding a full copy of the Rider/Environment. The controller resolves them
    # from Storage when needed.
    rider_id: Optional[int] = None
    envir_id: Optional[int] = None
    power_plan: PowerPlan = field(default_factory=PowerPlan)

    def update(self, **kwargs) -> None:
        validated = {}
        for k, v in kwargs.items():
            if k == 'sim_id' or not hasattr(self, k):
                raise AttributeError(f"Unknown or read-only field {k!r}")
            validated[k] = v
        new_name = validated.get('name', self.name)
        if not new_name:
            raise AttributeError("name must be set")
        for k, v in validated.items():
            setattr(self, k, v)


@dataclass
class AeroTest:
    aero_test_id: int
    name: str = ""
    rider_id: Optional[int] = None
    envir_id: Optional[int] = None
    data_file: Optional[str] = None

    def update(self, **kwargs) -> None:
        validated = {}
        for k, v in kwargs.items():
            if k == 'aero_test_id' or not hasattr(self, k):
                raise AttributeError(f"Unknown or read-only field {k!r}")
            validated[k] = v
        new_name = validated.get('name', self.name)
        if not new_name:
            raise AttributeError("name must be set")
        for k, v in validated.items():
            setattr(self, k, v)
