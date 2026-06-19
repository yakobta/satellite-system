# Orbital Mechanics Skill

This skill captures the workflow for calculating ETRSS-1 orbital state and ground track.

## Purpose

Calculate ETRSS-1 satellite position and ground track using mission parameters.

## Inputs

- NORAD ID: `44880`
- Altitude: `628 km`
- Inclination: `97.84°`
- Period: `97 minutes`

## Constants

- `MU_EARTH = 3.986004418e5` km³/s²
- `EARTH_RADIUS_KM = 6371.0` km
- `DEG_TO_RAD = math.pi / 180`
- `RAD_TO_DEG = 180 / math.pi`

## Workflow

1. **Choose orbit model**
   - Use a circular orbit model for ETRSS-1 because altitude and inclination are specified and eccentricity is assumed small.
   - If a TLE is available, use the NORAD ID `44880` to map it to propagation parameters.

2. **Compute orbital radius**
   - `ORBIT_RADIUS = EARTH_RADIUS_KM + ALTITUDE_KM`

3. **Calculate orbital velocity**
   - `velocity_kms = math.sqrt(MU_EARTH / ORBIT_RADIUS)`
   - This is the vis-viva equation for a circular orbit.

4. **Compute angular velocity**
   - `period_seconds = PERIOD_MINUTES * 60`
   - `angular_velocity = 2 * math.pi / period_seconds`

5. **Propagate angle over time**
   - `angle = (angular_velocity * elapsed_seconds) % (2 * math.pi)`
   - Use elapsed time from epoch or simulation start.

6. **Calculate orbital position in the local orbital plane**
   - `x_orbit = ORBIT_RADIUS * math.cos(angle)`
   - `y_orbit = ORBIT_RADIUS * math.sin(angle)`
   - `z_orbit = 0.0` for the orbital plane before inclination.

7. **Apply inclination to get Earth-centered coordinates**
   - `inclination_rad = INCLINATION_DEG * DEG_TO_RAD`
   - `x_ecef = x_orbit`
   - `y_ecef = y_orbit * math.cos(inclination_rad)`
   - `z_ecef = y_orbit * math.sin(inclination_rad)`

8. **Compute ground track latitude and longitude**
   - Latitude from `z_ecef` and orbital radius.
   - Longitude from `atan2(y_ecef, x_ecef)` plus Earth rotation offset if modeling Earth rotation.

9. **Validate results**
   - Velocity should be near `7.7 km/s`.
   - Altitude should remain near `628 km`.
   - Period should match `~97 minutes`.
   - Inclination should result in near-polar ground tracks.

## Example Calculation

```python
import math

MU_EARTH = 3.986004418e5
EARTH_RADIUS_KM = 6371.0

altitude_km = 628.0
period_minutes = 97.0
inclination_deg = 97.84

orbit_radius = EARTH_RADIUS_KM + altitude_km
velocity_kms = math.sqrt(MU_EARTH / orbit_radius)
period_seconds = period_minutes * 60
angular_velocity = 2 * math.pi / period_seconds

elapsed_seconds = 600.0
angle = (angular_velocity * elapsed_seconds) % (2 * math.pi)

x = orbit_radius * math.cos(angle)
y = orbit_radius * math.sin(angle)

inclination_rad = math.radians(inclination_deg)
x_ecef = x
y_ecef = y * math.cos(inclination_rad)
z_ecef = y * math.sin(inclination_rad)
```

## Decision Points

- Use circular propagation if orbit eccentricity is negligible.
- Use Earth rotation adjustment when computing ground-track longitude for multi-pass predictions.
- Use TLE-based propagation only when accurate ephemeris is required.

## Quality Checks

- Ensure angle units are consistent: radians for trig functions, degrees for output.
- Keep return units explicit: km for distance, km/s for velocity, degrees for angles.
- Log or assert that computed velocity and period match expected ETRSS-1 values.
- Document all assumptions, especially orbit circularity and Earth rotation treatment.

## Outcome

A reusable orbital mechanics workflow for ETRSS-1 that produces:
- orbital velocity
- position coordinates in km
- ground track latitude/longitude
- validation against expected mission values
