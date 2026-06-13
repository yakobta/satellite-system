"""
Satellite Simulator Module
Professional satellite simulation with realistic orbital mechanics
"""

import math
import random
import socket
import json
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

from src.telemetry import (
    TelemetryPacket, PositionData, BatteryData, 
    ThermalData, CommsData, SatelliteMode, SubsystemStatus
)
from src.config import config
import logging

logger = logging.getLogger(__name__)


class Satellite:
    """
    Professional Satellite Simulator
    Simulates orbital mechanics, telemetry generation, and data transmission
    """
    
    def __init__(self, name: Optional[str] = None):
        self.name = name or config.satellite.name
        
        # Convert values to float (they might come as strings from YAML)
        earth_radius_km = float(config.orbital.earth_radius_km)
        self.altitude_km = float(config.orbital.default_altitude_km)
        self.orbit_radius_km = earth_radius_km + self.altitude_km
        
        # Orbital calculations - convert to float to avoid type errors
        gravitational_parameter = float(config.orbital.gravitational_parameter)
        self.velocity_kms = math.sqrt(gravitational_parameter / self.orbit_radius_km)
        self.period_seconds = 2 * math.pi * math.sqrt(
            self.orbit_radius_km**3 / gravitational_parameter
        )
        self.angular_velocity = (2 * math.pi) / self.period_seconds
        
        # State variables
        self.start_time = time.time()
        self.packet_count = 0
        self.running = False
        self.sock: Optional[socket.socket] = None
        
        # Telemetry data
        self.telemetry = TelemetryPacket(satellite_id=self.name)
        
        logger.info(f"Satellite {self.name} initialized")
        logger.info(f"  Orbit Altitude: {self.altitude_km:.1f} km")
        logger.info(f"  Orbital Velocity: {self.velocity_kms:.2f} km/s")
        logger.info(f"  Orbital Period: {self.period_seconds/60:.2f} minutes")
    
    def calculate_position(self, elapsed_seconds: float) -> PositionData:
        """Calculate orbital position using Keplerian motion"""
        angle_rad = self.angular_velocity * elapsed_seconds
        angle_deg = math.degrees(angle_rad) % 360
        
        # Circular orbit position (2D projection)
        x_km = self.orbit_radius_km * math.cos(angle_rad)
        y_km = self.orbit_radius_km * math.sin(angle_rad)
        
        # Simple latitude/longitude calculation
        latitude = math.degrees(math.asin(math.sin(angle_rad) * math.sin(math.radians(45))))
        longitude = (angle_deg - 180) % 360 - 180
        
        return PositionData(
            x_km=round(x_km, 1),
            y_km=round(y_km, 1),
            altitude_km=self.altitude_km,
            velocity_kms=round(self.velocity_kms, 3),
            angle_deg=round(angle_deg, 2),
            latitude_deg=round(latitude, 2),
            longitude_deg=round(longitude, 2)
        )
    
    def update_subsystems(self, in_sunlight: bool):
        """Update all subsystem telemetry"""
        
        # Convert to float for calculations
        solar_panel_w = float(config.satellite.solar_panel_w)
        power_consumption_w = float(config.satellite.power_consumption_w)
        
        # Battery update
        if in_sunlight:
            charge = solar_panel_w / 3600
            self.telemetry.battery.level_percent = min(
                100, self.telemetry.battery.level_percent + charge
            )
            self.telemetry.battery.charge_rate_w = solar_panel_w
        else:
            discharge = power_consumption_w / 3600
            self.telemetry.battery.level_percent = max(
                0, self.telemetry.battery.level_percent - discharge
            )
            self.telemetry.battery.charge_rate_w = 0
        
        # Battery voltage based on level
        self.telemetry.battery.voltage_v = 24 + (self.telemetry.battery.level_percent / 100) * 6
        self.telemetry.battery.current_a = power_consumption_w / 28
        
        # Temperature simulation
        base_temp = 20 + (10 if in_sunlight else -5)
        self.telemetry.thermal.main_bus_c = base_temp + random.uniform(-2, 3)
        self.telemetry.thermal.payload_c = base_temp - 5 + random.uniform(-2, 2)
        self.telemetry.thermal.battery_c = base_temp + 3 + random.uniform(-1, 2)
        self.telemetry.thermal.transmitter_c = base_temp + 15 + random.uniform(-3, 5)
        
        # Communications signal strength
        signal_base = 70 + (20 if in_sunlight else 0)
        self.telemetry.comms.signal_strength_percent = signal_base + random.uniform(-10, 10)
        self.telemetry.comms.signal_strength_percent = max(30, min(99, self.telemetry.comms.signal_strength_percent))
        
        # Data rate varies with signal strength
        self.telemetry.comms.data_rate_mbps = 10 + (self.telemetry.comms.signal_strength_percent / 100) * 90
        self.telemetry.comms.link_margin_db = 5 + (self.telemetry.comms.signal_strength_percent - 50) / 5
        
        # Determine operational mode based on battery
        if self.telemetry.battery.level_percent < 15:
            self.telemetry.mode = SatelliteMode.LOW_POWER
        elif self.telemetry.battery.level_percent < 30:
            self.telemetry.mode = SatelliteMode.SAFE
        else:
            self.telemetry.mode = SatelliteMode.NORMAL
        
        # Update statuses
        if self.telemetry.battery.level_percent < 10:
            self.telemetry.battery.status = SubsystemStatus.CRITICAL
        elif self.telemetry.battery.level_percent < 25:
            self.telemetry.battery.status = SubsystemStatus.DEGRADED
        else:
            self.telemetry.battery.status = SubsystemStatus.NOMINAL
    
    def generate_telemetry(self) -> TelemetryPacket:
        """Generate complete telemetry packet"""
        elapsed = time.time() - self.start_time
        
        # Calculate position
        position = self.calculate_position(elapsed)
        
        # Determine if in sunlight (simplified: 50% of orbit)
        in_sunlight = (elapsed % self.period_seconds) < (self.period_seconds / 2)
        
        # Update subsystems
        self.update_subsystems(in_sunlight)
        
        # Update position in telemetry
        self.telemetry.position = position
        self.telemetry.packet_id = self.packet_count
        self.telemetry.timestamp = datetime.now()
        self.telemetry.comms.packets_sent = self.packet_count
        
        self.packet_count += 1
        
        return self.telemetry
    
    def broadcast(self, host: str = "127.0.0.1", port: int = 5005):
        """Main broadcast loop"""
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        logger.info(f"🚀 Broadcasting telemetry to {host}:{port}")
        print("\n" + "="*80)
        print("🛰️  SATELLITE TELEMETRY TRANSMISSION".center(80))
        print("="*80)
        
        try:
            while self.running:
                start_time = time.time()
                
                # Generate and send telemetry
                telemetry = self.generate_telemetry()
                message = telemetry.to_json()
                self.sock.sendto(message.encode(), (host, port))
                
                # Display status
                self._display_status(telemetry)
                
                # Maintain 1-second interval
                elapsed = time.time() - start_time
                time.sleep(max(0, 1 - elapsed))
                
        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            logger.error(f"Broadcast error: {e}")
            self.shutdown()
    
    def _display_status(self, telemetry: TelemetryPacket):
        """Display real-time status"""
        print(f"\r📡 PKT#{telemetry.packet_id:6d} | "
              f"📍 ({telemetry.position.x_km:6.0f}, {telemetry.position.y_km:6.0f}) km | "
              f"🎯 {telemetry.position.angle_deg:6.1f}° | "
              f"🔋 {telemetry.battery.level_percent:5.1f}% | "
              f"🌡️ {telemetry.thermal.main_bus_c:5.1f}°C | "
              f"📶 {telemetry.comms.signal_strength_percent:5.1f}% | "
              f"🔧 {telemetry.mode.value}", end="")
    
    def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        elapsed = time.time() - self.start_time
        
        print("\n\n" + "="*80)
        print("🛰️  SATELLITE DEORBIT REPORT".center(80))
        print("="*80)
        print(f"📊 Mission Statistics:")
        print(f"   📦 Packets Transmitted: {self.packet_count}")
        print(f"   ⏱️  Mission Duration: {elapsed:.1f} seconds")
        print(f"   🔋 Final Battery: {self.telemetry.battery.level_percent:.1f}%")
        print(f"   🌡️ Final Temperature: {self.telemetry.thermal.main_bus_c:.1f}°C")
        print(f"   📶 Avg Signal Strength: {self.telemetry.comms.signal_strength_percent:.1f}%")
        print("="*80)
        
        if self.sock:
            self.sock.close()
        
        logger.info("Satellite deorbit complete")


def main():
    """Entry point for satellite simulator"""
    import sys
    
    port = 5005
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    
    satellite = Satellite()
    satellite.broadcast(port=port)


if __name__ == "__main__":
    main()
