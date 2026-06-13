#!/usr/bin/env python3
"""
Professional Satellite Simulator - Advanced Orbital Mechanics & Telemetry
High-fidelity satellite simulation with realistic physics and systems engineering
Author: Aerospace Systems Engineer
Version: 2.0.0
"""

import socket
import json
import time
import math
import random
import logging
import threading
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('satellite.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Earth Physical Constants
class EarthConstants:
    """Earth physical constants for orbital mechanics"""
    MU = 3.986004418e14          # Gravitational parameter (m³/s²)
    RADIUS = 6371000.0           # Equatorial radius (m)
    ROTATION_PERIOD = 86164.0    # Sidereal day (seconds)
    J2 = 1.08262668e-3           # J2 perturbation coefficient


@dataclass
class OrbitalParameters:
    """Satellite orbital parameters"""
    semi_major_axis: float       # meters
    eccentricity: float
    inclination: float           # degrees
    raan: float                  # Right ascension (degrees)
    arg_perigee: float           # Argument of perigee (degrees)
    true_anomaly: float          # Current position (degrees)


class SatelliteMode(Enum):
    """Satellite operational modes"""
    NORMAL = "NORMAL"
    SAFE = "SAFE_MODE"
    LOW_POWER = "LOW_POWER"
    MANEUVER = "MANEUVERING"
    COMM_LOSS = "COMM_LOSS"


class Subsystem:
    """Base class for satellite subsystems"""
    def __init__(self, name: str):
        self.name = name
        self.temperature = 20.0
        self.status = "NOMINAL"
        self.power_consumption = 0.0
    
    def update(self, satellite_state: Dict):
        """Update subsystem state - to be overridden"""
        pass


class ADCSSubsystem(Subsystem):
    """Attitude Determination and Control System"""
    def __init__(self):
        super().__init__("ADCS")
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.star_tracker_status = "TRACKING"
        self.gyro_drift = 0.0
    
    def update(self, satellite_state: Dict):
        # Simulate attitude errors
        self.roll = random.uniform(-2, 2)
        self.pitch = random.uniform(-2, 2)
        self.yaw = random.uniform(-2, 2)
        self.gyro_drift += random.uniform(-0.01, 0.01)
        
        # Temperature effects
        self.temperature = 18 + random.uniform(-3, 5)
        self.power_consumption = 45.0 + random.uniform(-5, 10)
    
    def get_telemetry(self) -> Dict:
        return {
            "roll_deg": round(self.roll, 2),
            "pitch_deg": round(self.pitch, 2),
            "yaw_deg": round(self.yaw, 2),
            "star_tracker": self.star_tracker_status,
            "gyro_drift": round(self.gyro_drift, 3),
            "temperature": round(self.temperature, 1),
            "status": self.status
        }


class PowerSubsystem(Subsystem):
    """Electrical Power System"""
    def __init__(self, battery_capacity: float = 100.0):
        super().__init__("EPS")
        self.battery_level = 100.0
        self.solar_array_power = 0.0
        self.load_power = 0.0
        self.charge_current = 0.0
        self.battery_voltage = 28.0
        self.battery_capacity = battery_capacity
        self.cycles = 0
    
    def update(self, satellite_state: Dict):
        # Solar panel efficiency based on sun angle
        sun_angle = satellite_state.get('sun_angle', 0)
        efficiency = max(0, math.cos(math.radians(sun_angle)))
        self.solar_array_power = 1500 * efficiency + random.uniform(-20, 20)
        
        # Load varies with modes
        if satellite_state.get('mode') == SatelliteMode.NORMAL:
            self.load_power = 800 + random.uniform(-50, 50)
        elif satellite_state.get('mode') == SatelliteMode.LOW_POWER:
            self.load_power = 300 + random.uniform(-30, 30)
        else:
            self.load_power = 500 + random.uniform(-40, 40)
        
        # Net power
        net_power = self.solar_array_power - self.load_power
        
        # Battery update (simplified)
        if net_power > 0:
            self.battery_level = min(100, self.battery_level + (net_power / 3600) * 0.1)
            self.charge_current = net_power / self.battery_voltage
        else:
            discharge = abs(net_power) / 3600 * 0.1
            self.battery_level = max(0, self.battery_level - discharge)
            self.charge_current = -discharge / self.battery_voltage
        
        # Battery cycles increment when crossing thresholds
        if self.battery_level < 20:
            self.status = "LOW_POWER"
        else:
            self.status = "NOMINAL"
        
        # Temperature varies with load
        self.temperature = 25 + (self.load_power / 100) + random.uniform(-2, 3)
        self.power_consumption = self.load_power / 100
        
        # Battery voltage based on level
        self.battery_voltage = 24 + (self.battery_level / 100) * 6
    
    def get_telemetry(self) -> Dict:
        return {
            "level_percent": round(self.battery_level, 2),
            "voltage": round(self.battery_voltage, 2),
            "current_draw": round(self.load_power / self.battery_voltage, 2),
            "charge_rate": round(self.charge_current, 2),
            "solar_power_w": round(self.solar_array_power, 1),
            "load_power_w": round(self.load_power, 1),
            "temperature": round(self.temperature, 1),
            "cycles": self.cycles,
            "status": self.status
        }


class CommsSubsystem(Subsystem):
    """Communications System"""
    def __init__(self):
        super().__init__("COMMS")
        self.signal_strength = 85.0
        self.data_rate = 50.0
        self.bit_error_rate = 1e-9
        self.tx_power = 10.0
        self.rx_sensitivity = -95.0
        self.link_margin = 12.0
        self.antenna_gain = 15.0
    
    def update(self, satellite_state: Dict):
        # Signal degrades with distance
        distance = satellite_state.get('distance_to_ground', 1000)
        self.signal_strength = 100 - (distance / 50) + random.uniform(-5, 5)
        self.signal_strength = max(30, min(99, self.signal_strength))
        
        # Data rate varies with signal
        if self.signal_strength > 80:
            self.data_rate = 100 + random.uniform(-10, 10)
        elif self.signal_strength > 60:
            self.data_rate = 50 + random.uniform(-10, 10)
        else:
            self.data_rate = 10 + random.uniform(-5, 5)
        
        # Bit error rate
        self.bit_error_rate = 1e-12 * (100 / self.signal_strength)
        
        # Link margin
        self.link_margin = 10 + (self.signal_strength - 50) / 5
        
        # Temperature effect on amplifier
        self.temperature = 35 + (self.tx_power / 5) + random.uniform(-5, 10)
        self.power_consumption = self.tx_power * 2
    
    def get_telemetry(self) -> Dict:
        return {
            "signal_strength": round(self.signal_strength, 1),
            "data_rate_mbps": round(self.data_rate, 1),
            "bit_error_rate": f"{self.bit_error_rate:.2e}",
            "tx_power_w": round(self.tx_power, 2),
            "link_margin_db": round(self.link_margin, 1),
            "antenna_gain_dbi": self.antenna_gain,
            "temperature": round(self.temperature, 1),
            "status": self.status
        }


class ThermalSubsystem(Subsystem):
    """Thermal Control System"""
    def __init__(self):
        super().__init__("TCS")
        self.heater_power = 0.0
        self.radiator_temp = 10.0
        self.loop_temp = 20.0
        self.valve_position = 50.0
    
    def update(self, satellite_state: Dict):
        # External heat flux (sunlit vs eclipse)
        in_sunlight = satellite_state.get('in_sunlight', True)
        if in_sunlight:
            heat_flux = 1400 + random.uniform(-50, 50)
        else:
            heat_flux = -100 + random.uniform(-20, 20)
        
        # Temperature dynamics
        self.temperature = 20 + (heat_flux / 100) + random.uniform(-1, 2)
        self.temperature = max(-30, min(60, self.temperature))
        
        # Radiator temperature
        self.radiator_temp = self.temperature - 10 + random.uniform(-2, 2)
        
        # Loop temperature
        self.loop_temp = self.temperature + random.uniform(-2, 3)
        
        # Heater control
        if self.temperature < 10:
            self.heater_power = 100
            self.status = "HEATING"
        elif self.temperature > 40:
            self.heater_power = 0
            self.status = "COOLING"
        else:
            self.heater_power = 50
            self.status = "NOMINAL"
        
        self.power_consumption = self.heater_power / 100
    
    def get_telemetry(self) -> Dict:
        return {
            "main_bus": round(self.temperature, 1),
            "radiator": round(self.radiator_temp, 1),
            "coolant_loop": round(self.loop_temp, 1),
            "heater_power_w": round(self.heater_power, 1),
            "valve_position": round(self.valve_position, 1),
            "status": self.status
        }


class ProfessionalSatellite:
    """Advanced Satellite Simulator with realistic subsystems"""
    
    def __init__(self, name: str = "SAT-INSA-001", altitude_km: float = 550.0):
        self.name = name
        self.altitude = altitude_km * 1000
        self.orbit_radius = EarthConstants.RADIUS + self.altitude
        
        # Orbital calculations
        self.velocity = math.sqrt(EarthConstants.MU / self.orbit_radius)
        self.period = 2 * math.pi * math.sqrt(self.orbit_radius**3 / EarthConstants.MU)
        self.angular_velocity = (2 * math.pi) / self.period
        
        # Initial orbital position
        self.start_time = time.time()
        self.initial_angle = random.uniform(0, 360)
        
        # Subsystems
        self.adcs = ADCSSubsystem()
        self.power = PowerSubsystem()
        self.comms = CommsSubsystem()
        self.thermal = ThermalSubsystem()
        
        # Operational state
        self.mode = SatelliteMode.NORMAL
        self.packet_count = 0
        self.total_data_sent = 0
        
        # Ground station location (Addis Ababa, Ethiopia)
        self.ground_lat = 9.03
        self.ground_lon = 38.74
        self.ground_alt = 2355.0
        
        self.display_header()
    
    def display_header(self):
        """Display satellite initialization header"""
        print("\n" + "=" * 80)
        print("🛰️  PROFESSIONAL SATELLITE SIMULATOR".center(80))
        print("=" * 80)
        print(f"📡 Satellite: {self.name}")
        print(f"🌍 Orbit Altitude: {self.altitude/1000:.1f} km")
        print(f"🚀 Orbital Velocity: {self.velocity/1000:.2f} km/s")
        print(f"⏱️  Orbital Period: {self.period/60:.2f} minutes")
        print(f"🎯 Ground Station: Addis Ababa ({self.ground_lat}°, {self.ground_lon}°)")
        print("=" * 80)
        logger.info(f"Satellite {self.name} initialized successfully")
    
    def calculate_position(self, elapsed_time: float) -> Dict[str, float]:
        """Calculate precise orbital position"""
        angle = self.angular_velocity * elapsed_time
        angle_deg = math.degrees(angle) % 360
        
        # Convert polar to Cartesian
        x = self.orbit_radius * math.cos(angle) / 1000
        y = self.orbit_radius * math.sin(angle) / 1000
        
        # Calculate distance to ground station
        distance = math.sqrt(x**2 + y**2)
        
        return {
            "x_km": round(x, 1),
            "y_km": round(y, 1),
            "angle_rad": angle,
            "angle_deg": round(angle_deg, 2),
            "velocity_kms": round(self.velocity / 1000, 3),
            "distance_to_ground": round(distance, 1)
        }
    
    def calculate_sun_angle(self, angle_deg: float) -> float:
        """Calculate sun angle for power generation"""
        # Simplified: Sun is at 0° reference
        return abs(math.cos(math.radians(angle_deg))) * 180
    
    def determine_mode(self, battery_level: float) -> SatelliteMode:
        """Determine satellite operational mode"""
        if battery_level < 15:
            return SatelliteMode.LOW_POWER
        elif battery_level < 30:
            return SatelliteMode.SAFE
        else:
            return SatelliteMode.NORMAL
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate complete telemetry package"""
        elapsed = time.time() - self.start_time
        position = self.calculate_position(elapsed)
        
        # Update subsystems with satellite state
        satellite_state = {
            "mode": self.mode,
            "in_sunlight": (position['angle_deg'] % 360) < 180,
            "sun_angle": self.calculate_sun_angle(position['angle_deg']),
            "distance_to_ground": position['distance_to_ground']
        }
        
        # Update all subsystems
        self.adcs.update(satellite_state)
        self.power.update(satellite_state)
        self.comms.update(satellite_state)
        self.thermal.update(satellite_state)
        
        # Update operational mode
        self.mode = self.determine_mode(self.power.battery_level)
        
        # Calculate data volume
        self.total_data_sent += 2 * 1024  # ~2KB per packet
        
        telemetry = {
            "timestamp": datetime.now().isoformat(),
            "satellite_id": self.name,
            "packet_id": self.packet_count,
            "mode": self.mode.value,
            "orbit": {
                "altitude_km": round(self.altitude / 1000, 1),
                "velocity_kms": round(self.velocity / 1000, 3),
                "period_minutes": round(self.period / 60, 2),
                "completion_percent": round((elapsed % self.period) / self.period * 100, 1)
            },
            "position": position,
            "adcs": self.adcs.get_telemetry(),
            "power": self.power.get_telemetry(),
            "comms": self.comms.get_telemetry(),
            "thermal": self.thermal.get_telemetry(),
            "data_volume_mb": round(self.total_data_sent / (1024 * 1024), 2)
        }
        
        self.packet_count += 1
        return telemetry
    
    def broadcast(self, host: str = "127.0.0.1", port: int = 5005):
        """Main broadcast loop"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        logger.info(f"🚀 Broadcasting telemetry to {host}:{port}")
        
        try:
            last_status_time = time.time()
            
            while True:
                start = time.time()
                
                telemetry = self.generate_telemetry()
                message = json.dumps(telemetry)
                sock.sendto(message.encode(), (host, port))
                
                # Display status every second
                print(f"\r📡 PKT#{telemetry['packet_id']:6d} | "
                      f"📍 ({telemetry['position']['x_km']:6.0f}, {telemetry['position']['y_km']:6.0f}) km | "
                      f"🎯 {telemetry['position']['angle_deg']:6.1f}° | "
                      f"🔋 {telemetry['power']['level_percent']:5.1f}% | "
                      f"🌡️ {telemetry['thermal']['main_bus']:5.1f}°C | "
                      f"📶 {telemetry['comms']['signal_strength']:5.1f}% | "
                      f"🔧 {telemetry['mode']}", end="")
                
                # Maintain 1-second interval
                elapsed = time.time() - start
                time.sleep(max(0, 1 - elapsed))
                
        except KeyboardInterrupt:
            self.shutdown(sock)
        except Exception as e:
            logger.error(f"Broadcast error: {e}")
            self.shutdown(sock)
    
    def shutdown(self, sock: socket.socket):
        """Graceful shutdown"""
        print("\n\n" + "=" * 80)
        print("🛰️ SATELLITE DEORBIT REPORT".center(80))
        print("=" * 80)
        print(f"📊 Final Statistics:")
        print(f"   📦 Packets Sent: {self.packet_count}")
        print(f"   💾 Data Sent: {self.total_data_sent / (1024*1024):.2f} MB")
        print(f"   ⏱️  Runtime: {(time.time() - self.start_time):.1f} seconds")
        print(f"   🔋 Final Battery: {self.power.battery_level:.1f}%")
        print(f"   🌡️ Final Temperature: {self.thermal.temperature:.1f}°C")
        print("=" * 80)
        
        sock.close()
        logger.info("Satellite deorbit complete")


def main():
    """Main entry point"""
    import sys
    
    # Parse command line arguments
    port = 5005
    altitude = 550.0
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    
    satellite = ProfessionalSatellite(altitude_km=altitude)
    satellite.broadcast(port=port)


if __name__ == "__main__":
    main()
