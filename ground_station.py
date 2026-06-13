#!/usr/bin/env python3
"""
Professional Ground Station - Mission Control Center
Advanced telemetry receiver with data logging, anomaly detection, and real-time visualization
Author: Space Systems Engineer
Version: 2.0.0
"""

import socket
import json
import time
import logging
import threading
import sqlite3
from datetime import datetime
from collections import deque
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('ground_station.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SatelliteStatus(Enum):
    """Satellite operational status"""
    NOMINAL = "✅ NOMINAL"
    DEGRADED = "⚠️ DEGRADED"
    CRITICAL = "🔴 CRITICAL"
    SIGNAL_LOST = "📡 SIGNAL LOST"


@dataclass
class TelemetryData:
    """Structured telemetry data container"""
    timestamp: str
    packet_id: int
    satellite_id: str
    position_x: float
    position_y: float
    angle_deg: float
    battery_level: float
    temperature: float
    signal_strength: float
    data_rate: float


class TelemetryDatabase:
    """SQLite database for telemetry storage and analysis"""
    
    def __init__(self, db_path: str = "telemetry.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                packet_id INTEGER,
                satellite_id TEXT,
                position_x REAL,
                position_y REAL,
                angle_deg REAL,
                battery_level REAL,
                temperature REAL,
                signal_strength REAL,
                data_rate REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON telemetry(timestamp)
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized: telemetry.db")
    
    def insert_telemetry(self, data: TelemetryData):
        """Insert telemetry data into database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO telemetry (
                    timestamp, packet_id, satellite_id, position_x, position_y,
                    angle_deg, battery_level, temperature, signal_strength, data_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.timestamp, data.packet_id, data.satellite_id,
                data.position_x, data.position_y, data.angle_deg,
                data.battery_level, data.temperature, data.signal_strength, data.data_rate
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Database insert error: {e}")
    
    def get_statistics(self) -> Dict:
        """Get telemetry statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_packets,
                AVG(battery_level) as avg_battery,
                AVG(temperature) as avg_temp,
                AVG(signal_strength) as avg_signal,
                MIN(battery_level) as min_battery,
                MAX(temperature) as max_temp
            FROM telemetry
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            "total_packets": result[0] or 0,
            "avg_battery": round(result[1] or 0, 2),
            "avg_temperature": round(result[2] or 0, 1),
            "avg_signal": round(result[3] or 0, 2),
            "min_battery": round(result[4] or 0, 2),
            "max_temperature": round(result[5] or 0, 1)
        }


class GroundStation:
    """Professional Ground Station with advanced features"""
    
    def __init__(self, port: int = 5005, buffer_size: int = 65536):
        self.port = port
        self.buffer_size = buffer_size
        self.sock: Optional[socket.socket] = None
        self.packets_received = 0
        self.packets_lost = 0
        self.expected_packet_id = 0
        self.packet_history = deque(maxlen=1000)
        self.running = False
        self.db = TelemetryDatabase()
        self.anomaly_callbacks = []
        
        # Performance metrics
        self.start_time = None
        self.last_packet_time = None
        self.data_rate_history = deque(maxlen=60)
        
        logger.info(f"🚀 Ground Station initialized on port {port}")
    
    def start(self):
        """Start the ground station"""
        self.running = True
        self.start_time = time.time()
        
        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.settimeout(1.0)
        
        self.display_header()
        
        try:
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(self.buffer_size)
                    self.process_packet(data, addr)
                    
                except socket.timeout:
                    self.check_connection_status()
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {e}")
                    
        except KeyboardInterrupt:
            self.shutdown()
    
    def process_packet(self, data: bytes, addr: tuple):
        """Process incoming telemetry packet"""
        self.packets_received += 1
        self.last_packet_time = time.time()
        
        # Parse telemetry
        telemetry = json.loads(data.decode())
        
        # Validate packet sequence
        current_id = telemetry.get('packet_id', 0)
        if current_id != self.expected_packet_id and self.expected_packet_id > 0:
            lost = current_id - self.expected_packet_id
            self.packets_lost += lost
            logger.warning(f"Packet loss detected: {lost} packets missing")
        
        self.expected_packet_id = current_id + 1
        
        # Create structured data
        telemetry_data = TelemetryData(
            timestamp=telemetry.get('timestamp', datetime.now().isoformat()),
            packet_id=current_id,
            satellite_id=telemetry.get('satellite_id', 'UNKNOWN'),
            position_x=telemetry.get('position', {}).get('x_km', 0),
            position_y=telemetry.get('position', {}).get('y_km', 0),
            angle_deg=telemetry.get('position', {}).get('angle_deg', 0),
            battery_level=telemetry.get('battery_system', {}).get('level_percent', 0),
            temperature=telemetry.get('thermal_system', {}).get('main_bus', 0),
            signal_strength=telemetry.get('communication', {}).get('signal_strength', 0),
            data_rate=telemetry.get('communication', {}).get('data_rate_mbps', 0)
        )
        
        # Store in database
        self.db.insert_telemetry(telemetry_data)
        
        # Store in history
        self.packet_history.append(telemetry_data)
        
        # Calculate data rate
        elapsed = time.time() - self.start_time
        rate = self.packets_received / elapsed if elapsed > 0 else 0
        self.data_rate_history.append(rate)
        
        # Display telemetry
        self.display_telemetry(telemetry_data, addr, rate)
        
        # Detect anomalies
        self.detect_anomalies(telemetry_data)
    
    def display_header(self):
        """Display professional header"""
        print("\n" + "=" * 80)
        print("🛰️  PROFESSIONAL GROUND STATION".center(80))
        print("=" * 80)
        print(f"📡 Listening on: 0.0.0.0:{self.port}")
        print(f"💾 Database: telemetry.db")
        print(f"📊 Log file: ground_station.log")
        print("=" * 80)
        print(f"{'ID':>4} | {'Time':>12} | {'Position (km)':>20} | {'Battery':>7} | {'Temp':>6} | {'Signal':>6} | {'Rate':>6}")
        print("-" * 80)
    
    def display_telemetry(self, data: TelemetryData, addr: tuple, rate: float):
        """Display formatted telemetry"""
        # Parse time
        time_str = data.timestamp.split('T')[1].split('.')[0] if 'T' in data.timestamp else data.timestamp
        
        # Status indicators
        battery_icon = "🔋" if data.battery_level > 30 else "⚠️"
        signal_icon = "📶" if data.signal_strength > 50 else "📡⚠️"
        
        print(f"{data.packet_id:>4} | {time_str:>12} | ({data.position_x:>6.0f}, {data.position_y:>6.0f}) | "
              f"{battery_icon} {data.battery_level:>5.1f}% | {data.temperature:>5.1f}°C | "
              f"{signal_icon} {data.signal_strength:>5.1f}% | {rate:>5.2f} pkt/s")
    
    def detect_anomalies(self, data: TelemetryData):
        """Detect anomalies in telemetry"""
        anomalies = []
        
        # Battery critical
        if data.battery_level < 20:
            anomalies.append(f"CRITICAL BATTERY: {data.battery_level}%")
        elif data.battery_level < 35:
            anomalies.append(f"Low Battery: {data.battery_level}%")
        
        # Temperature anomaly
        if data.temperature > 50:
            anomalies.append(f"OVERHEATING: {data.temperature}°C")
        elif data.temperature < -10:
            anomalies.append(f"TOO COLD: {data.temperature}°C")
        
        # Signal weak
        if data.signal_strength < 60:
            anomalies.append(f"Weak Signal: {data.signal_strength}%")
        
        # Packet loss
        if self.packets_lost > 0:
            loss_rate = (self.packets_lost / self.packets_received) * 100
            if loss_rate > 10:
                anomalies.append(f"High Packet Loss: {loss_rate:.1f}%")
        
        # Report anomalies
        for anomaly in anomalies:
            logger.warning(f"🚨 ANOMALY: {anomaly}")
    
    def check_connection_status(self):
        """Check if satellite signal is lost"""
        if self.packets_received > 0 and self.last_packet_time:
            time_since_last = time.time() - self.last_packet_time
            if time_since_last > 10:
                logger.warning(f"Signal lost for {time_since_last:.0f} seconds")
    
    def get_status(self) -> SatelliteStatus:
        """Get current satellite status"""
        if self.packets_received == 0:
            return SatelliteStatus.SIGNAL_LOST
        
        if self.last_packet_time:
            time_since_last = time.time() - self.last_packet_time
            if time_since_last > 15:
                return SatelliteStatus.SIGNAL_LOST
        
        # Check recent telemetry
        if len(self.packet_history) > 0:
            latest = self.packet_history[-1]
            if latest.battery_level < 20 or latest.temperature > 55:
                return SatelliteStatus.CRITICAL
            elif latest.battery_level < 35 or latest.temperature > 45:
                return SatelliteStatus.DEGRADED
        
        return SatelliteStatus.NOMINAL
    
    def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        
        # Calculate statistics
        elapsed = time.time() - self.start_time if self.start_time else 0
        stats = self.db.get_statistics()
        
        print("\n" + "=" * 80)
        print("📊 GROUND STATION SHUTDOWN REPORT".center(80))
        print("=" * 80)
        print(f"⏱️  Run Time: {elapsed:.1f} seconds")
        print(f"📦 Packets Received: {self.packets_received}")
        print(f"⚠️ Packets Lost: {self.packets_lost}")
        
        loss_rate = (self.packets_lost / max(1, self.packets_received + self.packets_lost)) * 100
        print(f"📉 Packet Loss Rate: {loss_rate:.1f}%")
        print(f"📊 Average Data Rate: {self.packets_received / max(1, elapsed):.2f} pkt/s")
        print(f"\n📈 DATABASE STATISTICS:")
        print(f"   Total Packets: {stats['total_packets']}")
        print(f"   Avg Battery: {stats['avg_battery']}%")
        print(f"   Avg Temperature: {stats['avg_temperature']}°C")
        print(f"   Avg Signal: {stats['avg_signal']}%")
        print(f"   Min Battery: {stats['min_battery']}%")
        print(f"   Max Temperature: {stats['max_temperature']}°C")
        
        print(f"\n🛰️ Final Status: {self.get_status().value}")
        print("=" * 80)
        
        if self.sock:
            self.sock.close()
        
        logger.info("Ground Station shutdown complete")


def main():
    """Main entry point"""
    import sys
    
    port = 5005
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            logger.error(f"Invalid port: {sys.argv[1]}, using default 5005")
    
    station = GroundStation(port=port)
    station.start()


if __name__ == "__main__":
    main()
