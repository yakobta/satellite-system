#!/usr/bin/env python3
"""
ETRSS-1 Realistic Satellite Simulator - FIXED VERSION
Based on actual Ethiopian satellite orbital parameters
"""

import math
import random
import socket
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Real ETRSS-1 Orbital Parameters
ETRSS_1_DATA = {
    "name": "ETRSS-1",
    "norad_id": 44880,
    "altitude_km": 628.0,
    "inclination_deg": 97.84,
    "eccentricity": 0.00127,
    "period_seconds": 5800,
    "launch_date": "2019-12-20"
}

class ETRSS1Satellite:
    def __init__(self):
        self.name = ETRSS_1_DATA["name"]
        self.norad_id = ETRSS_1_DATA["norad_id"]
        self.altitude_km = ETRSS_1_DATA["altitude_km"]
        self.inclination = math.radians(ETRSS_1_DATA["inclination_deg"])
        
        self.earth_radius_km = 6371.0
        self.mu_earth = 398600.4418
        self.semi_major_axis_km = self.earth_radius_km + self.altitude_km
        self.orbital_velocity = math.sqrt(self.mu_earth / self.semi_major_axis_km)
        self.period_seconds = ETRSS_1_DATA["period_seconds"]
        self.angular_velocity = (2 * math.pi) / self.period_seconds
        
        self.start_time = time.time()
        self.packet_count = 0
        self.sock: Optional[socket.socket] = None
        
        # Battery starts at 100% and drains over time
        self.battery_level = 100.0
        self.battery_drain_rate = 0.05  # 0.05% per second (3% per minute)
        self.temperature = 20.0
        
        self._display_info()
    
    def _display_info(self):
        print("\n" + "=" * 70)
        print("🛰️  ETHIOPIA'S ETRSS-1 SATELLITE SIMULATOR".center(70))
        print("=" * 70)
        print(f"📡 Satellite: {self.name} (NORAD: {self.norad_id})")
        print(f"🇪🇹 Operator: Ethiopian Space Science and Technology Institute")
        print(f"🎯 Mission: Earth Observation / Remote Sensing")
        print(f"📍 Ground Station: Entoto Observatory, Addis Ababa")
        print("-" * 70)
        print(f"🌍 Orbit Altitude: {self.altitude_km} km (Sun-Synchronous)")
        print(f"📐 Inclination: {ETRSS_1_DATA['inclination_deg']}°")
        print(f"🚀 Orbital Velocity: {self.orbital_velocity:.2f} km/s")
        print(f"⏱️  Orbital Period: {self.period_seconds/60:.1f} minutes")
        print("=" * 70)
        print("\n📡 ETRSS-1 Telemetry Transmission Active")
        print("   Press Ctrl+C to stop\n")
    
    def calculate_position(self, elapsed_seconds: float) -> Dict[str, Any]:
        mean_anomaly = (2 * math.pi * elapsed_seconds / self.period_seconds) % (2 * math.pi)
        angle = mean_anomaly
        
        x_km = self.semi_major_axis_km * math.cos(angle)
        y_km = self.semi_major_axis_km * math.sin(angle)
        
        longitude = math.degrees(angle - self.angular_velocity * elapsed_seconds) % 360
        if longitude > 180:
            longitude -= 360
        
        latitude = math.degrees(math.asin(math.sin(angle) * math.sin(self.inclination)))
        
        is_visible = self._check_visibility(longitude, latitude)
        
        return {
            "x_km": round(x_km, 1),
            "y_km": round(y_km, 1),
            "latitude": round(latitude, 2),
            "longitude": round(longitude, 2),
            "angle_deg": round(math.degrees(angle), 2),
            "visible_from_ethiopia": is_visible,
        }
    
    def _check_visibility(self, longitude: float, latitude: float) -> bool:
        ground_lon_deg = 38.74
        ground_lat_deg = 9.03
        lon_diff = abs(longitude - ground_lon_deg)
        if lon_diff > 180:
            lon_diff = 360 - lon_diff
        angular_distance = math.sqrt(lon_diff**2 + (latitude - ground_lat_deg)**2)
        return angular_distance < 30
    
    def generate_telemetry(self, position: Dict) -> Dict[str, Any]:
        # Battery drains over time - THIS WILL CHANGE!
        self.battery_level = max(0, self.battery_level - self.battery_drain_rate)
        
        in_sunlight = (position["angle_deg"] % 360) < 180
        if in_sunlight:
            self.temperature = 22 + random.uniform(-2, 8)
        else:
            self.temperature = 15 + random.uniform(-3, 5)
        
        is_over_ethiopia = (position["latitude"] > -5 and position["latitude"] < 15 and 
                           abs(position["longitude"]) < 50)
        
        telemetry = {
            "timestamp": datetime.now().isoformat(),
            "satellite_id": self.name,
            "packet_id": self.packet_count,
            "position": position,
            "battery_level": round(self.battery_level, 1),
            "temperature": round(self.temperature, 1),
            "signal_strength": round(85 + random.uniform(-15, 10) + (10 if position["visible_from_ethiopia"] else -10), 1),
            "ground_contact": position["visible_from_ethiopia"],
            "camera_active": is_over_ethiopia
        }
        
        self.packet_count += 1
        return telemetry
    
    def broadcast(self, host: str = "127.0.0.1", port: int = 5005):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            while True:
                start_time = time.time()
                elapsed = time.time() - self.start_time
                
                position = self.calculate_position(elapsed)
                telemetry = self.generate_telemetry(position)
                
                # Send via UDP
                message = json.dumps(telemetry)
                self.sock.sendto(message.encode(), (host, port))
                
                # Display status - FIXED FORMAT!
                contact = "🟢 CONTACT" if position["visible_from_ethiopia"] else "⚫ NO CONTACT"
                print(f"\r{contact[:1]} ETRSS-1 | PKT#{telemetry['packet_id']:4d} | "
                      f"📍 ({position['x_km']:6.0f}, {position['y_km']:6.0f}) km | "
                      f"🌍 ({position['latitude']:5.1f}°, {position['longitude']:5.1f}°) | "
                      f"🔋 {telemetry['battery_level']:5.1f}% | "
                      f"🌡️ {telemetry['temperature']:5.1f}°C | "
                      f"📶 {telemetry['signal_strength']:5.1f}% | "
                      f"{contact}", end="")
                
                time.sleep(max(0, 1 - (time.time() - start_time)))
                
        except KeyboardInterrupt:
            self.shutdown()
    
    def shutdown(self):
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
        if self.sock:
            self.sock.close()


def main():
    satellite = ETRSS1Satellite()
    satellite.broadcast()


if __name__ == "__main__":
    main()
