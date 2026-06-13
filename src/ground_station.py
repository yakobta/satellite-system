"""
Ground Station Module
Professional telemetry receiver with database storage and anomaly detection
"""

import socket
import json
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List
from collections import deque

from src.telemetry import TelemetryPacket, SatelliteMode
from src.database import DatabaseManager
from src.config import config
import logging

logger = logging.getLogger(__name__)


class GroundStation:
    """
    Professional Ground Station for satellite telemetry reception
    """
    
    def __init__(self, port: Optional[int] = None):
        self.port = port or config.ground_station.port
        self.buffer_size = config.ground_station.buffer_size
        self.sock: Optional[socket.socket] = None
        self.running = False
        self.packets_received = 0
        self.packets_lost = 0
        self.expected_packet_id = 0
        self.db = DatabaseManager()
        self.packet_history = deque(maxlen=1000)
        self.start_time: Optional[float] = None
        
        logger.info(f"Ground Station initialized on port {self.port}")
    
    def start(self):
        """Start the ground station"""
        self.running = True
        self.start_time = time.time()
        
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
                    self._process_packet(data, addr)
                except socket.timeout:
                    self._check_connection()
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {e}")
                    
        except KeyboardInterrupt:
            self.shutdown()
    
    def _process_packet(self, data: bytes, addr: tuple):
        """Process incoming telemetry packet"""
        self.packets_received += 1
        
        # Parse telemetry
        telemetry_dict = json.loads(data.decode())
        telemetry = TelemetryPacket.from_dict(telemetry_dict)
        
        # Check for packet loss
        if telemetry.packet_id != self.expected_packet_id and self.expected_packet_id > 0:
            lost = telemetry.packet_id - self.expected_packet_id
            self.packets_lost += lost
            logger.warning(f"Packet loss detected: {lost} packets missing")
        
        self.expected_packet_id = telemetry.packet_id + 1
        telemetry.comms.packets_received = self.packets_received
        
        # Store in database
        self.db.insert_telemetry(telemetry)
        
        # Store in history
        self.packet_history.append(telemetry)
        
        # Display telemetry
        self._display_telemetry(telemetry)
        
        # Detect anomalies
        self._detect_anomalies(telemetry)
    
    def _display_header(self):
        """Display professional header"""
        print("\n" + "="*80)
        print("🛰️  PROFESSIONAL GROUND STATION".center(80))
        print("="*80)
        print(f"📡 Location: {config.ground_station.location}")
        print(f"📡 Listening on: 0.0.0.0:{self.port}")
        print(f"💾 Database: {config.database.path}")
        print(f"📊 Log file: logs/satellite.log")
        print("="*80)
        print(f"{'ID':>6} | {'Time':>12} | {'Position (km)':>20} | {'Battery':>8} | {'Temp':>6} | {'Signal':>6}")
        print("-"*80)
    
    def _display_telemetry(self, telemetry: TelemetryPacket):
        """Display formatted telemetry"""
        time_str = telemetry.timestamp.strftime("%H:%M:%S")
        
        # Status icons
        battery_icon = "🔋" if telemetry.battery.level_percent > 30 else "⚠️"
        signal_icon = "📶" if telemetry.comms.signal_strength_percent > 50 else "📡⚠️"
        
        print(f"{telemetry.packet_id:6d} | {time_str:>12} | "
              f"({telemetry.position.x_km:6.0f}, {telemetry.position.y_km:6.0f}) | "
              f"{battery_icon} {telemetry.battery.level_percent:5.1f}% | "
              f"{telemetry.thermal.main_bus_c:5.1f}°C | "
              f"{signal_icon} {telemetry.comms.signal_strength_percent:5.1f}%")
    
    def _detect_anomalies(self, telemetry: TelemetryPacket):
        """Detect anomalies in telemetry"""
        anomalies = []
        
        if telemetry.battery.level_percent < 15:
            anomalies.append(f"🚨 CRITICAL: Battery at {telemetry.battery.level_percent}%")
        elif telemetry.battery.level_percent < 30:
            anomalies.append(f"⚠️ Low Battery: {telemetry.battery.level_percent}%")
        
        if telemetry.thermal.main_bus_c > 50:
            anomalies.append(f"🚨 OVERHEATING: {telemetry.thermal.main_bus_c}°C")
        elif telemetry.thermal.main_bus_c < -10:
            anomalies.append(f"❄️ TOO COLD: {telemetry.thermal.main_bus_c}°C")
        
        if telemetry.comms.signal_strength_percent < 50:
            anomalies.append(f"⚠️ Weak Signal: {telemetry.comms.signal_strength_percent}%")
        
        for anomaly in anomalies:
            logger.warning(anomaly)
    
    def _check_connection(self):
        """Check if signal is lost"""
        if self.packets_received > 0:
            time_since_last = time.time() - self.start_time
            if time_since_last > 10:
                logger.warning(f"Signal lost for {time_since_last:.0f} seconds")
    
    def get_statistics(self) -> Dict:
        """Get reception statistics"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        loss_rate = (self.packets_lost / max(1, self.packets_received)) * 100
        
        return {
            "packets_received": self.packets_received,
            "packets_lost": self.packets_lost,
            "loss_rate_percent": round(loss_rate, 2),
            "packets_per_second": round(self.packets_received / max(1, elapsed), 2),
            "runtime_seconds": round(elapsed, 1)
        }
    
    def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        stats = self.get_statistics()
        
        print("\n" + "="*80)
        print("📡 GROUND STATION SHUTDOWN REPORT".center(80))
        print("="*80)
        print(f"📊 Reception Statistics:")
        print(f"   📦 Packets Received: {stats['packets_received']}")
        print(f"   ⚠️ Packets Lost: {stats['packets_lost']}")
        print(f"   📉 Loss Rate: {stats['loss_rate_percent']}%")
        print(f"   📈 Data Rate: {stats['packets_per_second']} pkt/s")
        print(f"   ⏱️ Runtime: {stats['runtime_seconds']:.1f} seconds")
        print("="*80)
        
        # Close database
        self.db.close()
        
        # Close socket
        if self.sock:
            self.sock.close()
        
        logger.info("Ground Station shutdown complete")


def main():
    """Entry point for ground station"""
    import sys
    
    port = 5005
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    
    station = GroundStation(port=port)
    station.start()


if __name__ == "__main__":
    main()
