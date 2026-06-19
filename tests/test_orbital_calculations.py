import math

from src.orbital_calculations import (
    calculate_orbital_period,
    parse_tle,
    eci_position,
    eci_to_ecef,
    ground_track_from_ecef,
    is_visible_from_entoto,
)


def test_calculate_orbital_period():
    period = calculate_orbital_period(14.86355)
    assert math.isclose(period, 86400.0 / 14.86355, rel_tol=1e-9)


def test_parse_tle_returns_expected_elements():
    tle_line1 = "1 44880U 19049A   20059.59855137  .00000024  00000-0  00000+0 0  9996"
    tle_line2 = "2 44880  97.8401  85.2526 0012700 147.8284 212.2884 14.86355100    12"

    elements = parse_tle(tle_line1, tle_line2)
    assert math.isclose(elements.inclination_deg, 97.8401, rel_tol=1e-6)
    assert math.isclose(elements.mean_motion_rev_per_day, 14.86355100, rel_tol=1e-9)
    assert elements.eccentricity == 0.00127
    assert elements.period_seconds == 86400.0 / 14.86355100


def test_eci_to_ecef_and_ground_track():
    tle_line1 = "1 44880U 19049A   20059.59855137  .00000024  00000-0  00000+0 0  9996"
    tle_line2 = "2 44880  97.8401  85.2526 0012700 147.8284 212.2884 14.86355100    12"
    elements = parse_tle(tle_line1, tle_line2)
    eci = eci_position(elements, elapsed_seconds=600.0)
    ecef = eci_to_ecef(eci, elapsed_seconds=600.0)
    latitude, longitude = ground_track_from_ecef(ecef)

    assert -90.0 <= latitude <= 90.0
    assert -180.0 <= longitude <= 180.0


def test_visibility_from_entoto():
    latitude_deg = 9.03
    longitude_deg = 38.74
    assert is_visible_from_entoto(latitude_deg, longitude_deg, altitude_km=628.0)

    far_latitude = -60.0
    far_longitude = 120.0
    assert not is_visible_from_entoto(far_latitude, far_longitude, altitude_km=628.0)
