"""Orbital calculations for ETRSS-1 and other low Earth orbit satellites."""

import math
import logging
from dataclasses import dataclass
from typing import Tuple

logger = logging.getLogger(__name__)

MU_EARTH = 398600.4418  # Earth's gravitational parameter, km^3/s^2
EARTH_RADIUS_KM = 6371.0  # Earth radius in kilometers
EARTH_ROTATION_RATE_RAD_S = 7.2921150e-5  # Earth rotation rate, rad/s


@dataclass
class KeplerElements:
    """Class for storing classical orbital elements."""
    inclination_deg: float
    raan_deg: float
    eccentricity: float
    arg_perigee_deg: float
    mean_anomaly_deg: float
    mean_motion_rev_per_day: float
    semi_major_axis_km: float
    period_seconds: float


@dataclass
class EciPosition:
    """Earth-centered inertial coordinates."""
    x_km: float
    y_km: float
    z_km: float


def calculate_orbital_period(mean_motion_rev_per_day: float) -> float:
    """Calculate orbital period in seconds from mean motion.

    Args:
        mean_motion_rev_per_day: Mean motion in revolutions per day.

    Returns:
        Orbital period in seconds.
    """
    if mean_motion_rev_per_day <= 0:
        raise ValueError("Mean motion must be positive")

    period_seconds = 86400.0 / mean_motion_rev_per_day
    logger.debug("Calculated orbital period: %.3f seconds", period_seconds)
    return period_seconds


def parse_tle(tle_line1: str, tle_line2: str) -> KeplerElements:
    """Parse two-line element (TLE) data into Keplerian orbital elements.

    Args:
        tle_line1: First line of TLE data.
        tle_line2: Second line of TLE data.

    Returns:
        KeplerElements containing parsed orbit parameters.
    """
    try:
        inclination_deg = float(tle_line2[8:16].strip())
        raan_deg = float(tle_line2[17:25].strip())
        eccentricity = float(f"0.{tle_line2[26:33].strip()}")
        arg_perigee_deg = float(tle_line2[34:42].strip())
        mean_anomaly_deg = float(tle_line2[43:51].strip())
        mean_motion_rev_per_day = float(tle_line2[52:63].strip())
    except (ValueError, IndexError) as exc:
        logger.error("Failed to parse TLE lines: %s", exc)
        raise ValueError("Invalid TLE format") from exc

    period_seconds = calculate_orbital_period(mean_motion_rev_per_day)
    mean_motion_rad_s = mean_motion_rev_per_day * 2 * math.pi / 86400.0
    semi_major_axis_km = (MU_EARTH / (mean_motion_rad_s**2)) ** (1.0 / 3.0)

    logger.info("Parsed TLE: inclination=%.2f°, mean motion=%.6f rev/day", inclination_deg, mean_motion_rev_per_day)

    return KeplerElements(
        inclination_deg=inclination_deg,
        raan_deg=raan_deg,
        eccentricity=eccentricity,
        arg_perigee_deg=arg_perigee_deg,
        mean_anomaly_deg=mean_anomaly_deg,
        mean_motion_rev_per_day=mean_motion_rev_per_day,
        semi_major_axis_km=semi_major_axis_km,
        period_seconds=period_seconds,
    )


def solve_kepler(mean_anomaly_rad: float, eccentricity: float, tolerance: float = 1e-10) -> float:
    """Solve Kepler's Equation for eccentric anomaly.

    Args:
        mean_anomaly_rad: Mean anomaly in radians.
        eccentricity: Orbital eccentricity.
        tolerance: Convergence tolerance.

    Returns:
        Eccentric anomaly in radians.
    """
    if eccentricity < 0 or eccentricity >= 1:
        raise ValueError("Only elliptical orbits with 0 <= e < 1 are supported")

    E = mean_anomaly_rad if eccentricity < 0.8 else math.pi
    for _ in range(100):
        f = E - eccentricity * math.sin(E) - mean_anomaly_rad
        f_prime = 1 - eccentricity * math.cos(E)
        delta = f / f_prime
        E -= delta
        if abs(delta) < tolerance:
            break
    else:
        logger.warning("Kepler solver did not converge after 100 iterations")

    logger.debug("Solved Kepler equation: E=%.8f rad", E)
    return E


def true_anomaly(mean_anomaly_rad: float, eccentricity: float) -> float:
    """Compute true anomaly from mean anomaly and eccentricity."""
    E = solve_kepler(mean_anomaly_rad, eccentricity)
    numerator = math.sqrt(1 + eccentricity) * math.sin(E / 2.0)
    denominator = math.sqrt(1 - eccentricity) * math.cos(E / 2.0)
    theta = 2.0 * math.atan2(numerator, denominator)
    theta = theta % (2.0 * math.pi)
    logger.debug("Calculated true anomaly: %.6f rad", theta)
    return theta


def eci_position(elements: KeplerElements, elapsed_seconds: float = 0.0) -> EciPosition:
    """Compute ECI position for the orbit at a given elapsed time.

    Args:
        elements: KeplerElements describing the orbit.
        elapsed_seconds: Time since epoch in seconds.

    Returns:
        EciPosition in kilometers.
    """
    mean_motion_rad_s = elements.mean_motion_rev_per_day * 2.0 * math.pi / 86400.0
    mean_anomaly_rad = (math.radians(elements.mean_anomaly_deg) + mean_motion_rad_s * elapsed_seconds) % (2.0 * math.pi)
    true_anomaly_rad = true_anomaly(mean_anomaly_rad, elements.eccentricity)

    semi_major_axis = elements.semi_major_axis_km
    r_km = semi_major_axis * (1 - elements.eccentricity**2) / (1 + elements.eccentricity * math.cos(true_anomaly_rad))

    x_orb = r_km * math.cos(true_anomaly_rad)
    y_orb = r_km * math.sin(true_anomaly_rad)

    cos_omega = math.cos(math.radians(elements.arg_perigee_deg))
    sin_omega = math.sin(math.radians(elements.arg_perigee_deg))
    cos_i = math.cos(math.radians(elements.inclination_deg))
    sin_i = math.sin(math.radians(elements.inclination_deg))
    cos_O = math.cos(math.radians(elements.raan_deg))
    sin_O = math.sin(math.radians(elements.raan_deg))

    x = (
        (cos_O * cos_omega - sin_O * sin_omega * cos_i) * x_orb
        - (cos_O * sin_omega + sin_O * cos_omega * cos_i) * y_orb
    )
    y = (
        (sin_O * cos_omega + cos_O * sin_omega * cos_i) * x_orb
        - (sin_O * sin_omega - cos_O * cos_omega * cos_i) * y_orb
    )
    z = (sin_omega * sin_i) * x_orb + (cos_omega * sin_i) * y_orb

    logger.debug("Computed ECI position: x=%.3f, y=%.3f, z=%.3f", x, y, z)
    return EciPosition(x_km=x, y_km=y, z_km=z)


def eci_to_ecef(position: EciPosition, elapsed_seconds: float = 0.0) -> EciPosition:
    """Convert ECI coordinates to ECEF using Earth rotation."""
    theta = (EARTH_ROTATION_RATE_RAD_S * elapsed_seconds) % (2.0 * math.pi)

    x = math.cos(theta) * position.x_km + math.sin(theta) * position.y_km
    y = -math.sin(theta) * position.x_km + math.cos(theta) * position.y_km
    z = position.z_km

    logger.debug("Converted ECI to ECEF with theta=%.6f rad", theta)
    return EciPosition(x_km=x, y_km=y, z_km=z)


def ground_track_from_ecef(position: EciPosition) -> Tuple[float, float]:
    """Calculate ground track latitude and longitude from ECEF coordinates."""
    latitude_rad = math.atan2(position.z_km, math.sqrt(position.x_km**2 + position.y_km**2))
    longitude_rad = math.atan2(position.y_km, position.x_km)

    latitude_deg = math.degrees(latitude_rad)
    longitude_deg = math.degrees(longitude_rad)
    if longitude_deg > 180.0:
        longitude_deg -= 360.0
    elif longitude_deg < -180.0:
        longitude_deg += 360.0

    logger.debug("Ground track lat=%.6f°, lon=%.6f°", latitude_deg, longitude_deg)
    return latitude_deg, longitude_deg


def is_visible_from_entoto(latitude_deg: float, longitude_deg: float, altitude_km: float) -> bool:
    """Estimate satellite visibility from Entoto Observatory.

    Args:
        latitude_deg: Sub-satellite latitude.
        longitude_deg: Sub-satellite longitude.
        altitude_km: Satellite altitude above Earth surface.

    Returns:
        True if the satellite is within a visibility cone from Entoto.
    """
    station_lat_rad = math.radians(9.03)
    station_lon_rad = math.radians(38.74)
    sat_lat_rad = math.radians(latitude_deg)
    sat_lon_rad = math.radians(longitude_deg)

    central_angle = math.acos(
        math.sin(station_lat_rad) * math.sin(sat_lat_rad)
        + math.cos(station_lat_rad) * math.cos(sat_lat_rad) * math.cos(abs(station_lon_rad - sat_lon_rad))
    )

    horizon_angle = math.acos(EARTH_RADIUS_KM / (EARTH_RADIUS_KM + altitude_km))
    visibility_limit_rad = horizon_angle + math.radians(5.0)

    visible = central_angle <= visibility_limit_rad
    logger.debug(
        "Visibility check: central_angle=%.6f rad, horizon=%.6f rad, visible=%s",
        central_angle,
        visibility_limit_rad,
        visible,
    )
    return visible


def calculate_orbit_state_from_tle(
    tle_line1: str,
    tle_line2: str,
    elapsed_seconds: float = 0.0,
) -> Tuple[KeplerElements, EciPosition, float, float, bool]:
    """Calculate orbit state and visibility from TLE data.

    Args:
        tle_line1: First line of the TLE.
        tle_line2: Second line of the TLE.
        elapsed_seconds: Seconds since epoch reference.

    Returns:
        A tuple containing KeplerElements, ECI position, latitude, longitude, and visibility.
    """
    elements = parse_tle(tle_line1, tle_line2)
    eci = eci_position(elements, elapsed_seconds)
    ecef = eci_to_ecef(eci, elapsed_seconds)
    latitude_deg, longitude_deg = ground_track_from_ecef(ecef)
    visible = is_visible_from_entoto(latitude_deg, longitude_deg, elements.semi_major_axis_km - EARTH_RADIUS_KM)

    return elements, eci, latitude_deg, longitude_deg, visible
