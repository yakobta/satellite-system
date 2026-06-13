"""
ETRSS-1 Realistic Satellite Simulator
Based on actual Ethiopian satellite orbital parameters
"""

import math
import random
import socket
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Real ETRSS-1 Orbital Parameters (from official data)
ETRSS_1_DATA = {
    "name": "ETRSS-1",
    "norad_id": 44880,
    "altitude_km": 628.0,
    "inclination_deg": 97.84,
    "eccentricity": 0.00127,
    "mean_motion_rev_per_day": 14.86355,
    "period_seconds": 5800,  # ~96.6 minutes
    "launch_date": "2019-12-20"
}

class ETRSS1Satellite:
    """
    Realistic ETRSS-1 Satellite Simulator
    Uses actual Ethiopian satellite orbital parameters
    """
    
    def __init__(self):
        self.name = ETRSS_1_DATA["name"]
        self.norad_id = ETRSS_1_DATA["norad_id"]
        self.altitude_km = ETRSS_1_DATA["altitude_km"]
        self.inclination = math.radians(ETRSS_1_DATA["inclination_deg"])
        self.eccentricity = ETRSS_1_DATA["eccentricity"]
        
        # Earth constants
        self.earth_radius_km = 6371.0
        self.mu_earth = 398600.4418  # km³/s²
        
        # Calculate orbital parameters
        self.semi_major_axis_km = self.earth_radius_km + self.altitude_km
        self.orbital_velocity = math.sqrt(self.mu_earth / self.semi_major_axis_km)
        self.period_seconds = ETRSS_1_DATA["period_seconds"]
        self.angular_velocity = (2 * math.pi) / self.period_seconds
        
        # Ground station location (Entoto Observatory)
        self.ground_lat = math.radians(9.03)
        self.ground_lon = math.radians(38.74)
        
        self.start_time = time.time()
        self.packet_count = 0
        self.running = False
        self.sock: Optional[socket.socket] = None
        
        # Telemetry state
        self.battery_level = 100.0
        self.temperature = 20.0
        self.solar_panel_power = 150.0  # watts
        
        self._display_info()
    
    def _display_info(self):
        """Display satellite information"""
        print("\n" + "=" * 70)
        print("🛰️  ETHIOPIA'S ETRSS-1 SATELLITE SIMULATOR".center(70))
        print("=" * 70)
        print(f"📡 Satellite: {self.name} (NORAD: {self.norad_id})")
        print(f"🇪🇹 Operator: Ethiopian Space Science and Technology Institute")
        print(f"📅 Launch Date: {ETRSS_1_DATA['launch_date']}")
        print(f"🎯 Mission: Earth Observation / Remote Sensing")
        print(f"📍 Ground Station: Entoto Observatory, Addis Ababa")
        print("-" * 70)
        print(f"🌍 Orbit Altitude: {self.altitude_km} km (Sun-Synchronous)")
        print(f"📐 Inclination: {ETRSS_1_DATA['inclination_deg']}°")
        print(f"🚀 Orbital Velocity: {self.orbital_velocity:.2f} km/s")
        print(f"⏱️  Orbital Period: {self.period_seconds/60:.1f} minutes")
        print(f"📸 Resolution: 13.7 meters | Bands: 4 | Revisit: 4 days")
        print("=" * 70)
    
    def calculate_position(self, elapsed_seconds: float) -> Dict[str, Any]:
        """
        Calculate ETRSS-1 orbital position using real parameters
        Sun-Synchronous Orbit calculation
        """
        # Mean anomaly progression
        mean_anomaly = (2 * math.pi * elapsed_seconds / self.period_seconds) % (2 * math.pi)
        
        # Simplified orbit calculation for SSO
        angle = mean_anomaly
        
        # Convert to Cartesian coordinates (Earth-centered)
        x_km = self.semi_major_axis_km * math.cos(angle)
        y_km = self.semi_major_axis_km * math.sin(angle)
        
        # Apply inclination for 3D effect
        z_km = x_km * math.sin(self.inclination)
        x_km_adjusted = x_km * math.cos(self.inclination)
        
        # Calculate sub-satellite point (latitude/longitude)
        longitude = math.degrees(angle - self.angular_velocity * elapsed_seconds) % 360
        if longitude > 180:
            longitude -= 360
            
        # Simplified latitude calculation for SSO
        latitude = math.degrees(math.asin(math.sin(angle) * math.sin(self.inclination)))
        
        # Check if satellite is visible from Entoto
        is_visible = self._check_visibility(longitude, latitude)
        
        return {
            "x_km": round(x_km, 1),
            "y_km": round(y_km, 1),
            "z_km": round(z_km, 1),
            "latitude": round(latitude, 2),
            "longitude": round(longitude, 2),
            "altitude_km": self.altitude_km,
            "velocity_kms": round(self.orbital_velocity, 3),
            "angle_deg": round(math.degrees(angle), 2),
            "visible_from_ethiopia": is_visible,
            "mean_anomaly_deg": round(math.degrees(mean_anomaly), 2)
        }
    
    def _check_visibility(self, longitude: float, latitude: float) -> bool:
        """Check if satellite is visible from Entoto Ground Station"""
        # Simple visibility check based on angular separation
        ground_lon_deg = 38.74
        ground_lat_deg = 9.03
        
        # Calculate great-circle distance
        lon_diff = abs(longitude - ground_lon_deg)
        if lon_diff > 180:
            lon_diff = 360 - lon_diff
            
        # Rough visibility cone (~30 degrees from ground station)
        angular_distance = math.sqrt(lon_diff**2 + (latitude - ground_lat_deg)**2)
        
        return angular_distance < 30
    
    def generate_telemetry(self, position: Dict) -> Dict[str, Any]:
        """Generate realistic telemetry based on ETRSS-1 subsystems"""
        
        # Battery simulation (charge/discharge based on sunlight)
        in_sunlight = (position["angle_deg"] % 360) < 180
        if in_sunlight:
            self.battery_level = min(100, self.battery_level + 0.05)
        else:
            self.battery_level = max(0, self.battery_level - 0.03)
        
        # Temperature varies with sunlight
        self.temperature = 20 + (10 if in_sunlight else -5) + random.uniform(-2, 3)
        
        # Camera status (active when over target areas)
        is_over_ethiopia = (position["latitude"] > -5 and position["latitude"] < 15 and 
                           abs(position["longitude"]) < 50)
        
        telemetry = {
            "timestamp": datetime.now().isoformat(),
            "satellite_id": self.name,
            "norad_id": self.norad_id,
            "packet_id": self.packet_count,
            "operator": "ESSTI",
            "mission": "Earth Observation",
            
            "orbit": {
                "altitude_km": self.altitude_km,
                "velocity_kms": round(self.orbital_velocity, 3),
                "inclination_deg": ETRSS_1_DATA["inclination_deg"],
                "period_minutes": round(self.period_seconds / 60, 1),
                "completion_percent": round((time.time() - self.start_time) % self.period_seconds / self.period_seconds * 100, 1)
            },
            
            "position": position,
            
            "power_subsystem": {
                "battery_level_percent": round(self.battery_level, 2),
                "solar_panel_power_w": round(self.solar_panel_power * (1.5 if in_sunlight else 0.2), 1),
                "voltage_v": round(28.0 + random.uniform(-0.5, 0.5), 2),
                "current_a": round(12.5 + random.uniform(-1, 2), 2),
                "in_sunlight": in_sunlight
            },
            
            "thermal_subsystem": {
                "main_bus_c": round(self.temperature, 1),
                "payload_c": round(self.temperature - 2 + random.uniform(-1, 2), 1),
                "battery_c": round(self.temperature + 3 + random.uniform(-1, 2), 1)
            },
            
            "payload": {
                "camera_status": "IMAGING" if is_over_ethiopia else "STANDBY",
                "spatial_resolution_m": 13.7,
                "spectral_bands": 4,
                "swath_width_km": 87.3,
                "images_captured": int(self.packet_count * 0.1)
            },
            
            "communications": {
                "signal_strength_percent": round(85 + random.uniform(-15, 10) + (10 if position["visible_from_ethiopia"] else -10), 1),
                "data_rate_mbps": round(50 + random.uniform(-20, 20), 2),
                "link_status": "ACTIVE" if position["visible_from_ethiopia"] else "STANDBY"
            },
            
            "status": {
                "operational_mode": "NOMINAL",
                "health": "GOOD",
                "ground_contact": position["visible_from_ethiopia"]
            }
        }
        
        self.packet_count += 1
        return telemetry
    
    def broadcast(self, host: str = "127.0.0.1", port: int = 5005):
        """Broadcast ETRSS-1 telemetry over UDP"""
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        logger.info(f"🚀 ETRSS-1 broadcasting to {host}:{port}")
        print("\n📡 ETRSS-1 Telemetry Transmission Active")
        print("   Press Ctrl+C to stop\n")
        
        try:
            while self.running:
                start_time = time.time()
                elapsed = time.time() - self.start_time
                
                # Calculate position using real orbital parameters
                position = self.calculate_position(elapsed)
                
                # Generate telemetry
                telemetry = self.generate_telemetry(position)
                
                # Send via UDP
                message = json.dumps(telemetry)
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
    
    def _display_status(self, telemetry: Dict):
        """Display real-time ETRSS-1 status"""
        pos = telemetry["position"]
        power = telemetry["power_subsystem"]
        
        # Status indicator
        contact_indicator = "🟢" if pos["visible_from_ethiopia"] else "⚫"
        
        print(f"\r{contact_indicator} ETRSS-1 | PKT#{telemetry['packet_id']:5d} | "
              f"📍 ({pos['x_km']:6.0f}, {pos['y_km']:6.0f}) km | "
              f"🌍 ({pos['latitude']:5.1f}°, {pos['longitude']:5.1f}°) | "
              f"🔋 {power['battery_level_percent']:5.1f}% | "
              f"🌡️ {telemetry['thermal_subsystem']['main_bus_c']:5.1f}°C | "
              f"📶 {telemetry['communications']['signal_strength_percent']:5.1f}% | "
              f"{'📡 CONTACT' if pos['visible_from_ethiopia'] else '---'}", end="")
    
    def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        elapsed = time.time() - self.start_time
        
        print("\n\n" + "=" * 70)
        print("🛰️  ETRSS-1 MISSION REPORT".center(70))
        print("=" * 70)
        print(f"📊 Mission Statistics:")
        print(f"   📦 Telemetry Packets: {self.packet_count}")
        print(f"   ⏱️  Mission Duration: {elapsed:.1f} seconds")
        print(f"   🔋 Final Battery: {self.battery_level:.1f}%")
        print(f"   🌡️ Final Temperature: {self.temperature:.1f}°C")
        print("=" * 70)
        print("🇪🇹 Ethiopian Space Science and Technology Institute")
        print("🛰️  ETRSS-1 - Ethiopia's First Satellite")
        print("=" * 70)
        
        if self.sock:
            self.sock.close()
        
        logger.info("ETRSS-1 simulation complete")


def main():
    """Entry point for ETRSS-1 simulator"""
    import sys
    
    port = 5005
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    
    satellite = ETRSS1Satellite()
    satellite.broadcast(port=port)


if __name__ == "__main__":
    main()
