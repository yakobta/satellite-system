"""
Professional Database Module for Satellite Telemetry
Enterprise-grade SQLite database with backup, migration, and query optimization
"""

import sqlite3
import os
import json
import shutil
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from dataclasses import dataclass
from threading import Lock

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class TelemetryRecord:
    """Represents a telemetry database record"""
    id: int
    timestamp: datetime
    satellite_id: str
    packet_id: int
    mode: str
    position_x: float
    position_y: float
    position_z: float
    altitude_km: float
    velocity_kms: float
    angle_deg: float
    latitude_deg: float
    longitude_deg: float
    battery_level: float
    battery_voltage: float
    battery_current: float
    battery_temp: float
    thermal_main_bus: float
    thermal_payload: float
    thermal_battery: float
    thermal_transmitter: float
    signal_strength: float
    data_rate_mbps: float
    link_margin_db: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            'satellite_id': self.satellite_id,
            'packet_id': self.packet_id,
            'mode': self.mode,
            'position': {
                'x_km': self.position_x,
                'y_km': self.position_y,
                'z_km': self.position_z
            },
            'altitude_km': self.altitude_km,
            'velocity_kms': self.velocity_kms,
            'angle_deg': self.angle_deg,
            'coordinates': {
                'latitude': self.latitude_deg,
                'longitude': self.longitude_deg
            },
            'battery': {
                'level_percent': self.battery_level,
                'voltage_v': self.battery_voltage,
                'current_a': self.battery_current,
                'temperature_c': self.battery_temp
            },
            'thermal': {
                'main_bus_c': self.thermal_main_bus,
                'payload_c': self.thermal_payload,
                'battery_c': self.thermal_battery,
                'transmitter_c': self.thermal_transmitter
            },
            'comms': {
                'signal_strength_percent': self.signal_strength,
                'data_rate_mbps': self.data_rate_mbps,
                'link_margin_db': self.link_margin_db
            }
        }


class DatabaseManager:
    """
    Professional Database Manager for Satellite Telemetry
    Handles connection pooling, query optimization, and data retention
    """
    
    # Database schema version
    SCHEMA_VERSION = 2
    
    def __init__(self, db_path: str = "data/telemetry.db"):
        self.db_path = db_path
        self._lock = Lock()
        self._ensure_directory()
        self._init_database()
        self._run_migrations()
        
        logger.info(f"Database Manager initialized: {db_path}")
    
    def _ensure_directory(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created database directory: {db_dir}")
    
    def _init_database(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Main telemetry table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    satellite_id TEXT NOT NULL,
                    packet_id INTEGER NOT NULL,
                    mode TEXT NOT NULL,
                    
                    -- Position data
                    position_x REAL NOT NULL,
                    position_y REAL NOT NULL,
                    position_z REAL DEFAULT 0,
                    altitude_km REAL NOT NULL,
                    velocity_kms REAL NOT NULL,
                    angle_deg REAL NOT NULL,
                    latitude_deg REAL NOT NULL,
                    longitude_deg REAL NOT NULL,
                    
                    -- Battery data
                    battery_level REAL NOT NULL,
                    battery_voltage REAL NOT NULL,
                    battery_current REAL NOT NULL,
                    battery_temp REAL NOT NULL,
                    
                    -- Thermal data
                    thermal_main_bus REAL NOT NULL,
                    thermal_payload REAL NOT NULL,
                    thermal_battery REAL NOT NULL,
                    thermal_transmitter REAL NOT NULL,
                    
                    -- Communications data
                    signal_strength REAL NOT NULL,
                    data_rate_mbps REAL NOT NULL,
                    link_margin_db REAL NOT NULL,
                    
                    -- Metadata
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON telemetry(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_packet_id ON telemetry(packet_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_satellite ON telemetry(satellite_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_mode ON telemetry(mode)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_battery ON telemetry(battery_level)')
            
            # Create views for common queries
            cursor.execute('''
                CREATE VIEW IF NOT EXISTS v_latest_telemetry AS
                SELECT * FROM telemetry 
                ORDER BY packet_id DESC 
                LIMIT 100
            ''')
            
            cursor.execute('''
                CREATE VIEW IF NOT EXISTS v_mission_statistics AS
                SELECT 
                    satellite_id,
                    COUNT(*) as total_packets,
                    MIN(timestamp) as mission_start,
                    MAX(timestamp) as last_contact,
                    AVG(battery_level) as avg_battery,
                    MIN(battery_level) as min_battery,
                    AVG(thermal_main_bus) as avg_temp,
                    MAX(thermal_main_bus) as max_temp,
                    AVG(signal_strength) as avg_signal,
                    MIN(signal_strength) as min_signal
                FROM telemetry
                GROUP BY satellite_id
            ''')
            
            # Create metadata table for system info
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert schema version
            cursor.execute('''
                INSERT OR REPLACE INTO metadata (key, value) 
                VALUES ('schema_version', ?)
            ''', (str(self.SCHEMA_VERSION),))
            
            conn.commit()
            logger.info("Database schema initialized")
    
    def _run_migrations(self):
        """Run database migrations"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check current schema version
            cursor.execute("SELECT value FROM metadata WHERE key = 'schema_version'")
            result = cursor.fetchone()
            current_version = int(result[0]) if result else 0
            
            if current_version < self.SCHEMA_VERSION:
                logger.info(f"Running migrations from version {current_version} to {self.SCHEMA_VERSION}")
                
                # Add any new columns or tables here
                if current_version < 2:
                    # Add new columns for version 2
                    try:
                        cursor.execute("ALTER TABLE telemetry ADD COLUMN data_quality REAL DEFAULT 1.0")
                    except sqlite3.OperationalError:
                        pass  # Column already exists
                
                cursor.execute("UPDATE metadata SET value = ? WHERE key = 'schema_version'", 
                             (str(self.SCHEMA_VERSION),))
                conn.commit()
                logger.info("Migrations completed")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager and locking"""
        with self._lock:
            conn = sqlite3.connect(self.db_path, timeout=30)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
    
    def insert_telemetry(self, telemetry) -> int:
        """
        Insert telemetry packet into database
        Returns the inserted record ID
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO telemetry (
                        timestamp, satellite_id, packet_id, mode,
                        position_x, position_y, position_z,
                        altitude_km, velocity_kms, angle_deg,
                        latitude_deg, longitude_deg,
                        battery_level, battery_voltage, battery_current, battery_temp,
                        thermal_main_bus, thermal_payload, thermal_battery, thermal_transmitter,
                        signal_strength, data_rate_mbps, link_margin_db
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    telemetry.timestamp.isoformat(),
                    telemetry.satellite_id,
                    telemetry.packet_id,
                    telemetry.mode.value,
                    telemetry.position.x_km,
                    telemetry.position.y_km,
                    telemetry.position.z_km,
                    telemetry.position.altitude_km,
                    telemetry.position.velocity_kms,
                    telemetry.position.angle_deg,
                    telemetry.position.latitude_deg,
                    telemetry.position.longitude_deg,
                    telemetry.battery.level_percent,
                    telemetry.battery.voltage_v,
                    telemetry.battery.current_a,
                    telemetry.battery.temperature_c,
                    telemetry.thermal.main_bus_c,
                    telemetry.thermal.payload_c,
                    telemetry.thermal.battery_c,
                    telemetry.thermal.transmitter_c,
                    telemetry.comms.signal_strength_percent,
                    telemetry.comms.data_rate_mbps,
                    telemetry.comms.link_margin_db
                ))
                
                conn.commit()
                record_id = cursor.lastrowid
                logger.debug(f"Inserted telemetry record {record_id} (packet {telemetry.packet_id})")
                return record_id
                
        except Exception as e:
            logger.error(f"Failed to insert telemetry: {e}")
            raise
    
    def insert_batch(self, telemetry_list: List) -> int:
        """Insert multiple telemetry records in batch"""
        count = 0
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for telemetry in telemetry_list:
                cursor.execute('''
                    INSERT INTO telemetry (
                        timestamp, satellite_id, packet_id, mode,
                        position_x, position_y, position_z,
                        altitude_km, velocity_kms, angle_deg,
                        latitude_deg, longitude_deg,
                        battery_level, battery_voltage, battery_current, battery_temp,
                        thermal_main_bus, thermal_payload, thermal_battery, thermal_transmitter,
                        signal_strength, data_rate_mbps, link_margin_db
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    telemetry.timestamp.isoformat(),
                    telemetry.satellite_id,
                    telemetry.packet_id,
                    telemetry.mode.value,
                    telemetry.position.x_km,
                    telemetry.position.y_km,
                    telemetry.position.z_km,
                    telemetry.position.altitude_km,
                    telemetry.position.velocity_kms,
                    telemetry.position.angle_deg,
                    telemetry.position.latitude_deg,
                    telemetry.position.longitude_deg,
                    telemetry.battery.level_percent,
                    telemetry.battery.voltage_v,
                    telemetry.battery.current_a,
                    telemetry.battery.temperature_c,
                    telemetry.thermal.main_bus_c,
                    telemetry.thermal.payload_c,
                    telemetry.thermal.battery_c,
                    telemetry.thermal.transmitter_c,
                    telemetry.comms.signal_strength_percent,
                    telemetry.comms.data_rate_mbps,
                    telemetry.comms.link_margin_db
                ))
                count += 1
            conn.commit()
        return count
    
    def get_telemetry(self, packet_id: int) -> Optional[TelemetryRecord]:
        """Get telemetry by packet ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM telemetry WHERE packet_id = ?", (packet_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_record(row)
            return None
    
    def get_latest_telemetry(self, limit: int = 100) -> List[TelemetryRecord]:
        """Get latest telemetry records"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM telemetry 
                ORDER BY packet_id DESC 
                LIMIT ?
            ''', (limit,))
            return [self._row_to_record(row) for row in cursor.fetchall()]
    
    def get_telemetry_range(self, start_packet: int, end_packet: int) -> List[TelemetryRecord]:
        """Get telemetry in packet ID range"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM telemetry 
                WHERE packet_id BETWEEN ? AND ?
                ORDER BY packet_id ASC
            ''', (start_packet, end_packet))
            return [self._row_to_record(row) for row in cursor.fetchall()]
    
    def get_telemetry_by_time(self, start_time: datetime, end_time: datetime) -> List[TelemetryRecord]:
        """Get telemetry by time range"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM telemetry 
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            ''', (start_time.isoformat(), end_time.isoformat()))
            return [self._row_to_record(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Overall statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_packets,
                    MIN(timestamp) as first_packet,
                    MAX(timestamp) as last_packet,
                    COUNT(DISTINCT satellite_id) as satellites,
                    AVG(battery_level) as avg_battery,
                    AVG(thermal_main_bus) as avg_temp,
                    AVG(signal_strength) as avg_signal,
                    MIN(battery_level) as min_battery,
                    MAX(thermal_main_bus) as max_temp,
                    MIN(signal_strength) as min_signal
                FROM telemetry
            ''')
            overall = cursor.fetchone()
            
            # Mode distribution
            cursor.execute('''
                SELECT mode, COUNT(*) as count 
                FROM telemetry 
                GROUP BY mode
            ''')
            modes = {row['mode']: row['count'] for row in cursor.fetchall()}
            
            # Recent activity (last hour)
            one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            cursor.execute('''
                SELECT COUNT(*) as recent_packets 
                FROM telemetry 
                WHERE timestamp > ?
            ''', (one_hour_ago,))
            recent = cursor.fetchone()
            
            # Database file size
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            return {
                "total_packets": overall[0] or 0,
                "first_packet": overall[1],
                "last_packet": overall[2],
                "satellites_tracked": overall[3] or 0,
                "avg_battery_percent": round(overall[4] or 0, 2),
                "avg_temperature_c": round(overall[5] or 0, 1),
                "avg_signal_percent": round(overall[6] or 0, 2),
                "min_battery_percent": round(overall[7] or 0, 2),
                "max_temperature_c": round(overall[8] or 0, 1),
                "min_signal_percent": round(overall[9] or 0, 2),
                "mode_distribution": modes,
                "recent_packets_last_hour": recent[0] or 0,
                "database_size_mb": round(db_size / (1024 * 1024), 2),
                "database_path": self.db_path
            }
    
    def get_mission_statistics(self, satellite_id: str = None) -> Dict:
        """Get mission-specific statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if satellite_id:
                cursor.execute('''
                    SELECT * FROM v_mission_statistics 
                    WHERE satellite_id = ?
                ''', (satellite_id,))
            else:
                cursor.execute('SELECT * FROM v_mission_statistics')
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {}
    
    def get_battery_trend(self, limit: int = 1000) -> List[Dict]:
        """Get battery level trend data"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT packet_id, timestamp, battery_level 
                FROM telemetry 
                ORDER BY packet_id DESC 
                LIMIT ?
            ''', (limit,))
            return [{'packet_id': row['packet_id'], 'timestamp': row['timestamp'], 'battery_level': row['battery_level']} 
                    for row in cursor.fetchall()]
    
    def get_temperature_trend(self, limit: int = 1000) -> List[Dict]:
        """Get temperature trend data"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT packet_id, timestamp, thermal_main_bus, thermal_payload, thermal_battery
                FROM telemetry 
                ORDER BY packet_id DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_signal_quality(self, limit: int = 1000) -> List[Dict]:
        """Get signal quality trend data"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT packet_id, timestamp, signal_strength, data_rate_mbps, link_margin_db
                FROM telemetry 
                ORDER BY packet_id DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_orbit_data(self, limit: int = 1000) -> List[Dict]:
        """Get orbit position data for visualization"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT packet_id, timestamp, position_x, position_y, altitude_km, velocity_kms, angle_deg
                FROM telemetry 
                ORDER BY packet_id DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def export_to_json(self, output_path: str, limit: int = 1000):
        """Export telemetry to JSON file"""
        records = self.get_latest_telemetry(limit)
        data = {
            "exported_at": datetime.now().isoformat(),
            "total_records": len(records),
            "telemetry": [r.to_dict() for r in records]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Exported {len(records)} records to {output_path}")
    
    def export_to_csv(self, output_path: str, limit: int = 1000):
        """Export telemetry to CSV file"""
        import csv
        
        records = self.get_latest_telemetry(limit)
        
        if not records:
            logger.warning("No records to export")
            return
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=records[0].to_dict().keys())
            writer.writeheader()
            for record in records:
                writer.writerow(record.to_dict())
        
        logger.info(f"Exported {len(records)} records to {output_path}")
    
    def cleanup_old_data(self, retention_days: int = 30):
        """Delete data older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM telemetry 
                WHERE timestamp < ?
            ''', (cutoff_date.isoformat(),))
            
            deleted = cursor.rowcount
            conn.commit()
            
            if deleted > 0:
                logger.info(f"Cleaned up {deleted} old telemetry records (older than {retention_days} days)")
            
            # Vacuum database to reclaim space
            cursor.execute("VACUUM")
            logger.info("Database vacuum completed")
    
    def backup(self, backup_path: str = None):
        """Create database backup"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/backup/telemetry_backup_{timestamp}.db"
        
        backup_dir = os.path.dirname(backup_path)
        if backup_dir and not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        with self._lock:
            shutil.copy2(self.db_path, backup_path)
        
        logger.info(f"Database backed up to {backup_path}")
        return backup_path
    
    def _row_to_record(self, row) -> TelemetryRecord:
        """Convert database row to TelemetryRecord"""
        return TelemetryRecord(
            id=row['id'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            satellite_id=row['satellite_id'],
            packet_id=row['packet_id'],
            mode=row['mode'],
            position_x=row['position_x'],
            position_y=row['position_y'],
            position_z=row['position_z'],
            altitude_km=row['altitude_km'],
            velocity_kms=row['velocity_kms'],
            angle_deg=row['angle_deg'],
            latitude_deg=row['latitude_deg'],
            longitude_deg=row['longitude_deg'],
            battery_level=row['battery_level'],
            battery_voltage=row['battery_voltage'],
            battery_current=row['battery_current'],
            battery_temp=row['battery_temp'],
            thermal_main_bus=row['thermal_main_bus'],
            thermal_payload=row['thermal_payload'],
            thermal_battery=row['thermal_battery'],
            thermal_transmitter=row['thermal_transmitter'],
            signal_strength=row['signal_strength'],
            data_rate_mbps=row['data_rate_mbps'],
            link_margin_db=row['link_margin_db']
        )
    
    def close(self):
        """Close database connection pool"""
        logger.info("Database Manager closed")


# Database query utility functions
def create_db_queries():
    """Create useful database query templates"""
    
    queries = {
        "health_check": """
            SELECT 
                COUNT(*) as total,
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                AVG(battery_level) as avg_battery,
                AVG(thermal_main_bus) as avg_temp,
                AVG(signal_strength) as avg_signal
            FROM telemetry
            WHERE timestamp > datetime('now', '-1 day')
            GROUP BY hour
            ORDER BY hour DESC
        """,
        
        "anomaly_detection": """
            SELECT * FROM telemetry 
            WHERE battery_level < 20 
               OR thermal_main_bus > 50 
               OR signal_strength < 50
            ORDER BY timestamp DESC
            LIMIT 100
        """,
        
        "orbit_comparison": """
            SELECT 
                MIN(altitude_km) as min_altitude,
                MAX(altitude_km) as max_altitude,
                AVG(altitude_km) as avg_altitude,
                MIN(velocity_kms) as min_velocity,
                MAX(velocity_kms) as max_velocity,
                AVG(velocity_kms) as avg_velocity
            FROM telemetry
        """
    }
    
    return queries


# Convenience function for quick database access
def get_database(db_path: str = "data/telemetry.db") -> DatabaseManager:
    """Get database manager instance"""
    return DatabaseManager(db_path)


if __name__ == "__main__":
    # Test database functionality
    db = DatabaseManager("data/test_telemetry.db")
    
    # Display statistics
    stats = db.get_statistics()
    print("\n📊 Database Statistics:")
    print(json.dumps(stats, indent=2, default=str))
    
    db.close()
