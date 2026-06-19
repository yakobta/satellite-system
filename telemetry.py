"""
Database Models for Satellite Telemetry
"""

from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class TelemetryRecord:
    """Telemetry data model"""
    id: Optional[int] = None
    timestamp: str = ""
    satellite_id: str = "ETRSS-1"
    packet_id: int = 0
    position_x: float = 0.0
    position_y: float = 0.0
    latitude: float = 0.0
    longitude: float = 0.0
    battery_level: float = 0.0
    temperature: float = 0.0
    signal_strength: float = 0.0
    ground_contact: int = 0
    created_at: str = ""
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "satellite_id": self.satellite_id,
            "packet_id": self.packet_id,
            "position": {
                "x": self.position_x,
                "y": self.position_y
            },
            "coordinates": {
                "latitude": self.latitude,
                "longitude": self.longitude
            },
            "battery": self.battery_level,
            "temperature": self.temperature,
            "signal": self.signal_strength,
            "ground_contact": bool(self.ground_contact)
        }
