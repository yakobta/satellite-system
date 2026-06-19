"""
Database Service - Handles all database operations
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import json

class DatabaseService:
    def __init__(self, db_path="backend/data/telemetry.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS telemetry (
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
                ground_contact INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        c.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON telemetry(timestamp)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_packet_id ON telemetry(packet_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_ground_contact ON telemetry(ground_contact)')
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized: {self.db_path}")
    
    def insert_telemetry(self, data: Dict):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO telemetry (
                timestamp, satellite_id, packet_id,
                position_x, position_y, latitude, longitude,
                battery_level, temperature, signal_strength, ground_contact
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('timestamp', datetime.now().isoformat()),
            data.get('satellite_id', 'ETRSS-1'),
            data.get('packet_id', 0),
            data.get('position_x', 0),
            data.get('position_y', 0),
            data.get('latitude', 0),
            data.get('longitude', 0),
            data.get('battery_level', 0),
            data.get('temperature', 0),
            data.get('signal_strength', 0),
            1 if data.get('ground_contact', False) else 0
        ))
        
        conn.commit()
        record_id = c.lastrowid
        conn.close()
        return record_id
    
    def get_latest(self, limit: int = 100):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''
            SELECT * FROM telemetry 
            ORDER BY packet_id DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_statistics(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) as total FROM telemetry')
        total = c.fetchone()[0]
        
        c.execute('SELECT AVG(battery_level) as avg_battery, AVG(temperature) as avg_temp, AVG(signal_strength) as avg_signal FROM telemetry')
        stats = c.fetchone()
        
        c.execute('SELECT MAX(packet_id) as last_packet FROM telemetry')
        last = c.fetchone()[0]
        
        conn.close()
        
        return {
            "total_packets": total,
            "avg_battery": round(stats[0] or 0, 2),
            "avg_temperature": round(stats[1] or 0, 2),
            "avg_signal": round(stats[2] or 0, 2),
            "last_packet": last or 0
        }
    
    def get_by_packet(self, packet_id: int):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM telemetry WHERE packet_id = ?', (packet_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def export_json(self, limit: int = 1000):
        data = self.get_latest(limit)
        return json.dumps(data, indent=2, default=str)
    
    def export_csv(self, limit: int = 1000):
        import csv
        from io import StringIO
        
        data = self.get_latest(limit)
        output = StringIO()
        
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return output.getvalue()
    
    def delete_old_data(self, days: int = 30):
        import datetime
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('DELETE FROM telemetry WHERE timestamp < ?', (cutoff,))
        deleted = c.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    
    def backup(self):
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backend/backups/telemetry_backup_{timestamp}.db"
        os.makedirs("backend/backups", exist_ok=True)
        
        shutil.copy2(self.db_path, backup_path)
        return backup_path
