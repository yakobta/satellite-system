"""
Configuration Management Module
Enterprise-grade configuration handling for satellite ground station
"""

import os
import yaml
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class OrbitalConfig:
    """Orbital mechanics configuration"""
    earth_radius_km: float = 6371.0
    gravitational_parameter: float = 3.986004418e5
    default_altitude_km: float = 550.0
    inclination_deg: float = 98.5
    eccentricity: float = 0.001


@dataclass
class SatelliteConfig:
    """Satellite configuration"""
    name: str = "ET-SAT-001"
    norad_id: int = 99999
    battery_capacity_ah: float = 100.0
    power_consumption_w: float = 500.0
    solar_panel_w: float = 1500.0
    telemetry_rate_hz: int = 1


@dataclass
class GroundStationConfig:
    """Ground station configuration"""
    name: str = "Addis Ababa Ground Station"
    location: str = "Entoto Observatory, Ethiopia"
    latitude: float = 9.03
    longitude: float = 38.74
    altitude_m: float = 3200.0
    port: int = 5005
    buffer_size: int = 65536


@dataclass
class DatabaseConfig:
    """Database configuration"""
    path: str = "data/telemetry.db"
    backup_enabled: bool = True
    retention_days: int = 30
    backup_interval_hours: int = 24


class Config:
    """Main configuration manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.orbital = OrbitalConfig()
        self.satellite = SatelliteConfig()
        self.ground_station = GroundStationConfig()
        self.database = DatabaseConfig()
        
        if config_path and os.path.exists(config_path):
            self._load_yaml(config_path)
    
    def _load_yaml(self, path: str):
        """Load configuration from YAML file"""
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                
                if 'orbital' in data:
                    for key, value in data['orbital'].items():
                        if hasattr(self.orbital, key):
                            setattr(self.orbital, key, value)
                
                if 'satellite' in data:
                    for key, value in data['satellite'].items():
                        if hasattr(self.satellite, key):
                            setattr(self.satellite, key, value)
                
                if 'ground_station' in data:
                    for key, value in data['ground_station'].items():
                        if hasattr(self.ground_station, key):
                            setattr(self.ground_station, key, value)
                
                if 'database' in data:
                    for key, value in data['database'].items():
                        if hasattr(self.database, key):
                            setattr(self.database, key, value)
                
                logger.info(f"Configuration loaded from {path}")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return {
            'orbital': self.orbital.__dict__,
            'satellite': self.satellite.__dict__,
            'ground_station': self.ground_station.__dict__,
            'database': self.database.__dict__
        }


# Global configuration instance
config = Config("config.yaml")
