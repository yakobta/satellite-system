# 🛰️ Satellite Ground Station System

## Ethiopian Space Science and Technology Institute - Prototype

A professional-grade satellite ground station simulation system demonstrating real-time telemetry reception, orbital mechanics, and mission control operations.

## 📋 Features

- **Real-time Telemetry Processing** - UDP-based data reception at 1Hz
- **Orbital Mechanics Simulation** - Physics-based position calculation
- **SQLite Database Storage** - Persistent telemetry logging
- **Anomaly Detection** - Automatic alerts for critical conditions
- **Professional Logging** - JSON-formatted logs with rotation
- **Modular Architecture** - Clean separation of concerns

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Run the System

Open two terminals:

```bash
# Terminal 1: Ground station receiver
python main.py --mode ground

# Terminal 2: Satellite simulator transmitter
python main.py --mode satellite
```

### Orbit Calculation CLI

Use the TLE-based orbit helper to compute orbital state and visibility from Entoto Observatory.

```bash
python3 scripts/calc_orbit_from_tle.py --elapsed 600
python3 scripts/calc_orbit_from_tle.py --tle-file path/to/tle.txt --elapsed 600 --output-json
```

## 📁 Important Files

- `main.py` - Entry point for ground station and satellite simulator
- `src/satellite.py` - Satellite simulator, telemetry generation, and broadcast
- `src/ground_station.py` - UDP telemetry receiver and processing
- `src/orbital_calculations.py` - TLE-based orbit propagation and ground track
- `src/database.py` - SQLite telemetry storage and queries
- `src/telemetry.py` - Data models for telemetry packets
- `scripts/calc_orbit_from_tle.py` - TLE orbit CLI helper

## 🧪 Testing

Run the unit tests with:

```bash
python3 -m pytest tests/ -q
```

## 📌 Notes

- Ground station listens on UDP port `5005` by default.
- Use ETRSS-1 parameters (NORAD 44880, 628 km altitude, 97.84° inclination).
- Store all telemetry and health data in SQLite.
