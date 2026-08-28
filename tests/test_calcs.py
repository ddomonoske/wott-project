import datetime
import math
import types
import pytest
import numpy as np
import fitdecode
from calcs import IPCalculator, CdAFitter, read_fit_file_data


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
    assert set(results.keys()) == {"time", "power", "velocity", "splits", "split_table", "csv_data"}


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


def test_solve_raises_when_race_distance_not_reached():
    # t_max=1 is nowhere near enough time to cover the 4000m race_distance.
    calc = IPCalculator(**SAMPLE_ATTRS)
    with pytest.raises(ValueError, match="did not reach race_distance"):
        calc.solve(t_max=1)


def test_get_lap_splits_raises_when_split_distance_not_reached():
    calc = IPCalculator(**SAMPLE_ATTRS)
    calc.solve()
    # Ask for splits well beyond the distance actually covered.
    with pytest.raises(ValueError, match="did not reach split distance"):
        calc.get_lap_splits(interval=125, distance=calc.position[-1] + 10000)


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
    # Peak TT speed should be 40-70 kph; raw m/s would be ~11-19, confirming the conversion
    assert 40 < max(results["velocity"]) < 100


# ------ CSV export resampling ------

def test_csv_export_data_one_second_spacing():
    calc = IPCalculator(**SAMPLE_ATTRS)
    calc.solve()
    csv_data = calc.get_csv_export_data()
    diffs = np.diff(csv_data["time"])
    assert np.allclose(diffs, 1.0)


def test_csv_export_data_spans_full_duration():
    calc = IPCalculator(**SAMPLE_ATTRS)
    calc.solve()
    csv_data = calc.get_csv_export_data()
    assert csv_data["time"][0] == 0.0
    # Last row's interval should reach the end of the simulation, possibly
    # via a shorter final bin if the run doesn't end on a whole second.
    last_width = calc.time[-1] - csv_data["time"][-1]
    assert 0 < last_width <= 1.0
    assert len(csv_data["time"]) == len(csv_data["velocity"]) == len(csv_data["power"])


def test_csv_export_data_preserves_area_under_curve():
    # Bin-averaging (integral / width) must reproduce the same total area
    # (energy, distance) as the full-resolution curve, not just look similar.
    calc = IPCalculator(**SAMPLE_ATTRS)
    calc.solve()
    csv_data = calc.get_csv_export_data()

    widths = np.diff(np.append(csv_data["time"], calc.time[-1]))
    resampled_power_area = np.sum(np.array(csv_data["power"]) * widths)
    full_res_power_area = np.trapz(calc.power, calc.time)
    assert resampled_power_area == pytest.approx(full_res_power_area, rel=1e-6)

    velocity_kph = 3600 / 1000 * calc.velocity
    resampled_velocity_area = np.sum(np.array(csv_data["velocity"]) * widths)
    full_res_velocity_area = np.trapz(velocity_kph, calc.time)
    assert resampled_velocity_area == pytest.approx(full_res_velocity_area, rel=1e-6)


# ------ Corner-lean physics helpers ------

def test_lean_angle_zero_on_straight():
    assert IPCalculator._lean_angle(v=15.0, kappa=0.0) == 0.0


def test_lean_angle_zero_at_v_zero():
    assert IPCalculator._lean_angle(v=0.0, kappa=1.0 / 20.0) == 0.0


def test_lean_angle_matches_formula():
    v, kappa = 12.0, 1.0 / 25.0
    expected = math.atan(v ** 2 * kappa / IPCalculator.GRAVITY)
    assert IPCalculator._lean_angle(v, kappa) == pytest.approx(expected)


def test_wheel_speed_coning_example():
    # User's worked example: 20m corner radius, CoM inset 10m -> wheel speed = 2x CoM speed.
    # kappa=1/20, and h*sin(theta)=10 (e.g. theta=pi/2, com_height_m=10) gives that inset.
    v_com = 5.0
    v_wheel = IPCalculator._wheel_speed(v=v_com, kappa=1.0 / 20.0, theta=math.pi / 2,
                                         com_height_m=10.0)
    assert v_wheel == pytest.approx(2 * v_com)


def test_wheel_speed_no_op_without_com_height():
    assert IPCalculator._wheel_speed(v=8.0, kappa=1.0 / 20.0, theta=0.3, com_height_m=None) == 8.0


def test_wheel_speed_no_op_on_straight():
    assert IPCalculator._wheel_speed(v=8.0, kappa=0.0, theta=0.0, com_height_m=1.0) == 8.0


def test_energy_accel_zero_without_com_height():
    assert IPCalculator._energy_accel(v=10.0, com_height_m=None, theta=0.3,
                                       dtheta_ds=0.01, v_wheel=10.0) == 0.0


def test_energy_accel_zero_near_v_zero():
    assert IPCalculator._energy_accel(v=0.01, com_height_m=0.7, theta=0.3,
                                       dtheta_ds=0.01, v_wheel=0.01) == 0.0


def test_energy_accel_symmetric_entering_and_exiting_corner():
    kwargs = dict(v=10.0, com_height_m=0.7, theta=0.3, v_wheel=10.0)
    entering = IPCalculator._energy_accel(dtheta_ds=0.02, **kwargs)
    exiting = IPCalculator._energy_accel(dtheta_ds=-0.02, **kwargs)
    assert entering > 0
    assert exiting == pytest.approx(-entering)


def test_banked_rolling_resistance_matches_plain_formula_at_zero_lean():
    result = IPCalculator._banked_rolling_resistance(mass_kg=100.0, crr=0.002, theta=0.0)
    assert result == pytest.approx(-IPCalculator.GRAVITY * 100.0 * 0.002)


def test_banked_rolling_resistance_scales_by_one_over_cos():
    base = IPCalculator._banked_rolling_resistance(mass_kg=100.0, crr=0.002, theta=0.0)
    leaned = IPCalculator._banked_rolling_resistance(mass_kg=100.0, crr=0.002, theta=0.4)
    assert leaned == pytest.approx(base / math.cos(0.4))


def test_energy_feedback_coeff_zero_without_com_height():
    assert IPCalculator._energy_feedback_coeff(v=10.0, kappa=0.05, theta=0.3, com_height_m=None) == 0.0


def test_energy_feedback_coeff_zero_on_straight():
    assert IPCalculator._energy_feedback_coeff(v=10.0, kappa=0.0, theta=0.0, com_height_m=1.0) == 0.0


def test_energy_feedback_coeff_matches_formula():
    v, kappa, theta, h = 12.0, 1.0 / 25.0, 0.5, 0.8
    x = v ** 2 * kappa / IPCalculator.GRAVITY
    expected = (2.0 * h * kappa * math.sin(theta)) / (1.0 + x ** 2)
    assert IPCalculator._energy_feedback_coeff(v, kappa, theta, h) == pytest.approx(expected)


def test_dtheta_dv_zero_on_straight():
    assert IPCalculator._dtheta_dv(v=15.0, kappa=0.0) == 0.0


def test_dtheta_dv_matches_formula():
    v, kappa = 12.0, 1.0 / 25.0
    x = v ** 2 * kappa / IPCalculator.GRAVITY
    expected = (1.0 / (1.0 + x ** 2)) * (2.0 * v * kappa / IPCalculator.GRAVITY)
    assert IPCalculator._dtheta_dv(v, kappa) == pytest.approx(expected)


def test_dtheta_dv_consistent_with_energy_feedback_coeff():
    # _energy_feedback_coeff is the pre-solved implicit-feedback form of the
    # same partial derivative _dtheta_dv exposes standalone (needed by the CdA
    # inverse fit below, which has a known dv/dt and so doesn't need the
    # implicit solve forward integration requires). They must agree:
    # energy_feedback_coeff == (g*h*sin(theta)/v) * dtheta_dv.
    v, kappa, theta, h = 12.0, 1.0 / 25.0, 0.5, 0.8
    coeff = IPCalculator._energy_feedback_coeff(v, kappa, theta, h)
    expected = (IPCalculator.GRAVITY * h * math.sin(theta) / v) * IPCalculator._dtheta_dv(v, kappa)
    assert coeff == pytest.approx(expected)


# ------ Corner-lean physics integration (via solve()) ------

def test_solve_no_op_without_track_geometry():
    # No track_length/corners/com_height_m -- must behave exactly like a flat, straight sim.
    calc = IPCalculator(**SAMPLE_ATTRS)
    calc.solve()
    assert calc._has_track is False


def test_solve_corner_energy_does_not_compound_over_many_laps():
    # Regression test: dropping theta's dependence on v from the corner energy
    # term (using only dtheta/ds, not the full dtheta/dt) silently leaks energy
    # into the system every corner. Undetectable in a single short sim -- lean
    # angle and speed compounded upward lap after lap over a long race instead
    # of settling into a bounded oscillation.
    calc = IPCalculator(**SAMPLE_ATTRS, track_length=250.0, corners=0.6,
                         com_height_m=1.0, race_distance=8000)
    calc.solve(t_max=600)
    lap_len = 250.0
    n_laps = int(calc.position[-1] // lap_len)

    def lap_max_lean_deg(lap):
        mask = (calc.position >= lap * lap_len) & (calc.position < (lap + 1) * lap_len)
        v = calc.velocity[mask]
        kappa = np.array([calc._kappa_at(s) for s in calc.position[mask]])
        theta = [IPCalculator._lean_angle(vv, kk) for vv, kk in zip(v, kappa)]
        return np.degrees(max(theta))

    early = lap_max_lean_deg(10)
    late = lap_max_lean_deg(n_laps - 1)
    assert late < early + 15


def test_solve_matches_finer_reference_near_corners():
    # Regression test: without a max_step cap, RK45's adaptive step size (chosen
    # from the smooth power/drag dynamics) can grow to multiple seconds and skip
    # clean over a corner's ~1s curvature transition zone, producing dense-output
    # values with no real connection to what happened in the corner -- this
    # produced large, smoothly-wrong excursions unrelated to the track geometry.
    # Guard against regressing by comparing against an independently
    # finer-integrated reference solution.
    kwargs = dict(cda=0.195, air_density=1.12, mass_kg=100.0, crr=0.002, mech_losses=0.02,
                  power_plan=[(0, 500, 300)], dt=0.1, track_length=250.0, corners=0.6,
                  com_height_m=1.0, race_distance=2000)
    calc = IPCalculator(**kwargs)
    calc.solve(t_max=150)

    reference = IPCalculator(**{**kwargs, 'dt': 0.02})
    reference.solve(t_max=150)

    ref_v_interp = np.interp(calc.time, reference.time, reference.velocity)
    assert np.max(np.abs(calc.velocity - ref_v_interp)) < 0.5


def test_solve_with_track_and_com_height_produces_lean():
    calc = IPCalculator(**SAMPLE_ATTRS, track_length=100.0, corners=0.8,
                         com_height_m=0.7, race_distance=1000)
    calc.solve()
    assert np.all(np.diff(calc.position) >= 0)  # monotonic wheel distance
    thetas = [IPCalculator._lean_angle(v, calc._kappa_at(s))
              for v, s in zip(calc.velocity, calc.position)]
    assert max(thetas) > 0


def test_solve_with_track_no_com_height_still_runs():
    # Track geometry present but no com_height_m -- banked Crr still applies,
    # but CoM-offset/energy terms are no-ops.
    calc = IPCalculator(**SAMPLE_ATTRS, track_length=100.0, corners=0.8, race_distance=1000)
    calc.solve()
    assert len(calc.velocity) == len(calc.position)


# ------ CdAFitter ------

def test_cda_fitter_matches_known_value_constant_velocity():
    # No track geometry, constant velocity -- degenerates to the same
    # power-balance inversion the old average-based calculator used, and
    # should reproduce the same known answer.
    fitter = CdAFitter(air_density=1.2, mass_kg=80, crr=0.004, mech_losses=0.02)
    t = np.arange(20, dtype=float)
    v = np.full(20, 10.0)
    p = np.full(20, 300.0)
    result = fitter.fit(t, v, p)
    # f_power = 300/10 * 0.98 = 29.4; f_rolling = -80*9.80665*0.004 ~= -3.14
    # cda = (29.4 - 3.14) / (0.5*1.2*100) ~= 0.438
    assert result["cda"] == pytest.approx(0.438, abs=0.01)
    assert result["s0"] is None


def test_cda_fitter_no_track_geometry_still_fits():
    fitter = CdAFitter(air_density=1.2, mass_kg=80, crr=0.004, mech_losses=0.02)
    t = np.arange(20, dtype=float)
    v = np.linspace(9.0, 11.0, 20)
    p = np.linspace(280.0, 320.0, 20)
    result = fitter.fit(t, v, p)
    assert result["s0"] is None
    assert result["cda"] > 0


def test_cda_fitter_insufficient_moving_samples_raises():
    fitter = CdAFitter(air_density=1.2, mass_kg=80, crr=0.004, mech_losses=0.02)
    t = np.arange(5, dtype=float)
    v = np.zeros(5)  # all below V_EPS
    p = np.zeros(5)
    with pytest.raises(ValueError):
        fitter.fit(t, v, p)


def test_cda_fitter_s0_periodicity():
    # Regression test: TrackShape's symmetric two-straight/two-corner
    # construction makes kappa(s) periodic with period track_length/2, not
    # track_length, so the s0 search only needs to cover the half-period.
    # Guard against someone "fixing" the search range back to the full
    # track_length under a mistaken belief it's under-searching.
    fitter = CdAFitter(air_density=1.2, mass_kg=80, crr=0.004, mech_losses=0.02,
                        com_height_m=0.7, track_length=250.0, corners=0.6)
    rng = np.random.default_rng(0)
    v = rng.uniform(8.0, 14.0, 60)
    p = rng.uniform(200.0, 400.0, 60)
    dv_dt = np.gradient(v, np.arange(60, dtype=float))
    dist = np.cumsum(v)
    s0 = 37.5

    cda_a, residual_a = fitter._cda_for_s0(s0, v, p, dv_dt, dist)
    cda_b, residual_b = fitter._cda_for_s0(s0 + fitter.track_length / 2, v, p, dv_dt, dist)

    assert cda_a == pytest.approx(cda_b)
    assert residual_a == pytest.approx(residual_b)


def test_cda_fitter_round_trip_recovers_known_cda_on_cornered_track():
    # Strongest check: drive the forward simulator with a KNOWN cda on a
    # cornered track, resample to 1Hz like a real FIT file, and confirm the
    # inverse fit recovers that same cda from the resulting speed/power trace.
    known_cda = 0.195
    kwargs = dict(cda=known_cda, air_density=1.12, mass_kg=100.0, crr=0.002, mech_losses=0.02,
                  power_plan=[(0, 500, 300)], dt=0.1, track_length=250.0, corners=0.6,
                  com_height_m=0.7, race_distance=2000)
    calc = IPCalculator(**kwargs)
    calc.solve(t_max=150)
    csv_data = calc.get_csv_export_data(dt=1.0)

    t = np.array(csv_data["time"])
    v = np.array(csv_data["velocity"]) / 3.6  # kph -> m/s, matching FIT 'speed' units
    p = np.array(csv_data["power"])

    fitter = CdAFitter(air_density=1.12, mass_kg=100.0, crr=0.002, mech_losses=0.02,
                        com_height_m=0.7, track_length=250.0, corners=0.6)
    result = fitter.fit(t, v, p)

    assert result["cda"] == pytest.approx(known_cda, rel=0.03)
    assert result["s0"] is not None


def test_cda_fitter_round_trip_recovers_known_cda_no_com_height():
    # Track geometry present but no com_height_m -- banked Crr still applies
    # but the energy term is a no-op; recovery should still work.
    known_cda = 0.22
    kwargs = dict(cda=known_cda, air_density=1.12, mass_kg=90.0, crr=0.003, mech_losses=0.02,
                  power_plan=[(0, 450, 300)], dt=0.1, track_length=250.0, corners=0.6,
                  race_distance=2000)
    calc = IPCalculator(**kwargs)
    calc.solve(t_max=150)
    csv_data = calc.get_csv_export_data(dt=1.0)

    t = np.array(csv_data["time"])
    v = np.array(csv_data["velocity"]) / 3.6
    p = np.array(csv_data["power"])

    fitter = CdAFitter(air_density=1.12, mass_kg=90.0, crr=0.003, mech_losses=0.02,
                        track_length=250.0, corners=0.6)
    result = fitter.fit(t, v, p)

    assert result["cda"] == pytest.approx(known_cda, rel=0.03)


# ------ read_fit_file_data ------
# Helpers that build lightweight stand-ins for fitdecode frame / field objects.

_START_DT = datetime.datetime(2024, 6, 1, 8, 0, 0)


def _field(name, value):
    return types.SimpleNamespace(name=name, value=value)


def _session_frame(start_dt=_START_DT):
    f = types.SimpleNamespace(
        frame_type=fitdecode.FIT_FRAME_DATA,
        name='session',
        fields=[_field('start_time', start_dt)],
    )
    f.get_field = lambda field_name: _field(field_name, start_dt)
    return f


def _record_frame(elapsed_s, start_dt=_START_DT, **kwargs):
    fields = [_field('timestamp', start_dt + datetime.timedelta(seconds=elapsed_s))]
    for name, val in kwargs.items():
        fields.append(_field(name, val))
    return types.SimpleNamespace(
        frame_type=fitdecode.FIT_FRAME_DATA,
        name='record',
        fields=fields,
    )


class _MockFitReader:
    """Context-manager stub for fitdecode.FitReader; yields pre-built frames."""
    def __init__(self, frames):
        self._frames = frames

    def __enter__(self):
        return iter(self._frames)

    def __exit__(self, *_):
        return False


def _reader_factory(*frame_lists):
    """Returns a FitReader callable that serves each frame list in turn."""
    itr = iter(frame_lists)
    return lambda _path: _MockFitReader(next(itr))


def test_read_fit_returns_elapsed_time(monkeypatch):
    session = _session_frame()
    records = [_record_frame(0, speed=10.0), _record_frame(1, speed=11.0)]
    monkeypatch.setattr('calcs.fitdecode.FitReader', _reader_factory([session], records))

    result = read_fit_file_data('/fake.fit')

    assert 'elapsed_time' in result
    np.testing.assert_array_equal(result['elapsed_time'], [0.0, 1.0])


def test_read_fit_returns_numeric_fields(monkeypatch):
    session = _session_frame()
    records = [
        _record_frame(0, speed=10.0, power=250.0, cadence=90.0),
        _record_frame(1, speed=11.0, power=260.0, cadence=92.0),
    ]
    monkeypatch.setattr('calcs.fitdecode.FitReader', _reader_factory([session], records))

    result = read_fit_file_data('/fake.fit')

    assert set(result.keys()) == {'elapsed_time', 'speed', 'power', 'cadence'}
    np.testing.assert_array_equal(result['speed'], [10.0, 11.0])
    np.testing.assert_array_equal(result['power'], [250.0, 260.0])


def test_read_fit_excludes_raw_timestamp(monkeypatch):
    session = _session_frame()
    records = [_record_frame(0, speed=10.0)]
    monkeypatch.setattr('calcs.fitdecode.FitReader', _reader_factory([session], records))

    result = read_fit_file_data('/fake.fit')

    assert 'timestamp' not in result


def test_read_fit_missing_field_becomes_nan(monkeypatch):
    session = _session_frame()
    records = [
        _record_frame(0, speed=10.0, power=250.0),
        _record_frame(1, speed=11.0),  # no power on this record
    ]
    monkeypatch.setattr('calcs.fitdecode.FitReader', _reader_factory([session], records))

    result = read_fit_file_data('/fake.fit')

    assert result['power'][0] == 250.0
    assert np.isnan(result['power'][1])


def test_read_fit_excludes_nonnumeric_fields(monkeypatch):
    session = _session_frame()
    records = [_record_frame(0, speed=10.0, label="some_string")]
    # Override: the string field must be detected as non-numeric and dropped
    # We supply it by patching the field value directly
    rec = _record_frame(0, speed=10.0)
    rec.fields.append(_field('label', 'fast'))  # string value
    records = [rec]
    monkeypatch.setattr('calcs.fitdecode.FitReader', _reader_factory([session], records))

    result = read_fit_file_data('/fake.fit')

    assert 'label' not in result
    assert 'speed' in result


def test_read_fit_empty_records_returns_empty(monkeypatch):
    session = _session_frame()
    monkeypatch.setattr('calcs.fitdecode.FitReader', _reader_factory([session], []))

    result = read_fit_file_data('/fake.fit')

    assert result == {}


def test_read_fit_no_session_frame_still_reads_records(monkeypatch):
    # When there's no session frame, elapsed_time can't be computed --
    # the function still returns whatever numeric fields it finds.
    records = [_record_frame(0, speed=10.0)]
    # Both FitReader calls return only record frames (no session)
    monkeypatch.setattr('calcs.fitdecode.FitReader', _reader_factory(records, records))

    result = read_fit_file_data('/fake.fit')

    assert 'speed' in result
    assert 'elapsed_time' not in result
