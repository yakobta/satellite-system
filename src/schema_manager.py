"""
Database Schema Manager - Auto-detects and adds missing columns
"""

import sqlite3
import os
from typing import List, Dict, Any
from contextlib import contextmanager

TARGET_SCHEMA = {
    "telemetry": {
        "columns": [
            ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
            ("timestamp", "TEXT NOT NULL"),
            ("satellite_id", "TEXT NOT NULL"),
            ("packet_id", "INTEGER NOT NULL"),
            ("position_x", "REAL NOT NULL"),
            ("position_y", "REAL NOT NULL"),
            ("latitude", "REAL NOT NULL"),
            ("longitude", "REAL NOT NULL"),
            ("battery_level", "REAL NOT NULL"),
            ("temperature", "REAL NOT NULL"),
            ("signal_strength", "REAL NOT NULL"),
            ("ground_contact", "INTEGER DEFAULT 0"),
            ("created_at", "TEXT DEFAULT CURRENT_TIMESTAMP")
        ]
    }
}

class SchemaManager:
    def __init__(self, db_path: str = "data/telemetry.db"):
        self.db_path = db_path
        self._ensure_directory()
    
    def _ensure_directory(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def get_existing_columns(self, table_name: str) -> List[str]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            return [row['name'] for row in cursor.fetchall()]
    
    def get_target_columns(self, table_name: str) -> List[str]:
        if table_name not in TARGET_SCHEMA:
            return []
        return [col[0] for col in TARGET_SCHEMA[table_name]["columns"]]
    
    def add_missing_columns(self, table_name: str) -> List[str]:
        existing = self.get_existing_columns(table_name)
        target = self.get_target_columns(table_name)
        missing = [col for col in target if col not in existing]
        
        if not missing:
            return []
        
        col_defs = {name: col_type for name, col_type in TARGET_SCHEMA[table_name]["columns"]}
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            added = []
            for col_name in missing:
                if col_name == "id":
                    continue
                col_type = col_defs.get(col_name, "TEXT")
                default = "DEFAULT 0" if "INTEGER" in col_type or "REAL" in col_type else "DEFAULT ''"
                try:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type} {default}")
                    added.append(col_name)
                except sqlite3.OperationalError:
                    pass
            conn.commit()
        return added
    
    def ensure_schema(self, table_name: str) -> Dict[str, Any]:
        result = {"table_exists": False, "columns_added": [], "status": "error"}
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                exists = cursor.fetchone()
                if not exists:
                    columns = ", ".join([f"{name} {col_type}" for name, col_type in TARGET_SCHEMA[table_name]["columns"]])
                    cursor.execute(f"CREATE TABLE {table_name} ({columns})")
                    conn.commit()
                    result["table_exists"] = True
                    result["columns_added"] = self.get_target_columns(table_name)
                    result["status"] = "success"
                else:
                    result["table_exists"] = True
                    added = self.add_missing_columns(table_name)
                    result["columns_added"] = added
                    result["status"] = "success"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        return result

def fix_latitude_column(db_path: str = "data/telemetry.db") -> Dict[str, Any]:
    manager = SchemaManager(db_path)
    return manager.ensure_schema("telemetry")

if __name__ == "__main__":
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/telemetry.db"
    result = fix_latitude_column(db_path)
    print(f"✅ Schema fixed: {result}")
