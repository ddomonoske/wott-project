import pickle
from pathlib import Path
from model.entities import Rider, Environment, Simulation, AeroTest


_DEFAULT_DIR = Path.home() / "Library/Application Support/wott_project"


class Storage:
    def __init__(self, storage_dir: str = str(_DEFAULT_DIR)):
        self.storage_dir = Path(storage_dir)
        self._next_rider_id = 0
        self._next_envir_id = 0
        self._next_sim_id = 0
        self._next_aero_test_id = 0
        self.riders: list[Rider] = []
        self.envirs: list[Environment] = []
        self.sims: list[Simulation] = []
        self.aero_tests: list[AeroTest] = []
        self._load()

    # ------ load ------

    def _load(self):
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.riders = self._load_object("riders_data", list, Rider) or []
        self.envirs = self._load_object("envirs_data", list, Environment) or []
        self.sims = self._load_object("sims_data", list, Simulation) or []
        self.aero_tests = self._load_object("aerotests_data", list, AeroTest) or []
        meta = self._load_object("meta_data", dict)
        if isinstance(meta, dict):
            # Persist counters rather than computing max(existing_ids)+1 so that
            # IDs of deleted items are never reused across save/load cycles.
            self._next_rider_id = meta.get("next_rider_id", 0)
            self._next_envir_id = meta.get("next_envir_id", 0)
            self._next_sim_id = meta.get("next_sim_id", 0)
            self._next_aero_test_id = meta.get("next_aero_test_id", 0)

    def _load_object(self, filename: str, expected_type, item_type=None):
        path = self.storage_dir / filename
        if not path.exists():
            return None
        with open(path, "rb") as f:
            data = pickle.load(f)
        if not isinstance(data, expected_type):
            return None
        # Spot-check the first element to catch schema mismatches after a refactor.
        # Only the first element is checked; the rest are assumed consistent.
        if item_type and isinstance(data, list) and data and not isinstance(data[0], item_type):
            return None
        return data

    # ------ save ------

    def save(self):
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._save_object("riders_data", self.riders)
        self._save_object("envirs_data", self.envirs)
        self._save_object("sims_data", self.sims)
        self._save_object("aerotests_data", self.aero_tests)
        self._save_object("meta_data", {
            "next_rider_id": self._next_rider_id,
            "next_envir_id": self._next_envir_id,
            "next_sim_id": self._next_sim_id,
            "next_aero_test_id": self._next_aero_test_id,
        })

    def _save_object(self, filename: str, obj):
        path = self.storage_dir / filename
        if path.exists():
            path.unlink()
        with open(path, "wb") as f:
            pickle.dump(obj, f)

    # ------ riders ------

    def add_rider(self, **kwargs) -> Rider:
        rider = Rider(rider_id=self._next_rider_id, **kwargs)
        self._next_rider_id += 1
        self.riders.append(rider)
        return rider

    def get_rider(self, rider_id: int) -> Rider | None:
        return next((r for r in self.riders if r.rider_id == rider_id), None)

    def delete_rider(self, rider_id: int):
        rider = self.get_rider(rider_id)
        if rider:
            self.riders.remove(rider)

    def get_rider_name_ids(self) -> list[tuple[str, int]]:
        return [(r.name, r.rider_id) for r in self.riders]

    # ------ environments ------

    def add_environment(self, **kwargs) -> Environment:
        envir = Environment(envir_id=self._next_envir_id, **kwargs)
        self._next_envir_id += 1
        self.envirs.append(envir)
        return envir

    def get_envir(self, envir_id: int) -> Environment | None:
        return next((e for e in self.envirs if e.envir_id == envir_id), None)

    def delete_environment(self, envir_id: int):
        envir = self.get_envir(envir_id)
        if envir:
            self.envirs.remove(envir)

    def get_envir_name_ids(self) -> list[tuple[str, int]]:
        return [(e.name, e.envir_id) for e in self.envirs]

    # ------ simulations ------

    def add_simulation(self, **kwargs) -> Simulation:
        sim = Simulation(sim_id=self._next_sim_id, **kwargs)
        self._next_sim_id += 1
        self.sims.append(sim)
        return sim

    def get_sim(self, sim_id: int) -> Simulation | None:
        return next((s for s in self.sims if s.sim_id == sim_id), None)

    def delete_simulation(self, sim_id: int):
        sim = self.get_sim(sim_id)
        if sim:
            self.sims.remove(sim)

    def get_sim_name_ids(self) -> list[tuple[str, int]]:
        return [(s.name, s.sim_id) for s in self.sims]

    # ------ aero tests ------

    def add_aero_test(self, **kwargs) -> AeroTest:
        test = AeroTest(aero_test_id=self._next_aero_test_id, **kwargs)
        self._next_aero_test_id += 1
        self.aero_tests.append(test)
        return test

    def get_aero_test(self, aero_test_id: int) -> AeroTest | None:
        return next((t for t in self.aero_tests if t.aero_test_id == aero_test_id), None)

    def delete_aero_test(self, aero_test_id: int):
        test = self.get_aero_test(aero_test_id)
        if test:
            self.aero_tests.remove(test)

    def get_aero_test_name_ids(self) -> list[tuple[str, int]]:
        return [(t.name, t.aero_test_id) for t in self.aero_tests]
