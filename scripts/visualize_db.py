#!/usr/bin/env python3
"""
Database Visualization Tool
Generate plots and charts from telemetry data
"""

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import DatabaseManager


def plot_battery_trend(db: DatabaseManager):
    """Plot battery level over time"""
    data = db.get_battery_trend(limit=500)
    
    if not data:
        print("No data available for battery trend")
        return
    
    packets = [d['packet_id'] for d in data[::-1]]
    battery = [d['battery_level'] for d in data[::-1]]
    
    plt.figure(figsize=(12, 6))
    plt.plot(packets, battery, 'g-', linewidth=2)
    plt.xlabel('Packet Number')
    plt.ylabel('Battery Level (%)')
    plt.title('Satellite Battery Level Trend')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 105)
    plt.savefig('battery_trend.png', dpi=150)
    plt.close()
    print("✅ Saved battery_trend.png")


def plot_temperature_trend(db: DatabaseManager):
    """Plot temperature trends"""
    data = db.get_temperature_trend(limit=500)
    
    if not data:
        print("No data available for temperature trend")
        return
    
    packets = [d['packet_id'] for d in data[::-1]]
    main_bus = [d['thermal_main_bus'] for d in data[::-1]]
    payload = [d['thermal_payload'] for d in data[::-1]]
    battery = [d['thermal_battery'] for d in data[::-1]]
    
    plt.figure(figsize=(12, 6))
    plt.plot(packets, main_bus, 'r-', label='Main Bus', linewidth=2)
    plt.plot(packets, payload, 'b-', label='Payload', linewidth=2)
    plt.plot(packets, battery, 'g-', label='Battery', linewidth=2)
    plt.xlabel('Packet Number')
    plt.ylabel('Temperature (°C)')
    plt.title('Satellite Thermal Trends')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('temperature_trend.png', dpi=150)
    plt.close()
    print("✅ Saved temperature_trend.png")


def plot_signal_quality(db: DatabaseManager):
    """Plot signal quality trends"""
    data = db.get_signal_quality(limit=500)
    
    if not data:
        print("No data available for signal quality")
        return
    
    packets = [d['packet_id'] for d in data[::-1]]
    signal = [d['signal_strength'] for d in data[::-1]]
    data_rate = [d['data_rate_mbps'] for d in data[::-1]]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    ax1.plot(packets, signal, 'b-', linewidth=2)
    ax1.set_ylabel('Signal Strength (%)')
    ax1.set_title('Communication Signal Quality')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 105)
    
    ax2.plot(packets, data_rate, 'g-', linewidth=2)
    ax2.set_xlabel('Packet Number')
    ax2.set_ylabel('Data Rate (Mbps)')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('signal_quality.png', dpi=150)
    plt.close()
    print("✅ Saved signal_quality.png")


def plot_orbit_path(db: DatabaseManager):
    """Plot satellite orbit path"""
    data = db.get_orbit_data(limit=500)
    
    if not data:
        print("No data available for orbit path")
        return
    
    x = [d['position_x'] for d in data[::-1]]
    y = [d['position_y'] for d in data[::-1]]
    
    plt.figure(figsize=(10, 10))
    plt.plot(x, y, 'b-', linewidth=2, alpha=0.7)
    if len(x) > 0:
        plt.scatter(x[0], y[0], c='g', s=100, marker='o', label='Start Position')
        plt.scatter(x[-1], y[-1], c='r', s=100, marker='s', label='Current Position')
    plt.scatter(0, 6371, c='blue', s=200, marker='o', label='Earth Center')
    plt.xlabel('X Position (km)')
    plt.ylabel('Y Position (km)')
    plt.title('Satellite Orbit Path')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.savefig('orbit_path.png', dpi=150)
    plt.close()
    print("✅ Saved orbit_path.png")


def generate_report(db: DatabaseManager):
    """Generate HTML report"""
    stats = db.get_statistics()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Satellite Telemetry Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            h1 {{ color: #1a1a2e; }}
            .stats {{ background: white; padding: 20px; border-radius: 10px; margin: 10px 0; }}
            .stat-card {{ display: inline-block; background: #e94560; color: white; padding: 20px; margin: 10px; border-radius: 10px; min-width: 150px; }}
            .stat-value {{ font-size: 28px; font-weight: bold; }}
            .stat-label {{ font-size: 12px; margin-top: 5px; }}
            img {{ max-width: 100%; margin: 20px 0; border-radius: 10px; }}
        </style>
    </head>
    <body>
        <h1>🛰️ Satellite Telemetry Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="stats">
            <h2>📊 Mission Statistics</h2>
            <div class="stat-card">
                <div class="stat-value">{stats.get('total_packets', 0)}</div>
                <div class="stat-label">Total Packets</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('avg_battery_percent', 0)}%</div>
                <div class="stat-label">Avg Battery</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('avg_temperature_c', 0)}°C</div>
                <div class="stat-label">Avg Temperature</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('avg_signal_percent', 0)}%</div>
                <div class="stat-label">Avg Signal</div>
            </div>
        </div>
        
        <h2>📈 Telemetry Trends</h2>
        <img src="battery_trend.png" alt="Battery Trend">
        <img src="temperature_trend.png" alt="Temperature Trend">
        <img src="signal_quality.png" alt="Signal Quality">
        <img src="orbit_path.png" alt="Orbit Path">
    </body>
    </html>
    """
    
    with open('telemetry_report.html', 'w') as f:
        f.write(html)
    
    print("✅ Saved telemetry_report.html")


def main():
    print("📊 Generating Database Visualizations...")
    print("="*50)
    
    db = DatabaseManager()
    
    plot_battery_trend(db)
    plot_temperature_trend(db)
    plot_signal_quality(db)
    plot_orbit_path(db)
    generate_report(db)
    
    print("\n✅ All visualizations completed!")
    print("📁 Files generated:")
    print("   - battery_trend.png")
    print("   - temperature_trend.png")
    print("   - signal_quality.png")
    print("   - orbit_path.png")
    print("   - telemetry_report.html")
    
    db.close()


if __name__ == "__main__":
    main()
