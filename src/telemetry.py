"""
Telemetry Data Models
Defines structured telemetry data classes for satellite communication
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import json


class SatelliteMode(Enum):
    """Satellite operational modes"""
    NORMAL = "NORMAL"
    SAFE = "SAFE_MODE"
    LOW_POWER = "LOW_POWER"
    MANEUVER = "MANEUVERING"
    COMM_LOSS = "COMM_LOSS"


class SubsystemStatus(Enum):
    """Subsystem health status"""
    NOMINAL = "NOMINAL"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    OFFLINE = "OFFLINE"


@dataclass
class PositionData:
    """Satellite position data"""
    x_km: float = 0.0
    y_km: float = 0.0
    z_km: float = 0.0
    altitude_km: float = 550.0
    velocity_kms: float = 0.0
    angle_deg: float = 0.0
    latitude_deg: float = 0.0
    longitude_deg: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            'x_km': self.x_km,
            'y_km': self.y_km,
            'z_km': self.z_km,
            'altitude_km': self.altitude_km,
            'velocity_kms': self.velocity_kms,
            'angle_deg': self.angle_deg,
            'latitude_deg': self.latitude_deg,
            'longitude_deg': self.longitude_deg
        }


@dataclass
class BatteryData:
    """Battery telemetry data"""
    level_percent: float = 100.0
    voltage_v: float = 28.0
    current_a: float = 0.0
    temperature_c: float = 25.0
    charge_rate_w: float = 0.0
    cycles: int = 0
    health_percent: float = 100.0
    status: SubsystemStatus = SubsystemStatus.NOMINAL
    
    def to_dict(self) -> dict:
        return {
            'level_percent': round(self.level_percent, 2),
            'voltage_v': round(self.voltage_v, 2),
            'current_a': round(self.current_a, 2),
            'temperature_c': round(self.temperature_c, 1),
            'charge_rate_w': round(self.charge_rate_w, 2),
            'cycles': self.cycles,
            'health_percent': round(self.health_percent, 2),
            'status': self.status.value
        }


@dataclass
class ThermalData:
    """Thermal telemetry data"""
    main_bus_c: float = 22.0
    payload_c: float = 18.0
    battery_c: float = 25.0
    transmitter_c: float = 35.0
    radiator_c: float = 10.0
    heater_power_w: float = 0.0
    status: SubsystemStatus = SubsystemStatus.NOMINAL
    
    def to_dict(self) -> dict:
        return {
            'main_bus_c': round(self.main_bus_c, 1),
            'payload_c': round(self.payload_c, 1),
            'battery_c': round(self.battery_c, 1),
            'transmitter_c': round(self.transmitter_c, 1),
            'radiator_c': round(self.radiator_c, 1),
            'heater_power_w': round(self.heater_power_w, 2),
            'status': self.status.value
        }


@dataclass
class CommsData:
    """Communications telemetry data"""
    signal_strength_percent: float = 85.0
    data_rate_mbps: float = 50.0
    bit_error_rate: float = 1e-9
    tx_power_w: float = 10.0
    link_margin_db: float = 12.0
    packets_sent: int = 0
    packets_received: int = 0
    status: SubsystemStatus = SubsystemStatus.NOMINAL
    
    def to_dict(self) -> dict:
        return {
            'signal_strength_percent': round(self.signal_strength_percent, 1),
            'data_rate_mbps': round(self.data_rate_mbps, 2),
            'bit_error_rate': f"{self.bit_error_rate:.2e}",
            'tx_power_w': round(self.tx_power_w, 2),
            'link_margin_db': round(self.link_margin_db, 1),
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'status': self.status.value
        }


@dataclass
class TelemetryPacket:
    """Complete telemetry packet"""
    timestamp: datetime = field(default_factory=datetime.now)
    satellite_id: str = "ET-SAT-001"
    packet_id: int = 0
    mode: SatelliteMode = SatelliteMode.NORMAL
    position: PositionData = field(default_factory=PositionData)
    battery: BatteryData = field(default_factory=BatteryData)
    thermal: ThermalData = field(default_factory=ThermalData)
    comms: CommsData = field(default_factory=CommsData)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'satellite_id': self.satellite_id,
            'packet_id': self.packet_id,
            'mode': self.mode.value,
            'position': self.position.to_dict(),
            'battery': self.battery.to_dict(),
            'thermal': self.thermal.to_dict(),
            'comms': self.comms.to_dict()
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TelemetryPacket':
        """Create from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            satellite_id=data['satellite_id'],
            packet_id=data['packet_id'],
            mode=SatelliteMode(data['mode']),
            position=PositionData(**data['position']),
            battery=BatteryData(**data['battery']),
            thermal=ThermalData(**data['thermal']),
            comms=CommsData(**data['comms'])
        )
