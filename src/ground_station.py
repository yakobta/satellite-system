"""
Ground Station Module - Compatible with ETRSS-1 Satellite
Professional telemetry receiver with database storage
"""

import socket
import json
import time
import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GroundStation:
    def __init__(self, port: int = 5005):
        self.port = port
        self.buffer_size = 65536
        self.sock = None
        self.running = False
        self.packets_received = 0
        self.db_path = "data/telemetry.db"
        
        # Create data directory
        os.makedirs("data", exist_ok=True)
        self._init_database()
        
        print(f"✅ Ground Station initialized on port {self.port}")
    
    def _init_database(self):
        """Initialize database with correct schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Drop old table if exists
        cursor.execute("DROP TABLE IF EXISTS telemetry")
        
        # Create new table with correct schema
        cursor.execute('''
            CREATE TABLE telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                satellite_id TEXT,
                packet_id INTEGER,
                position_x REAL,
                position_y REAL,
                latitude REAL,
                longitude REAL,
                battery_level REAL,
                temperature REAL,
                signal_strength REAL,
                ground_contact INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_packet ON telemetry(packet_id)")
        cursor.execute("CREATE INDEX idx_time ON telemetry(timestamp)")
        
        conn.commit()
        conn.close()
        print("✅ Database initialized with correct schema")
    
    def start(self):
        """Start the ground station"""
        self.running = True
        
        # Create UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.settimeout(1.0)
        
        self._display_header()
        
        try:
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(self.buffer_size)
                    self._process_packet(data)
                except socket.timeout:
                    pass
                except json.JSONDecodeError:
                    pass
        except KeyboardInterrupt:
            self.shutdown()
    
    def _process_packet(self, data: bytes):
        """Process incoming telemetry packet"""
        try:
            telemetry = json.loads(data.decode())
            self.packets_received += 1
            
            # Extract data
            pos = telemetry.get('position', {})
            packet_id = telemetry.get('packet_id', 0)
            
            # Store in database
            self._store_telemetry({
                'timestamp': telemetry.get('timestamp', datetime.now().isoformat()),
                'satellite_id': telemetry.get('satellite_id', 'ETRSS-1'),
                'packet_id': packet_id,
                'position_x': pos.get('x_km', 0),
                'position_y': pos.get('y_km', 0),
                'latitude': pos.get('latitude', 0),
                'longitude': pos.get('longitude', 0),
                'battery_level': telemetry.get('battery_level', 0),
                'temperature': telemetry.get('temperature', 0),
                'signal_strength': telemetry.get('signal_strength', 0),
                'ground_contact': 1 if telemetry.get('ground_contact', False) else 0
            })
            
            # Display
            self._display_telemetry(telemetry)
            
        except Exception as e:
            print(f"⚠️ Error processing packet: {e}")
    
    def _store_telemetry(self, data: dict):
        """Store telemetry in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO telemetry (
                    timestamp, satellite_id, packet_id,
                    position_x, position_y, latitude, longitude,
                    battery_level, temperature, signal_strength, ground_contact
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['timestamp'],
                data['satellite_id'],
                data['packet_id'],
                data['position_x'],
                data['position_y'],
                data['latitude'],
                data['longitude'],
                data['battery_level'],
                data['temperature'],
                data['signal_strength'],
                data['ground_contact']
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ DB error: {e}")
    
    def _display_header(self):
        """Display header"""
        print("\n" + "="*80)
        print("🛰️  ETRSS-1 GROUND STATION".center(80))
        print("="*80)
        print(f"📡 Location: Entoto Observatory, Ethiopia")
        print(f"📡 Listening on: 0.0.0.0:{self.port}")
        print(f"💾 Database: {self.db_path}")
        print("="*80)
        print(f"{'ID':>6} | {'Time':>12} | {'Position (km)':>20} | {'Battery':>8} | {'Temp':>6} | {'Signal':>6}")
        print("-"*80)
    
    def _display_telemetry(self, telemetry: dict):
        """Display telemetry"""
        pos = telemetry.get('position', {})
        ts = telemetry.get('timestamp', '')
        time_str = ts.split('T')[1][:8] if 'T' in ts else ''
        
        contact = "🟢" if telemetry.get('ground_contact', False) else "⚫"
        
        print(f"{telemetry.get('packet_id', 0):6d} | {time_str:>12} | "
              f"({pos.get('x_km', 0):6.0f}, {pos.get('y_km', 0):6.0f}) | "
              f"{contact} {telemetry.get('battery_level', 0):5.1f}% | "
              f"{telemetry.get('temperature', 0):5.1f}°C | "
              f"{telemetry.get('signal_strength', 0):5.1f}%")
    
    def shutdown(self):
        """Shutdown"""
        self.running = False
        print(f"\n📊 Packets Received: {self.packets_received}")
        if self.sock:
            self.sock.close()


def main():
    station = GroundStation()
    station.start()

if __name__ == "__main__":
    main()
