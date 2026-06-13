#!/usr/bin/env python3
"""
Database Utilities for Satellite Telemetry
Command-line tools for database management
"""

import sys
import os
import argparse
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import DatabaseManager
from src.utils import setup_logging

logger = setup_logging()


def main():
    parser = argparse.ArgumentParser(description="Satellite Telemetry Database Utilities")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export telemetry data')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Export format')
    export_parser.add_argument('--limit', type=int, default=1000, help='Number of records to export')
    export_parser.add_argument('--output', type=str, help='Output file path')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup database')
    backup_parser.add_argument('--output', type=str, help='Backup file path')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean old data')
    cleanup_parser.add_argument('--days', type=int, default=30, help='Retention days')
    
    args = parser.parse_args()
    
    db = DatabaseManager()
    
    if args.command == 'stats':
        stats = db.get_statistics()
        print("\n📊 DATABASE STATISTICS")
        print("="*50)
        for key, value in stats.items():
            print(f"{key:25}: {value}")
    
    elif args.command == 'export':
        if args.format == 'json':
            output = args.output or f"export_telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            db.export_to_json(output, limit=args.limit)
        else:
            output = args.output or f"export_telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            db.export_to_csv(output, limit=args.limit)
        print(f"✅ Exported to {output}")
    
    elif args.command == 'backup':
        backup_path = db.backup(args.output)
        print(f"✅ Database backed up to {backup_path}")
    
    elif args.command == 'cleanup':
        db.cleanup_old_data(retention_days=args.days)
        print(f"✅ Cleaned data older than {args.days} days")
    
    else:
        parser.print_help()
    
    db.close()


if __name__ == "__main__":
    main()
