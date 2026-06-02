import pytest
from calcs import IPCalculator


SAMPLE_ATTRS = dict(
    cda=0.195,
    air_density=1.12,
    mass_kg=100.0,
    crr=0.002,
    mech_losses=0.02,
    power_plan=[(0, 500, 1), (1, 988, 14), (15, 550, 20), (35, 458, 100), (135, 523, 120)],
    dt=0.1,
)


def test_calc_pedal_force_never_exceeds_max():
    calc = IPCalculator(**SAMPLE_ATTRS)
    for v in [0.1, 3, 10, 20]:
        for t in [0, 0.5, 1, 5, 30, 60]:
            assert calc.calc_pedal_force(v, t) <= calc.max_force


def test_solve_produces_outputs():
    calc = IPCalculator(**SAMPLE_ATTRS)
    calc.solve()
    assert len(calc.time) > 0
    assert len(calc.velocity) == len(calc.time)
    assert len(calc.position) == len(calc.time)
    assert calc.position[-1] >= calc.race_distance


def test_get_results_keys():
    calc = IPCalculator(**SAMPLE_ATTRS)
    calc.solve()
    results = calc.get_results()
    assert set(results.keys()) == {"time", "power", "velocity", "splits", "split_table"}


def test_get_results_lengths_match():
    calc = IPCalculator(**SAMPLE_ATTRS)
    calc.solve()
    results = calc.get_results()
    assert len(results["time"]) == len(results["power"])
    assert len(results["time"]) == len(results["velocity"])


def test_split_table_has_header():
    calc = IPCalculator(**SAMPLE_ATTRS)
    calc.solve()
    results = calc.get_results()
    assert results["split_table"][0] == ["Distance (m)", "Half Lap Splits", "Total Time"]


def test_get_power_from_plan():
    calc = IPCalculator(**SAMPLE_ATTRS)
    # First segment starts at t=0 (power=500), second at t=1 (power=988)
    assert calc.get_power_from_plan(0) == 500
    assert calc.get_power_from_plan(0.5) == 500
    assert calc.get_power_from_plan(1) == 988
    # Last segment (t>=135) returns last power
    assert calc.get_power_from_plan(200) == 523


def test_split_table_row_count():
    calc = IPCalculator(**SAMPLE_ATTRS)
    calc.solve()
    results = calc.get_results()
    # 4000m / 125m interval = 32 half-laps + 1 header row
    assert len(results["split_table"]) == 33


def test_velocity_output_is_kph():
    calc = IPCalculator(**SAMPLE_ATTRS)
    calc.solve()
    results = calc.get_results()
    # Peak TT speed should be 40–70 kph; raw m/s would be ~11–19, confirming the conversion
    assert 40 < max(results["velocity"]) < 100


# ------ CdACalculator (no .fit file needed) ------

def test_cda_set_range_valid():
    from calcs import CdACalculator
    calc = CdACalculator("/fake/path", 1.2, 80, 0.004, 0.02)
    calc._max_index = 100
    calc.start_index = 0
    calc.end_index = 100
    calc.set_range(10, 90)
    assert calc.start_index == 10
    assert calc.end_index == 90


def test_cda_set_range_invalid():
    from calcs import CdACalculator
    import pytest
    calc = CdACalculator("/fake/path", 1.2, 80, 0.004, 0.02)
    calc._max_index = 100
    calc.start_index = 0
    calc.end_index = 100
    with pytest.raises(ValueError):
        calc.set_range(90, 10)  # start > end


def test_cda_calc_cda_constant_velocity():
    from calcs import CdACalculator
    import numpy as np
    calc = CdACalculator("/fake/path", air_density=1.2, mass_kg=80, crr=0.004, mech_losses=0.02)
    v = np.full(10, 10.0)   # constant 10 m/s → zero acceleration term
    t = np.arange(10, dtype=float)
    p = np.full(10, 300.0)
    result = calc.calc_cda(t, v, p)
    # f_power = 300/10 * 0.98 = 29.4; f_rolling = -80*9.80665*0.004 ≈ -3.14
    # cda = 2 / (1.2 * 100) * (29.4 - 3.14) ≈ 0.438
    assert abs(result - 0.438) < 0.01


def test_norm_power():
    from calcs import CdACalculator
    import numpy as np
    calc = CdACalculator("/fake/path", 1.2, 80, 0.004, 0.02)
    p = np.array([200.0, 300.0, 400.0, 500.0])
    expected = float(np.mean(p ** 4) ** 0.25)
    assert abs(calc.get_norm_power(p) - expected) < 0.001


@pytest.mark.skip(reason="requires local .fit file outside repo")
def test_cda_calculator():
    from calcs import CdACalculator
    calc = CdACalculator("/path/to/activity.fit", 0, 0, 0, 0)
    calc.read_fit_file()
