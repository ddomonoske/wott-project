import pytest
import numpy as np
from model.entities import Rider, Environment, Simulation, AeroTest, PowerPlan
from model.storage import Storage
from controller import Controller, _replace_empty_name


# ------ Stubs ------

class StubAeroTestWindow:
    def __init__(self):
        self.refreshed_selections = None

    def refresh_selections(self, selections):
        self.refreshed_selections = selections


class StubView:
    def __init__(self):
        self.last_error = None
        self.last_success = None
        self.rider_list = None
        self.envir_list = None
        self.sim_list = None
        self.aero_test_list = None
        self.shown_rider = None
        self.shown_envir = None
        self.shown_sim = None
        self.shown_aero_test = None
        self.sim_window_shown = False
        self.aero_test_window_shown = False
        self.aero_test_window_args = None
        self.aero_test_windows: dict = {}

    def show_rider_selection_list(self, name_ids): self.rider_list = name_ids
    def show_envir_selection_list(self, name_ids): self.envir_list = name_ids
    def show_sim_selection_list(self, name_ids): self.sim_list = name_ids
    def show_aero_test_selection_list(self, name_ids): self.aero_test_list = name_ids
    def clear_main_content(self): pass
    def show_rider_detail(self, rider): self.shown_rider = rider
    def show_envir_detail(self, envir): self.shown_envir = envir
    def show_sim_detail(self, sim, *args): self.shown_sim = sim
    def show_aero_test_detail(self, test, *args): self.shown_aero_test = test
    def show_detail_error(self, msg): self.last_error = str(msg)
    def show_detail_success(self, msg): self.last_success = msg
    def show_sim_window(self, *args, **kwargs): self.sim_window_shown = True

    def show_aero_test_window(self, aero_test_id, aero_test, fit_data):
        self.aero_test_window_shown = True
        self.aero_test_window_args = (aero_test_id, aero_test, fit_data)


@pytest.fixture
def ctrl(tmp_path):
    storage = Storage(storage_dir=str(tmp_path))
    view = StubView()
    return Controller(storage, view), storage, view


# ------ Helpers ------

def test_replace_empty_name():
    result = _replace_empty_name([("", 0), ("Bob", 1)], "New Rider")
    assert result[0] == ("New Rider", 0)
    assert result[1] == ("Bob", 1)


# ------ Rider flow ------

def test_add_rider(ctrl):
    c, storage, view = ctrl
    c.add_rider_btn_press()
    assert len(storage.riders) == 1
    assert view.shown_rider is not None
    assert view.rider_list is not None


def test_save_rider_valid(ctrl):
    c, storage, view = ctrl
    c.add_rider_btn_press()
    rider = storage.riders[0]
    c.save_rider_btn_press(rider.rider_id, first_name="David", last_name="D",
                           weight_kg="89", ftp="418", w_prime="28", cda="0.195")
    assert rider.first_name == "David"
    assert rider.ftp == 418.0
    assert view.last_success == "Rider saved"
    assert view.last_error is None


def test_save_rider_invalid(ctrl):
    c, storage, view = ctrl
    c.add_rider_btn_press()
    rider = storage.riders[0]
    c.save_rider_btn_press(rider.rider_id, first_name="", last_name="")
    assert view.last_error is not None


def test_delete_rider(ctrl):
    c, storage, view = ctrl
    c.add_rider_btn_press()
    rider = storage.riders[0]
    c.delete_rider_btn_press(rider.rider_id)
    assert len(storage.riders) == 0
    assert view.rider_list == []


# ------ Environment flow ------

def test_add_envir(ctrl):
    c, storage, view = ctrl
    c.add_envir_btn_press()
    assert len(storage.envirs) == 1
    assert view.shown_envir is not None


def test_save_envir_valid(ctrl):
    c, storage, view = ctrl
    c.add_envir_btn_press()
    envir = storage.envirs[0]
    c.save_envir_btn_press(envir.envir_id, name="COS", air_density="0.995",
                           crr="0.002", mech_losses="0.01")
    assert envir.name == "COS"
    assert view.last_success == "Environment saved"


# ------ Simulation flow ------

def test_add_sim(ctrl):
    c, storage, view = ctrl
    c.add_sim_btn_press()
    assert len(storage.sims) == 1
    assert view.shown_sim is not None


def test_save_sim_valid(ctrl):
    c, storage, view = ctrl
    c.add_sim_btn_press()
    sim = storage.sims[0]
    c.save_sim_btn_press(sim.sim_id, name="Test Sim", rider_id=None, envir_id=None)
    assert sim.name == "Test Sim"
    assert view.last_success == "Simulation saved"


def test_run_sim_missing_rider(ctrl):
    c, storage, view = ctrl
    c.add_sim_btn_press()
    sim = storage.sims[0]
    c.run_sim_btn_press(sim.sim_id)
    assert view.last_error is not None


# ------ Power plan ------

def test_add_power_point(ctrl):
    c, storage, view = ctrl
    c.add_sim_btn_press()
    sim = storage.sims[0]
    c.add_power_point(sim.sim_id)
    assert len(sim.power_plan.plan) == 1
    assert view.shown_sim is sim


def test_delete_power_point(ctrl):
    c, storage, view = ctrl
    c.add_sim_btn_press()
    sim = storage.sims[0]
    c.add_power_point(sim.sim_id)
    c.delete_power_point(sim.sim_id, 0)
    assert len(sim.power_plan.plan) == 0


def test_swap_power_points(ctrl):
    c, storage, view = ctrl
    c.add_sim_btn_press()
    sim = storage.sims[0]
    c.add_power_point(sim.sim_id)
    c.add_power_point(sim.sim_id)
    sim.power_plan.update_point(0, power=200, duration=10)
    sim.power_plan.update_point(1, power=300, duration=20)
    c.swap_power_points(sim.sim_id, 0, 1)
    assert sim.power_plan.plan[0].power == 300
    assert sim.power_plan.plan[1].power == 200


# ------ Environment flow ------

def test_delete_envir(ctrl):
    c, storage, view = ctrl
    c.add_envir_btn_press()
    envir = storage.envirs[0]
    c.delete_envir_btn_press(envir.envir_id)
    assert len(storage.envirs) == 0
    assert view.envir_list == []


# ------ Simulation flow ------

def test_delete_sim(ctrl):
    c, storage, view = ctrl
    c.add_sim_btn_press()
    sim = storage.sims[0]
    c.delete_sim_btn_press(sim.sim_id)
    assert len(storage.sims) == 0
    assert view.sim_list == []


def test_run_sim_missing_envir(ctrl):
    c, storage, view = ctrl
    rider = storage.add_rider(first_name="Dave", weight_kg=80, cda=0.25)
    c.add_sim_btn_press()
    sim = storage.sims[0]
    sim.rider_id = rider.rider_id  # rider assigned but no envir
    sim.power_plan.add_point()
    c.run_sim_btn_press(sim.sim_id)
    assert view.last_error is not None


def test_run_sim_no_power_plan(ctrl):
    c, storage, view = ctrl
    rider = storage.add_rider(first_name="Dave", weight_kg=80, cda=0.25)
    envir = storage.add_environment(name="COS", air_density=1.2, crr=0.004, mech_losses=0.02)
    c.add_sim_btn_press()
    sim = storage.sims[0]
    sim.rider_id = rider.rider_id
    sim.envir_id = envir.envir_id
    # power_plan is empty by default
    c.run_sim_btn_press(sim.sim_id)
    assert view.last_error is not None


def test_run_sim_incomplete_rider_fields(ctrl):
    c, storage, view = ctrl
    rider = storage.add_rider(first_name="Dave")  # cda and weight_kg are None
    envir = storage.add_environment(name="COS", air_density=1.2, crr=0.004, mech_losses=0.02)
    c.add_sim_btn_press()
    sim = storage.sims[0]
    sim.rider_id = rider.rider_id
    sim.envir_id = envir.envir_id
    sim.power_plan.add_point()
    c.run_sim_btn_press(sim.sim_id)
    assert view.last_error is not None


def test_run_sim_success(ctrl):
    c, storage, view = ctrl
    rider = storage.add_rider(first_name="Dave", weight_kg=80, cda=0.25)
    envir = storage.add_environment(name="COS", air_density=1.2, crr=0.004, mech_losses=0.02)
    c.add_sim_btn_press()
    sim = storage.sims[0]
    sim.rider_id = rider.rider_id
    sim.envir_id = envir.envir_id
    # High opening effort followed by steady power -- known to complete 4000m in time
    sim.power_plan = PowerPlan([(0, 500, 1), (1, 988, 14), (15, 550, 20), (35, 458, 100), (135, 523, 120)])
    c.run_sim_btn_press(sim.sim_id)
    assert view.last_error is None
    assert view.sim_window_shown is True


def test_run_sim_success_with_corner_physics(ctrl):
    c, storage, view = ctrl
    rider = storage.add_rider(first_name="Dave", weight_kg=80, cda=0.25, com_height_m=0.7)
    envir = storage.add_environment(name="Velodrome", air_density=1.2, crr=0.004,
                                    mech_losses=0.02, track_length=250.0, corners=0.6)
    c.add_sim_btn_press()
    sim = storage.sims[0]
    sim.rider_id = rider.rider_id
    sim.envir_id = envir.envir_id
    sim.power_plan = PowerPlan([(0, 500, 1), (1, 988, 14), (15, 550, 20), (35, 458, 100), (135, 523, 120)])
    c.run_sim_btn_press(sim.sim_id)
    assert view.last_error is None
    assert view.sim_window_shown is True


def test_run_sim_track_geometry_without_com_height_still_runs(ctrl):
    c, storage, view = ctrl
    rider = storage.add_rider(first_name="Dave", weight_kg=80, cda=0.25)  # no com_height_m
    envir = storage.add_environment(name="Velodrome", air_density=1.2, crr=0.004,
                                    mech_losses=0.02, track_length=250.0, corners=0.6)
    c.add_sim_btn_press()
    sim = storage.sims[0]
    sim.rider_id = rider.rider_id
    sim.envir_id = envir.envir_id
    sim.power_plan = PowerPlan([(0, 500, 1), (1, 988, 14), (15, 550, 20), (35, 458, 100), (135, 523, 120)])
    c.run_sim_btn_press(sim.sim_id)
    assert view.last_error is None
    assert view.sim_window_shown is True


# ------ Aero test flow ------

def test_add_aero_test(ctrl):
    c, storage, view = ctrl
    c.add_aero_test_btn_press()
    assert len(storage.aero_tests) == 1
    assert view.shown_aero_test is not None


def test_save_aero_test_valid(ctrl):
    c, storage, view = ctrl
    c.add_aero_test_btn_press()
    test = storage.aero_tests[0]
    c.save_aero_test_btn_press(test.aero_test_id, name="Test 1")
    assert test.name == "Test 1"
    assert view.last_success == "Aero Test saved"


def test_delete_aero_test(ctrl):
    c, storage, view = ctrl
    c.add_aero_test_btn_press()
    test = storage.aero_tests[0]
    c.delete_aero_test_btn_press(test.aero_test_id)
    assert len(storage.aero_tests) == 0


def test_calc_aero_test_no_file_shows_error(ctrl):
    c, storage, view = ctrl
    c.add_aero_test_btn_press()
    test = storage.aero_tests[0]
    c.calc_aero_test_btn_press(test.aero_test_id)
    assert view.last_error is not None
    assert view.aero_test_window_shown is False


def test_calc_aero_test_bad_file_shows_error(ctrl):
    c, storage, view = ctrl
    c.add_aero_test_btn_press()
    test = storage.aero_tests[0]
    test.data_file = '/nonexistent/file.fit'
    c.calc_aero_test_btn_press(test.aero_test_id)
    assert view.last_error is not None
    assert view.aero_test_window_shown is False


def test_calc_aero_test_success_opens_window(ctrl, monkeypatch):
    c, storage, view = ctrl
    c.add_aero_test_btn_press()
    test = storage.aero_tests[0]
    test.data_file = '/fake.fit'

    fake_fit = {
        'elapsed_time': np.array([0.0, 1.0, 2.0]),
        'speed': np.array([10.0, 11.0, 12.0]),
        'power': np.array([250.0, 260.0, 270.0]),
    }
    monkeypatch.setattr('controller.read_fit_file_data', lambda p: fake_fit)

    c.calc_aero_test_btn_press(test.aero_test_id)

    assert view.last_error is None
    assert view.aero_test_window_shown is True
    aero_test_id, aero_test, fit_data = view.aero_test_window_args
    assert aero_test_id == test.aero_test_id
    assert fit_data is fake_fit


def test_calc_aero_test_missing_elapsed_time_shows_error(ctrl, monkeypatch):
    c, storage, view = ctrl
    c.add_aero_test_btn_press()
    test = storage.aero_tests[0]
    test.data_file = '/fake.fit'

    # fit data with no elapsed_time key (e.g. no session frame in file)
    monkeypatch.setattr('controller.read_fit_file_data',
                        lambda p: {'speed': np.array([10.0])})

    c.calc_aero_test_btn_press(test.aero_test_id)

    assert view.last_error is not None
    assert view.aero_test_window_shown is False


def test_save_aero_test_selection_adds_to_model(ctrl):
    c, storage, view = ctrl
    c.add_aero_test_btn_press()
    test = storage.aero_tests[0]

    c.save_aero_test_selection(test.aero_test_id, "Lap 1", 10.0, 70.0,
                                duration=60.0, avg_power=280.0)

    assert len(test.selections) == 1
    assert test.selections[0].name == "Lap 1"
    assert test.selections[0].start_time == 10.0
    assert test.selections[0].avg_power == 280.0


def test_save_aero_test_selection_refreshes_open_window(ctrl):
    c, storage, view = ctrl
    c.add_aero_test_btn_press()
    test = storage.aero_tests[0]

    stub_window = StubAeroTestWindow()
    view.aero_test_windows[test.aero_test_id] = stub_window

    c.save_aero_test_selection(test.aero_test_id, "Lap 1", 10.0, 70.0)

    assert stub_window.refreshed_selections is test.selections


def test_save_aero_test_selection_no_window_no_error(ctrl):
    c, storage, view = ctrl
    c.add_aero_test_btn_press()
    test = storage.aero_tests[0]
    # No window in aero_test_windows -- should complete without raising
    c.save_aero_test_selection(test.aero_test_id, "Lap 1", 10.0, 70.0)
    assert len(test.selections) == 1


def test_delete_aero_test_selection_removes_from_model(ctrl):
    c, storage, view = ctrl
    c.add_aero_test_btn_press()
    test = storage.aero_tests[0]
    sel = test.add_selection("Lap 1", 10.0, 70.0)

    c.delete_aero_test_selection(test.aero_test_id, sel.selection_id)

    assert len(test.selections) == 0


def test_delete_aero_test_selection_refreshes_open_window(ctrl):
    c, storage, view = ctrl
    c.add_aero_test_btn_press()
    test = storage.aero_tests[0]
    sel = test.add_selection("Lap 1", 10.0, 70.0)

    stub_window = StubAeroTestWindow()
    view.aero_test_windows[test.aero_test_id] = stub_window

    c.delete_aero_test_selection(test.aero_test_id, sel.selection_id)

    assert stub_window.refreshed_selections is test.selections
    assert len(stub_window.refreshed_selections) == 0

