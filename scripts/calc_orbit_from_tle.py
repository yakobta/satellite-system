#!/usr/bin/env python3
"""Calculate satellite orbit state from TLE data."""

import argparse
from pathlib import Path
from typing import Tuple

from src.orbital_calculations import calculate_orbit_state_from_tle


DEFAULT_TLE = (
    "1 44880U 19049A   20059.59855137  .00000024  00000-0  00000+0 0  9996",
    "2 44880  97.8401  85.2526 0012700 147.8284 212.2884 14.86355100    12",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate satellite orbit state from TLE data."
    )
    parser.add_argument(
        "--tle-file",
        type=Path,
        help="Path to a text file containing two TLE lines.",
    )
    parser.add_argument(
        "--elapsed",
        type=float,
        default=0.0,
        help="Elapsed seconds since epoch reference for propagation.",
    )
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Output the results as JSON.",
    )
    return parser.parse_args()


def read_tle_file(path: Path) -> Tuple[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"TLE file not found: {path}")

    lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if len(lines) < 2:
        raise ValueError("TLE file must contain at least two non-empty lines.")

    return lines[0], lines[1]


def render_results(
    elements,
    eci,
    latitude_deg: float,
    longitude_deg: float,
    visible: bool,
    output_json: bool,
) -> None:
    if output_json:
        import json

        result = {
            "orbital_elements": {
                "inclination_deg": elements.inclination_deg,
                "raan_deg": elements.raan_deg,
                "eccentricity": elements.eccentricity,
                "arg_perigee_deg": elements.arg_perigee_deg,
                "mean_anomaly_deg": elements.mean_anomaly_deg,
                "mean_motion_rev_per_day": elements.mean_motion_rev_per_day,
                "semi_major_axis_km": round(elements.semi_major_axis_km, 3),
                "period_seconds": round(elements.period_seconds, 3),
            },
            "eci_position": {
                "x_km": round(eci.x_km, 3),
                "y_km": round(eci.y_km, 3),
                "z_km": round(eci.z_km, 3),
            },
            "ground_track": {
                "latitude_deg": round(latitude_deg, 5),
                "longitude_deg": round(longitude_deg, 5),
            },
            "visible_from_entoto": visible,
        }
        print(json.dumps(result, indent=2))
        return

    print("Orbital Elements:")
    print(f"  Inclination: {elements.inclination_deg:.5f}°")
    print(f"  RAAN: {elements.raan_deg:.5f}°")
    print(f"  Eccentricity: {elements.eccentricity:.7f}")
    print(f"  Argument of perigee: {elements.arg_perigee_deg:.5f}°")
    print(f"  Mean anomaly: {elements.mean_anomaly_deg:.5f}°")
    print(f"  Mean motion: {elements.mean_motion_rev_per_day:.8f} rev/day")
    print(f"  Semi-major axis: {elements.semi_major_axis_km:.3f} km")
    print(f"  Orbital period: {elements.period_seconds:.1f} s")
    print()
    print("ECI Position:")
    print(f"  x: {eci.x_km:.3f} km")
    print(f"  y: {eci.y_km:.3f} km")
    print(f"  z: {eci.z_km:.3f} km")
    print()
    print("Ground Track:")
    print(f"  Latitude: {latitude_deg:.5f}°")
    print(f"  Longitude: {longitude_deg:.5f}°")
    print()
    print(f"Visible from Entoto: {'YES' if visible else 'NO'}")


def main() -> None:
    args = parse_args()

    if args.tle_file:
        tle_line1, tle_line2 = read_tle_file(args.tle_file)
    else:
        tle_line1, tle_line2 = DEFAULT_TLE

    elements, eci, latitude_deg, longitude_deg, visible = calculate_orbit_state_from_tle(
        tle_line1, tle_line2, args.elapsed
    )

    render_results(elements, eci, latitude_deg, longitude_deg, visible, args.output_json)


if __name__ == "__main__":
    main()
