import datetime
import types
import pytest
import numpy as np
import fitdecode
from calcs import IPCalculator, read_fit_file_data


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
    v = np.full(10, 10.0)   # constant 10 m/s => zero acceleration term
    t = np.arange(10, dtype=float)
    p = np.full(10, 300.0)
    result = calc.calc_cda(t, v, p)
    # f_power = 300/10 * 0.98 = 29.4; f_rolling = -80*9.80665*0.004 ~= -3.14
    # cda = 2 / (1.2 * 100) * (29.4 - 3.14) ~= 0.438
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
