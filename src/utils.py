"""
Utility Functions
Helper functions for logging, formatting, and calculations
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any
import math

# Configure logging
def setup_logging(level: str = "INFO", log_file: str = "logs/satellite.log"):
    """Setup professional logging configuration"""
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def format_telemetry(telemetry: Dict[str, Any]) -> str:
    """Format telemetry for display"""
    return json.dumps(telemetry, indent=2, default=str)


def calculate_orbit(altitude_km: float) -> Dict[str, float]:
    """Calculate orbital parameters"""
    EARTH_RADIUS_KM = 6371.0
    MU_EARTH = 3.986004418e5  # km³/s²
    
    orbit_radius_km = EARTH_RADIUS_KM + altitude_km
    velocity_kms = math.sqrt(MU_EARTH / orbit_radius_km)
    period_seconds = 2 * math.pi * math.sqrt(orbit_radius_km**3 / MU_EARTH)
    
    return {
        "orbit_radius_km": round(orbit_radius_km, 1),
        "velocity_kms": round(velocity_kms, 3),
        "period_seconds": round(period_seconds, 1),
        "period_minutes": round(period_seconds / 60, 2)
    }


def bytes_to_mb(bytes_value: int) -> float:
    """Convert bytes to megabytes"""
    return round(bytes_value / (1024 * 1024), 2)


# Global logger
logger = setup_logging()
