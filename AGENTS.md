# 🛰️ AI Agent Instructions for Satellite Ground Station System

This document helps AI coding agents understand the ETRSS-1 satellite ground station codebase and be immediately productive.

## Project Overview

A professional-grade Python satellite ground station simulation system for Ethiopia's first satellite (ETRSS-1). Features real-time telemetry processing, orbital mechanics simulation, SQLite database storage, and anomaly detection. This is **production-ready code** that demonstrates enterprise-grade satellite operations.

- **Tech Stack**: Python 3.9+, SQLite, pydantic, numpy, pytest
- **Architecture**: Modular, separated concerns (satellite simulator, ground station receiver, telemetry processing, database, config)
- **Key Files**: [src/satellite.py](src/satellite.py), [src/ground_station.py](src/ground_station.py), [src/database.py](src/database.py), [src/config.py](src/config.py), [main.py](main.py)

---

## Development Standards (ENFORCE)

### Commit Messages
Use concise emoji-prefixed commits:
- `🚀 feature: description` - New features
- `🛰️ refactor: description` - Code improvements
- `🐛 fix: description` - Bug fixes
- `🇪🇹 docs: description` - Documentation updates
- `✅ test: description` - Test additions

Example: `🚀 feature: add battery anomaly detection for voltage drops`

### Code Style & Type Hints
- **PEP 8 compliance** - Follow Python style guidelines strictly
- **Type hints** - Required for all functions, method parameters, and return types
  ```python
  def calculate_altitude(position_x: float, position_y: float, position_z: float) -> float:
      """Calculate altitude from cartesian coordinates."""
  ```
- **Docstrings** - All modules, classes, and functions require docstrings
  ```python
  """Module description. One sentence overview."""
  
  class Satellite:
      """Professional Satellite Simulator. Simulates orbital mechanics and telemetry."""
      
  def transmit_telemetry(self, host: str, port: int) -> bool:
      """Send telemetry packet to ground station. Returns True if successful."""
  ```
- **F-strings only** - Never use `.format()` or `%` formatting
  ```python
  logger.info(f"Satellite {self.name} initialized at {timestamp}")
  ```

### Logging (REQUIRED)
All major operations **must** include logging:
- **Level selection**: `DEBUG` for variable states, `INFO` for operations, `WARNING` for anomalies, `ERROR` for failures
- **Format**: Use module logger `logger = logging.getLogger(__name__)`
- **Pattern**: Log at entry/exit of significant functions, state changes, errors
  ```python
  logger.info(f"Starting Ground Station on port {args.port}")
  logger.warning(f"Battery voltage {voltage}V below threshold {threshold}V")
  logger.error(f"Database connection failed: {exc}")
  ```

### Error Handling
- **Use try/except** for all I/O, network, database operations
- **Specific exceptions** - Catch specific exception types, not bare `except`
- **Logging on error** - Always log exceptions before re-raising or handling
- **Graceful degradation** - Maintain system state even when operations fail
  ```python
  try:
      telemetry_data = self.socket.recvfrom(1024)
  except socket.timeout:
      logger.warning("Telemetry reception timeout - retrying")
      return None
  except Exception as exc:
      logger.error(f"Unexpected socket error: {exc}")
      raise
  ```

### Testing
- **Location**: Create `tests/` directory at project root
- **Naming**: `test_*.py` files for test modules
- **Coverage**: Aim for 80%+ coverage on critical paths (satellite.py, database.py, telemetry.py)
- **Framework**: pytest with pytest-cov
- **Run tests**: `pytest --cov=src tests/`
- **Example**:
  ```python
  def test_calculate_altitude():
      """Test altitude calculation from position data."""
      # Test implementation
  ```

---

## Architecture & Key Patterns

### Module Organization
```
src/
├── satellite.py         # Satellite simulator with orbital mechanics
├── ground_station.py    # Ground station receiver and data processor
├── database.py          # SQLite telemetry storage and queries
├── telemetry.py         # Data structures (TelemetryPacket, BatteryData, etc.)
├── config.py            # Configuration management (dataclasses-based)
├── utils.py             # Logging setup, calculations, formatting
└── real_satellite_tracker.py  # External satellite tracking integration
```

### Core Patterns

**Configuration Management** - Use [config.py](src/config.py) dataclass pattern:
- `OrbitalConfig`, `SatelliteConfig`, `GroundStationConfig`, `DatabaseConfig`
- Load from YAML files: `Config(config_path="config.yaml")`
- Access via `config.satellite.name`, `config.orbital.altitude_km`

**Telemetry Structure** - Use dataclasses for data ([telemetry.py](src/telemetry.py)):
- `TelemetryPacket` - Complete satellite telemetry
- `PositionData`, `BatteryData`, `ThermalData`, `CommsData` - Subsystem telemetry
- Include `to_dict()` method for JSON serialization

**Database Operations** - Context managers for SQLite:
```python
@contextmanager
def get_connection(self):
    """Database connection context manager."""
    # Connection handling
```

**Satellite State** - Thread-safe state management:
- Use `threading.Lock()` for shared state
- Atomic operations for telemetry updates
- Graceful shutdown with `running` flag

**Logging Setup** - Central logger initialization:
- Call `setup_logging()` in main entry point
- All modules use `logging.getLogger(__name__)`
- JSON-formatted logs with rotation support

---

## Running the System

### Single Terminal (Sequential)
```bash
# Terminal: Start both satellite and ground station sequentially
python main.py --mode ground --port 5005
python main.py --mode satellite --port 5005
```

### Dual Terminal (Concurrent - Recommended)
```bash
# Terminal 1: Start ground station receiver
python main.py --mode ground --port 5005

# Terminal 2: Start satellite simulator transmitter
python main.py --mode satellite --port 5005
```

### Database Operations
```bash
# View telemetry data
python scripts/visualize_db.py

# Run custom queries
sqlite3 data/telemetry.db < sql/queries.sql

# Generate professional report
python scripts/professional_report.py
```

---

## Common Development Tasks

### Adding New Telemetry Sensors
1. Add field to appropriate dataclass in [src/telemetry.py](src/telemetry.py)
2. Add calculation logic in [src/satellite.py](src/satellite.py) `_generate_telemetry()`
3. Update database schema in [src/database.py](src/database.py)
4. Add to JSON serialization in `TelemetryRecord.to_dict()`

### Adding Anomaly Detection Rules
1. Create detection function in module-specific file (e.g., battery anomaly in ground_station.py)
2. Add logging at `WARNING` level when anomaly detected
3. Implement graceful handling (alert, log, continue)
4. Add test case to `tests/test_anomaly_detection.py`

### Database Queries
- Location: [sql/queries.sql](sql/queries.sql)
- Run via: `python scripts/visualize_db.py` or direct SQLite
- Always include timestamp filters for performance
- Log slow queries at `DEBUG` level

### Configuration Changes
1. Edit [config.yaml](config.yaml) or [config_etrss1.yaml](config_etrss1.yaml)
2. Update corresponding dataclass in [src/config.py](src/config.py)
3. Reload via `Config(config_path="config.yaml")`
4. Log configuration changes at `INFO` level

---

## Critical Files & Conventions

| File | Purpose | Key Convention |
|------|---------|-----------------|
| [main.py](main.py) | Entry point | Parse args, setup logging, instantiate simulator/station |
| [src/satellite.py](src/satellite.py) | Orbital mechanics, telemetry generation | Realistic physics-based calculations |
| [src/ground_station.py](src/ground_station.py) | Telemetry receiver, data processor | UDP reception, anomaly detection |
| [src/database.py](src/database.py) | SQLite storage, queries | Context managers, thread safety |
| [src/telemetry.py](src/telemetry.py) | Data structures | Dataclasses with `to_dict()` methods |
| [src/config.py](src/config.py) | Configuration | Dataclass-based, YAML-loadable |
| [requirements.txt](requirements.txt) | Dependencies | Keep minimal, pin major versions |

---

## Do's and Don'ts

### ✅ DO
- Use type hints for all function signatures
- Include docstrings explaining "what" and "why"
- Log significant state changes and errors
- Handle exceptions gracefully with specific error types
- Use f-strings for all string formatting
- Keep functions focused and under 50 lines
- Test critical paths (satellite physics, database operations)
- Use dataclasses for structured data
- Lock shared state in threaded code
- Document complex orbital mechanics calculations

### ❌ DON'T
- Use `.format()` or `%` string formatting
- Write bare `except:` or `except Exception:` without specificity
- Skip error logging before re-raising
- Mix concerns in modules (e.g., satellite logic with database logic)
- Use global variables for state (use class attributes with locks)
- Ignore type hints or use `Any` for lazy typing
- Write multi-line functions without docstrings
- Leave debug print statements in production code
- Hardcode values instead of using config
- Forget to log when operations fail or succeed unexpectedly

---

## Ethiopian Context & Mission

This system represents Ethiopia's ETRSS-1 satellite program:
- 🇪🇹 First Ethiopian-developed satellite
- 🛰️ Addis Ababa Ground Station (Entoto Observatory)
- 🌍 Low Earth Orbit (LEO) at ~550 km altitude
- 📡 Real-time telemetry reception and processing

Honor the mission by maintaining **high code quality, thorough testing, and professional documentation**.

---

## Questions or Clarifications?

When in doubt, consult:
1. [README.md](README.md) - Project overview
2. [src/config.py](src/config.py) - Configuration structure
3. [src/telemetry.py](src/telemetry.py) - Data models
4. Existing code in `src/` directory as reference

For agent use: Reference existing modules to understand patterns, maintain consistency with established style, and prioritize production readiness and test coverage.
