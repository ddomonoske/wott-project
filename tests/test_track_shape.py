import numpy as np
import pytest
from calcs import TrackShape


def test_kappa_zero_mid_straight():
    track = TrackShape(track_length=250.0, corners=0.60, transition=15.0, dx=0.1)
    result = track.compute()
    # The straight (50m total) is split by the curvature period's wrap point into
    # [0, 25) and (100, 125); s=10 sits well inside the first half, comfortably
    # outside the +-7.5m smoothing window around the s=25 corner boundary.
    idx = np.argmin(np.abs(result["s"] - 10.0))
    assert result["kappa"][idx] < 1e-9


def test_kappa_matches_radius_mid_corner():
    track = TrackShape(track_length=250.0, corners=0.60, transition=15.0, dx=0.1)
    result = track.compute()
    straight = 250.0 * (1 - 0.60) / 2  # 50.0
    corner = 250.0 * 0.60 / 2  # 75.0
    radius = corner / np.pi
    s_mid = straight + corner / 2
    idx = np.argmin(np.abs(result["s"] - s_mid))
    assert result["kappa"][idx] == pytest.approx(1.0 / radius, rel=1e-2)
    assert result["radius"] == pytest.approx(radius)


def test_compute_dict_shape():
    track = TrackShape()
    result = track.compute()
    assert set(result.keys()) == {"s", "kappa", "x", "y", "radius"}
    assert len(result["kappa"]) == len(result["s"])
    assert len(result["x"]) == len(result["s"])
    assert len(result["y"]) == len(result["s"])


def test_track_shape_closes_loop():
    track = TrackShape(track_length=250.0, corners=0.60, transition=15.0, dx=0.1)
    result = track.compute()
    # A closed oval should return close to its starting x/y after one full lap.
    assert result["x"][-1] == pytest.approx(result["x"][0], abs=1.0)
    assert result["y"][-1] == pytest.approx(result["y"][0], abs=1.0)
