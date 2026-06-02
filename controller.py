from calcs import IPCalculator, CdACalculator
from model.entities import Rider, Environment, Simulation, AeroTest
from model.storage import Storage
from view.panels import View


def _replace_empty_name(name_ids: list[tuple[str, int]], replacement: str = "Empty") -> list[tuple[str, int]]:
    # New entities have an empty name until the user fills it in and saves.
    # Substitute a placeholder so the selection list shows something readable.
    return [(replacement, id_) if name == "" else (name, id_) for name, id_ in name_ids]


class Controller:
    def __init__(self, storage: Storage, view: View):
        self.storage = storage
        self.view = view

    # ------ Top-level nav ------

    def rider_btn_press(self):
        self.view.show_rider_selection_list(
            _replace_empty_name(self.storage.get_rider_name_ids(), "New Rider"))
        self.view.clear_main_content()

    def envir_btn_press(self):
        self.view.show_envir_selection_list(
            _replace_empty_name(self.storage.get_envir_name_ids(), "New Environment"))
        self.view.clear_main_content()

    def sim_btn_press(self):
        self.view.show_sim_selection_list(
            _replace_empty_name(self.storage.get_sim_name_ids(), "New Simulation"))
        self.view.clear_main_content()

    def aero_test_btn_press(self):
        self.view.show_aero_test_selection_list(
            _replace_empty_name(self.storage.get_aero_test_name_ids(), "New Aero Test"))
        self.view.clear_main_content()

    # ------ Add ------

    def add_rider_btn_press(self):
        rider = self.storage.add_rider()
        self.view.show_rider_detail(rider)
        self.view.show_rider_selection_list(
            _replace_empty_name(self.storage.get_rider_name_ids(), "New Rider"))

    def add_envir_btn_press(self):
        envir = self.storage.add_environment()
        self.view.show_envir_detail(envir)
        self.view.show_envir_selection_list(
            _replace_empty_name(self.storage.get_envir_name_ids(), "New Environment"))

    def add_sim_btn_press(self):
        sim = self.storage.add_simulation()
        self._show_sim_detail(sim.sim_id)
        self.view.show_sim_selection_list(
            _replace_empty_name(self.storage.get_sim_name_ids(), "New Simulation"))

    def add_aero_test_btn_press(self):
        test = self.storage.add_aero_test()
        self._show_aero_test_detail(test.aero_test_id)
        self.view.show_aero_test_selection_list(
            _replace_empty_name(self.storage.get_aero_test_name_ids(), "New Aero Test"))

    # ------ Select ------

    def rider_select_btn_press(self, rider_id: int):
        rider = self.storage.get_rider(rider_id)
        self.view.show_rider_detail(rider)

    def envir_select_btn_press(self, envir_id: int):
        envir = self.storage.get_envir(envir_id)
        self.view.show_envir_detail(envir)

    def sim_select_btn_press(self, sim_id: int):
        self._show_sim_detail(sim_id)

    def aero_test_select_btn_press(self, aero_test_id: int):
        self._show_aero_test_detail(aero_test_id)

    # ------ Save ------

    def save_rider_btn_press(self, rider_id: int, **kwargs):
        rider = self.storage.get_rider(rider_id)
        try:
            rider.update(**kwargs)
            self.view.show_rider_selection_list(
                _replace_empty_name(self.storage.get_rider_name_ids(), "New Rider"))
            self.view.show_detail_success("Rider saved")
        except (TypeError, AttributeError) as e:
            self.view.show_detail_error(e)

    def save_envir_btn_press(self, envir_id: int, **kwargs):
        envir = self.storage.get_envir(envir_id)
        try:
            envir.update(**kwargs)
            self.view.show_envir_selection_list(
                _replace_empty_name(self.storage.get_envir_name_ids(), "New Environment"))
            self.view.show_detail_success("Environment saved")
        except (TypeError, AttributeError) as e:
            self.view.show_detail_error(e)

    def save_sim_btn_press(self, sim_id: int, **kwargs):
        sim = self.storage.get_sim(sim_id)
        try:
            sim.update(**kwargs)
            self.view.show_sim_selection_list(
                _replace_empty_name(self.storage.get_sim_name_ids(), "New Simulation"))
            self.view.show_detail_success("Simulation saved")
        except (TypeError, AttributeError) as e:
            self.view.show_detail_error(e)

    def save_aero_test_btn_press(self, aero_test_id: int, **kwargs):
        test = self.storage.get_aero_test(aero_test_id)
        try:
            test.update(**kwargs)
            self.view.show_aero_test_selection_list(
                _replace_empty_name(self.storage.get_aero_test_name_ids(), "New Aero Test"))
            self.view.show_detail_success("Aero Test saved")
        except (TypeError, AttributeError) as e:
            self.view.show_detail_error(e)

    # ------ Delete ------

    def delete_rider_btn_press(self, rider_id: int):
        self.storage.delete_rider(rider_id)
        self.rider_btn_press()

    def delete_envir_btn_press(self, envir_id: int):
        self.storage.delete_environment(envir_id)
        self.envir_btn_press()

    def delete_sim_btn_press(self, sim_id: int):
        self.storage.delete_simulation(sim_id)
        self.sim_btn_press()

    def delete_aero_test_btn_press(self, aero_test_id: int):
        self.storage.delete_aero_test(aero_test_id)
        self.aero_test_btn_press()

    # ------ Run simulation ------

    def run_sim_btn_press(self, sim_id: int):
        sim = self.storage.get_sim(sim_id)
        rider = self.storage.get_rider(sim.rider_id) if sim.rider_id is not None else None
        envir = self.storage.get_envir(sim.envir_id) if sim.envir_id is not None else None
        try:
            if rider is None or envir is None:
                raise ValueError("Simulation must have a rider and environment assigned")
            if not sim.power_plan.plan:
                raise ValueError("Simulation must have at least one power plan point")
            required = [rider.cda, rider.weight_kg, envir.air_density, envir.crr, envir.mech_losses]
            if any(v is None for v in required):
                raise ValueError("Rider and environment fields must all be filled in before running")
            calc = IPCalculator(
                cda=rider.cda,
                air_density=envir.air_density,
                mass_kg=rider.weight_kg,
                crr=envir.crr,
                mech_losses=envir.mech_losses,
                power_plan=sim.power_plan.as_tuple_list(),
                dt=0.1,
            )
            calc.solve()
            self.view.show_sim_window(sim_id, sim.name, calc.get_results())
        except Exception as e:
            self.view.show_detail_error(e)

    def calc_aero_test_btn_press(self, aero_test_id: int):
        self.view.show_detail_error("Aero Test calculation is not yet implemented")

    # ------ Power plan ------

    def save_power_point(self, sim_id: int, point_id: int, entries: tuple):
        sim = self.storage.get_sim(sim_id)
        sim.power_plan.update_point(point_id, entries[1], entries[2])
        self._show_sim_detail(sim_id)

    def swap_power_points(self, sim_id: int, i: int, j: int):
        sim = self.storage.get_sim(sim_id)
        sim.power_plan.swap_points(i, j)
        self._show_sim_detail(sim_id)

    def delete_power_point(self, sim_id: int, point_id: int):
        sim = self.storage.get_sim(sim_id)
        sim.power_plan.delete_point(point_id)
        self._show_sim_detail(sim_id)

    def add_power_point(self, sim_id: int):
        sim = self.storage.get_sim(sim_id)
        sim.power_plan.add_point()
        self._show_sim_detail(sim_id)

    # ------ Helpers ------

    def _resolve_rider_envir(self, sim_or_test) -> tuple[tuple, tuple]:
        # Returns (name, id) tuples for the assigned rider and environment.
        # id=-1 is the sentinel used by NameIDOptionMenu to mean "nothing selected".
        selected_rider = ("", -1)
        selected_envir = ("", -1)
        if sim_or_test.rider_id is not None:
            r = self.storage.get_rider(sim_or_test.rider_id)
            if r:
                selected_rider = (r.name or "New Rider", r.rider_id)
        if sim_or_test.envir_id is not None:
            e = self.storage.get_envir(sim_or_test.envir_id)
            if e:
                selected_envir = (e.name or "New Environment", e.envir_id)
        return selected_rider, selected_envir

    def _show_sim_detail(self, sim_id: int):
        sim = self.storage.get_sim(sim_id)
        selected_rider, selected_envir = self._resolve_rider_envir(sim)
        rider_names = _replace_empty_name(self.storage.get_rider_name_ids(), "New Rider")
        envir_names = _replace_empty_name(self.storage.get_envir_name_ids(), "New Environment")
        self.view.show_sim_detail(sim, selected_rider, selected_envir, rider_names, envir_names)

    def _show_aero_test_detail(self, aero_test_id: int):
        test = self.storage.get_aero_test(aero_test_id)
        selected_rider, selected_envir = self._resolve_rider_envir(test)
        rider_names = _replace_empty_name(self.storage.get_rider_name_ids(), "New Rider")
        envir_names = _replace_empty_name(self.storage.get_envir_name_ids(), "New Environment")
        self.view.show_aero_test_detail(test, selected_rider, selected_envir, rider_names, envir_names)
