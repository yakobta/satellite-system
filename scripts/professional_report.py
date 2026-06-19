#!/usr/bin/env python3
"""
Professional Report Generator - Simple Working Version
"""

import sqlite3
from datetime import datetime
import os

DB_PATH = "data/telemetry.db"

def get_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM telemetry")
    count = cursor.fetchone()[0]
    
    if count == 0:
        return None, None
    
    cursor.execute("""
        SELECT packet_id, battery_level, temperature, signal_strength
        FROM telemetry
        ORDER BY packet_id DESC
        LIMIT 100
    """)
    data = cursor.fetchall()
    conn.close()
    return data, count

def generate_html(data, count):
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>ETRSS-1 Telemetry Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #0a0e27; color: #e0e0e0; margin: 20px; }}
        h1 {{ text-align: center; color: #00d4ff; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
        .card {{ background: #1a1f3a; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #2a2f4a; }}
        .value {{ font-size: 28px; font-weight: bold; color: #00d4ff; }}
        .label {{ font-size: 12px; color: #94a3b8; margin-top: 5px; }}
        img {{ max-width: 100%; margin: 10px 0; border-radius: 10px; }}
        .footer {{ text-align: center; color: #475569; margin-top: 30px; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>🛰️ ETRSS-1 Telemetry Dashboard</h1>
    <p style="text-align:center; color:#94a3b8;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="stats">
        <div class="card"><div class="value">{count}</div><div class="label">Total Packets</div></div>
        <div class="card"><div class="value">{data[0][1] if data else 0:.1f}%</div><div class="label">Latest Battery</div></div>
        <div class="card"><div class="value">{data[0][2] if data else 0:.1f}°C</div><div class="label">Latest Temp</div></div>
        <div class="card"><div class="value">{data[0][3] if data else 0:.1f}%</div><div class="label">Latest Signal</div></div>
    </div>
    
    <h2 style="color:#00d4ff;">📈 Telemetry Trends</h2>
    <img src="battery_trend.png" alt="Battery Trend">
    <img src="temperature_trend.png" alt="Temperature Trend">
    <img src="signal_quality.png" alt="Signal Quality">
    <img src="orbit_path.png" alt="Orbit Path">
    
    <div class="footer">ESSTI Ground Station - Entoto Observatory, Ethiopia</div>
</body>
</html>
'''
    
    with open('telemetry_dashboard.html', 'w') as f:
        f.write(html)
    print("✅ Saved telemetry_dashboard.html")

def main():
    print("📊 Generating Professional Satellite Telemetry Dashboard...")
    print("="*50)
    
    data, count = get_data()
    
    if not data or count == 0:
        print("❌ No telemetry data found. Run the ground station and satellite first!")
        return
    
    print(f"📡 Found {count} telemetry records")
    generate_html(data, count)
    print("\n✅ Dashboard Generated Successfully!")
    print("📁 File: telemetry_dashboard.html")
    print("\n🌐 Open in browser:")
    print("   open telemetry_dashboard.html")

if __name__ == "__main__":
    main()
