# Generate Orbit Calculation Prompt

Create a reusable prompt for generating Python code that calculates satellite position and visibility.

## Description
Generate a Python function to calculate satellite position from TLE data, including orbital period, ECI coordinates, ground track latitude/longitude, and visibility from Entoto Observatory.

## Prompt

Write a Python function that:
- parses TLE lines for a satellite orbit
- computes the satellite orbital period
- propagates position in Earth-centered inertial (ECI) coordinates
- calculates ground track latitude and longitude
- evaluates whether the satellite is visible from Entoto Observatory at 9.03°N, 38.74°E

The function should include type hints, docstrings, and use standard orbital constants. Include any assumptions and clarify units.

## Example Invocation

```
Generate a Python function that takes TLE data and returns orbital period, ECI position, latitude, longitude, and Entoto visibility.
```
