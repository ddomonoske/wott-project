import pytest
from model.entities import Rider, Environment, Simulation, AeroTest, PowerPlan, PowerPlanPoint
from model.storage import Storage


# ------ Rider ------

def test_rider_valid_attributes(sample_rider):
    assert sample_rider.first_name == "David"
    assert sample_rider.weight_kg == 89.0
    assert sample_rider.name == "David Domonoske"


def test_rider_update_valid(sample_rider):
    sample_rider.update(first_name="Anders", ftp="450")
    assert sample_rider.first_name == "Anders"
    assert sample_rider.ftp == 450.0


def test_rider_update_invalid_field(sample_rider):
    with pytest.raises(AttributeError):
        sample_rider.update(invalid_field="x")


def test_rider_update_invalid_float(sample_rider):
    with pytest.raises(TypeError):
        sample_rider.update(ftp="not_a_number")


def test_rider_update_requires_name(sample_rider):
    with pytest.raises(AttributeError):
        sample_rider.update(first_name="", last_name="")


def test_rider_update_empty_float_becomes_none(sample_rider):
    sample_rider.update(ftp="")
    assert sample_rider.ftp is None


def test_rider_name_property():
    r = Rider(rider_id=0, first_name="", last_name="Smith")
    assert r.name == "Smith"


# ------ Environment ------

def test_envir_valid_attributes(sample_envir):
    assert sample_envir.name == "COS"
    assert sample_envir.air_density == 0.995


def test_envir_update_valid(sample_envir):
    sample_envir.update(name="LA", air_density="1.20")
    assert sample_envir.name == "LA"
    assert sample_envir.air_density == 1.20


def test_envir_update_requires_name(sample_envir):
    with pytest.raises(AttributeError):
        sample_envir.update(name="")


def test_envir_update_invalid_float(sample_envir):
    with pytest.raises(TypeError):
        sample_envir.update(crr="bad")


# ------ Simulation ------

def test_sim_valid_attributes(sample_sim):
    assert sample_sim.name == "David in COS"
    assert sample_sim.rider_id == 0
    assert sample_sim.envir_id == 0


def test_sim_update_name(sample_sim):
    sample_sim.update(name="Updated Sim")
    assert sample_sim.name == "Updated Sim"


def test_sim_update_requires_name(sample_sim):
    with pytest.raises(AttributeError):
        sample_sim.update(name="")


# ------ AeroTest ------

def test_aero_test_valid(sample_aero_test):
    assert sample_aero_test.name == "Dave LA Test 1"
    assert sample_aero_test.data_file is None


def test_aero_test_update(sample_aero_test):
    sample_aero_test.update(name="Test 2")
    assert sample_aero_test.name == "Test 2"


def test_aero_test_update_requires_name(sample_aero_test):
    with pytest.raises(AttributeError):
        sample_aero_test.update(name="")


def test_aero_test_update_invalid_field(sample_aero_test):
    with pytest.raises(AttributeError):
        sample_aero_test.update(invalid_field="x")


def test_envir_update_invalid_field(sample_envir):
    with pytest.raises(AttributeError):
        sample_envir.update(invalid_field="x")


def test_sim_update_invalid_field(sample_sim):
    with pytest.raises(AttributeError):
        sample_sim.update(invalid_field="x")


# ------ PowerPlan ------

def test_power_plan_from_list(sample_power_plan):
    assert len(sample_power_plan.plan) == 5
    assert sample_power_plan.plan[0].start == 0
    assert sample_power_plan.plan[1].start == 1


def test_power_plan_add_point(sample_power_plan):
    n = len(sample_power_plan.plan)
    sample_power_plan.add_point()
    assert len(sample_power_plan.plan) == n + 1


def test_power_plan_update_point(sample_power_plan):
    sample_power_plan.update_point(0, power=600, duration=5)
    assert sample_power_plan.plan[0].power == 600
    assert sample_power_plan.plan[1].start == 5


def test_power_plan_delete_point(sample_power_plan):
    n = len(sample_power_plan.plan)
    sample_power_plan.delete_point(0)
    assert len(sample_power_plan.plan) == n - 1


def test_power_plan_swap_points(sample_power_plan):
    p0_power = sample_power_plan.plan[0].power
    p1_power = sample_power_plan.plan[1].power
    sample_power_plan.swap_points(0, 1)
    assert sample_power_plan.plan[0].power == p1_power
    assert sample_power_plan.plan[1].power == p0_power


def test_power_plan_as_tuple_list(sample_power_plan):
    tuples = sample_power_plan.as_tuple_list()
    assert isinstance(tuples, list)
    assert all(len(t) == 3 for t in tuples)


# ------ Storage ------

def test_storage_add_get_rider(tmp_storage):
    rider = tmp_storage.add_rider(first_name="David")
    assert tmp_storage.get_rider(rider.rider_id) is rider


def test_storage_delete_rider(tmp_storage):
    rider = tmp_storage.add_rider(first_name="David")
    tmp_storage.delete_rider(rider.rider_id)
    assert tmp_storage.get_rider(rider.rider_id) is None


def test_storage_add_get_envir(tmp_storage):
    envir = tmp_storage.add_environment(name="COS")
    assert tmp_storage.get_envir(envir.envir_id) is envir


def test_storage_delete_envir(tmp_storage):
    envir = tmp_storage.add_environment(name="COS")
    tmp_storage.delete_environment(envir.envir_id)
    assert tmp_storage.get_envir(envir.envir_id) is None


def test_storage_add_get_sim(tmp_storage):
    sim = tmp_storage.add_simulation(name="Test Sim")
    assert tmp_storage.get_sim(sim.sim_id) is sim


def test_storage_delete_sim(tmp_storage):
    sim = tmp_storage.add_simulation(name="Test Sim")
    tmp_storage.delete_simulation(sim.sim_id)
    assert tmp_storage.get_sim(sim.sim_id) is None


def test_storage_add_get_aero_test(tmp_storage):
    test = tmp_storage.add_aero_test(name="Test")
    assert tmp_storage.get_aero_test(test.aero_test_id) is test


def test_storage_delete_aero_test(tmp_storage):
    test = tmp_storage.add_aero_test(name="Test")
    tmp_storage.delete_aero_test(test.aero_test_id)
    assert tmp_storage.get_aero_test(test.aero_test_id) is None


def test_storage_get_envir_name_ids(tmp_storage):
    tmp_storage.add_environment(name="COS")
    name_ids = tmp_storage.get_envir_name_ids()
    assert len(name_ids) == 1
    assert name_ids[0][0] == "COS"


def test_storage_get_sim_name_ids(tmp_storage):
    tmp_storage.add_simulation(name="Test Sim")
    name_ids = tmp_storage.get_sim_name_ids()
    assert len(name_ids) == 1
    assert name_ids[0][0] == "Test Sim"


def test_storage_get_aero_test_name_ids(tmp_storage):
    tmp_storage.add_aero_test(name="My Test")
    name_ids = tmp_storage.get_aero_test_name_ids()
    assert len(name_ids) == 1
    assert name_ids[0][0] == "My Test"


def test_storage_ids_increment(tmp_storage):
    r1 = tmp_storage.add_rider(first_name="A")
    r2 = tmp_storage.add_rider(first_name="B")
    assert r2.rider_id == r1.rider_id + 1


def test_storage_save_load_round_trip(tmp_storage, tmp_path):
    tmp_storage.add_rider(first_name="David", last_name="D")
    tmp_storage.add_environment(name="COS")
    tmp_storage.save()

    loaded = Storage(storage_dir=str(tmp_path))
    assert len(loaded.riders) == 1
    assert loaded.riders[0].first_name == "David"
    assert len(loaded.envirs) == 1
    assert loaded.envirs[0].name == "COS"


def test_storage_meta_persists(tmp_storage, tmp_path):
    tmp_storage.add_rider(first_name="A")
    tmp_storage.add_rider(first_name="B")
    tmp_storage.save()

    loaded = Storage(storage_dir=str(tmp_path))
    r = loaded.add_rider(first_name="C")
    assert r.rider_id == 2
