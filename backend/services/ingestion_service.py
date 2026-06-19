"""
Data Ingestion Service - Receives and processes telemetry data
"""

import socket
import json
import sys
import os
import time
from datetime import datetime
from threading import Thread

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_service import DatabaseService

class IngestionService:
    def __init__(self, port=5005):
        self.port = port
        self.db = DatabaseService()
        self.running = False
        self.sock = None
        self.packet_count = 0
    
    def start(self):
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.settimeout(1.0)
        
        print(f"📡 Ingestion Service started on port {self.port}")
        print(f"💾 Saving to: {self.db.db_path}")
        print("-" * 60)
        
        try:
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(65536)
                    telemetry = json.loads(data.decode())
                    self._process_telemetry(telemetry)
                except socket.timeout:
                    continue
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON error: {e}")
                except Exception as e:
                    print(f"⚠️ Error: {e}")
                    
        except KeyboardInterrupt:
            self.stop()
    
    def _process_telemetry(self, telemetry):
        """Process and store telemetry"""
        self.packet_count += 1
        
        # Extract data
        pos = telemetry.get('position', {})
        
        record = {
            'timestamp': telemetry.get('timestamp', datetime.now().isoformat()),
            'satellite_id': telemetry.get('satellite_id', 'ETRSS-1'),
            'packet_id': telemetry.get('packet_id', self.packet_count),
            'position_x': pos.get('x_km', 0),
            'position_y': pos.get('y_km', 0),
            'latitude': pos.get('latitude', 0),
            'longitude': pos.get('longitude', 0),
            'battery_level': telemetry.get('battery_level', 0),
            'temperature': telemetry.get('temperature', 0),
            'signal_strength': telemetry.get('signal_strength', 0),
            'ground_contact': telemetry.get('ground_contact', False)
        }
        
        # Save to database
        record_id = self.db.insert_telemetry(record)
        
        # Display
        contact = "🟢" if record['ground_contact'] else "⚫"
        print(f"PKT#{record['packet_id']:6d} | "
              f"({record['position_x']:6.0f}, {record['position_y']:6.0f}) | "
              f"{contact} {record['battery_level']:5.1f}% | "
              f"{record['temperature']:5.1f}°C | "
              f"{record['signal_strength']:5.1f}%")
    
    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
        print(f"\n📡 Ingestion Service stopped. {self.packet_count} packets processed.")

if __name__ == "__main__":
    service = IngestionService()
    service.start()
