#!/usr/bin/env python3
"""
Database Visualization Tool - Simple Working Version
"""

import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import os

DB_PATH = "data/telemetry.db"

def get_data():
    """Get telemetry data from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM telemetry")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("⚠️ No data in database. Run ground station and satellite first.")
        conn.close()
        return None, None
    
    cursor.execute("""
        SELECT packet_id, battery_level, temperature, signal_strength, position_x, position_y
        FROM telemetry
        ORDER BY packet_id
        LIMIT 500
    """)
    
    data = cursor.fetchall()
    conn.close()
    return data, count

def plot_battery(data):
    """Plot battery trend"""
    if not data:
        return
    packets = [d[0] for d in data]
    battery = [d[1] for d in data]
    
    plt.figure(figsize=(10, 5))
    plt.plot(packets, battery, 'g-', linewidth=2)
    plt.xlabel('Packet Number')
    plt.ylabel('Battery Level (%)')
    plt.title('Satellite Battery Level Trend')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 105)
    plt.savefig('battery_trend.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Saved battery_trend.png")

def plot_temperature(data):
    """Plot temperature trend"""
    if not data:
        return
    packets = [d[0] for d in data]
    temp = [d[2] for d in data]
    
    plt.figure(figsize=(10, 5))
    plt.plot(packets, temp, 'r-', linewidth=2)
    plt.xlabel('Packet Number')
    plt.ylabel('Temperature (°C)')
    plt.title('Satellite Temperature Trend')
    plt.grid(True, alpha=0.3)
    plt.savefig('temperature_trend.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Saved temperature_trend.png")

def plot_signal(data):
    """Plot signal strength trend"""
    if not data:
        return
    packets = [d[0] for d in data]
    signal = [d[3] for d in data]
    
    plt.figure(figsize=(10, 5))
    plt.plot(packets, signal, 'b-', linewidth=2)
    plt.xlabel('Packet Number')
    plt.ylabel('Signal Strength (%)')
    plt.title('Signal Strength Trend')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 105)
    plt.savefig('signal_quality.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Saved signal_quality.png")

def plot_orbit(data):
    """Plot orbit path"""
    if not data:
        return
    x = [d[4] for d in data]
    y = [d[5] for d in data]
    
    plt.figure(figsize=(10, 10))
    plt.plot(x, y, 'b-', linewidth=2, alpha=0.7)
    if len(x) > 0:
        plt.scatter(x[0], y[0], c='g', s=100, marker='o', label='Start')
        plt.scatter(x[-1], y[-1], c='r', s=100, marker='s', label='Current')
    plt.scatter(0, 0, c='blue', s=200, marker='o', label='Earth')
    plt.xlabel('X Position (km)')
    plt.ylabel('Y Position (km)')
    plt.title('Satellite Orbit Path')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.savefig('orbit_path.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("✅ Saved orbit_path.png")

def main():
    print("📊 Generating Database Visualizations...")
    print("="*50)
    
    data, count = get_data()
    
    if not data:
        print("❌ No data found. Please run ground station and satellite first.")
        return
    
    print(f"📡 Found {count} telemetry records")
    
    plot_battery(data)
    plot_temperature(data)
    plot_signal(data)
    plot_orbit(data)
    
    print("\n✅ All visualizations completed!")
    print("📁 Files generated:")
    print("   - battery_trend.png")
    print("   - temperature_trend.png")
    print("   - signal_quality.png")
    print("   - orbit_path.png")

if __name__ == "__main__":
    main()
