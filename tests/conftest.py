import pytest
from model.entities import Rider, Environment, Simulation, AeroTest, PowerPlan
from model.storage import Storage


@pytest.fixture
def sample_rider():
    return Rider(
        rider_id=0,
        first_name="David",
        last_name="Domonoske",
        weight_kg=89.0,
        ftp=418.0,
        w_prime=28.0,
        cda=0.195,
    )


@pytest.fixture
def sample_envir():
    return Environment(
        envir_id=0,
        name="COS",
        air_density=0.995,
        crr=0.002,
        mech_losses=0.01,
    )


@pytest.fixture
def sample_power_plan():
    return PowerPlan([
        (0, 500, 1),
        (1, 988, 14),
        (15, 550, 20),
        (35, 458, 100),
        (135, 523, 120),
    ])


@pytest.fixture
def sample_sim(sample_power_plan):
    return Simulation(
        sim_id=0,
        name="David in COS",
        rider_id=0,
        envir_id=0,
        power_plan=sample_power_plan,
    )


@pytest.fixture
def sample_aero_test():
    return AeroTest(
        aero_test_id=0,
        name="Dave LA Test 1",
        rider_id=0,
        envir_id=0,
    )


@pytest.fixture
def tmp_storage(tmp_path):
    return Storage(storage_dir=str(tmp_path))
