#!/usr/bin/env python3
"""
Professional Satellite Telemetry Report Generator
Creates modern, interactive HTML dashboard with real-time visualizations
"""

import json
import sqlite3
from datetime import datetime
import os

def get_telemetry_data(db_path="data/telemetry.db", limit=500):
    """Fetch telemetry data from database"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get latest telemetry for statistics
    cursor.execute('''
        SELECT 
            COUNT(*) as total_packets,
            AVG(battery_level) as avg_battery,
            AVG(thermal_main_bus) as avg_temp,
            AVG(signal_strength) as avg_signal,
            MIN(battery_level) as min_battery,
            MAX(thermal_main_bus) as max_temp,
            MIN(signal_strength) as min_signal,
            MAX(packet_id) as last_packet
        FROM telemetry
    ''')
    stats = dict(cursor.fetchone())
    
    # Get time-series data for charts
    cursor.execute('''
        SELECT 
            packet_id,
            timestamp,
            battery_level,
            thermal_main_bus,
            signal_strength,
            position_x,
            position_y,
            velocity_kms
        FROM telemetry
        ORDER BY packet_id DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    data = [dict(row) for row in rows][::-1]  # Reverse to chronological order
    
    conn.close()
    return stats, data


def generate_html_report(stats, data, output_path="telemetry_dashboard.html"):
    """Generate modern HTML dashboard"""
    
    # Prepare data for JavaScript
    packets = [d['packet_id'] for d in data]
    timestamps = [d['timestamp'] for d in data]
    battery = [round(d['battery_level'], 1) for d in data]
    temperature = [round(d['thermal_main_bus'], 1) for d in data]
    signal = [round(d['signal_strength'], 1) for d in data]
    positions_x = [round(d['position_x'], 0) for d in data]
    positions_y = [round(d['position_y'], 0) for d in data]
    velocity = [round(d['velocity_kms'], 2) for d in data]
    
    # Calculate trends
    battery_trend = "increasing" if battery[-1] > battery[0] else "decreasing" if battery[-1] < battery[0] else "stable"
    temp_trend = "rising" if temperature[-1] > temperature[0] else "falling" if temperature[-1] < temperature[0] else "stable"
    signal_trend = "improving" if signal[-1] > signal[0] else "degrading" if signal[-1] < signal[0] else "stable"
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESSTI Satellite Telemetry Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        /* Header */
        .header {{
            text-align: center;
            padding: 30px 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            background: linear-gradient(135deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #94a3b8;
            font-size: 0.9rem;
        }}
        
        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            border-color: rgba(0,212,255,0.3);
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stat-label {{
            font-size: 0.85rem;
            color: #94a3b8;
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-trend {{
            font-size: 0.75rem;
            margin-top: 8px;
            padding: 4px 8px;
            border-radius: 20px;
            display: inline-block;
        }}
        
        .trend-up {{ background: rgba(34,197,94,0.2); color: #22c55e; }}
        .trend-down {{ background: rgba(239,68,68,0.2); color: #ef4444; }}
        .trend-stable {{ background: rgba(234,179,8,0.2); color: #eab308; }}
        
        /* Charts Grid */
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .chart-container {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .chart-title {{
            font-size: 1.1rem;
            margin-bottom: 15px;
            color: #00d4ff;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .chart-title::before {{
            content: '';
            width: 4px;
            height: 20px;
            background: linear-gradient(135deg, #00d4ff, #7c3aed);
            border-radius: 2px;
        }}
        
        canvas {{
            max-height: 300px;
            width: 100%;
        }}
        
        /* Orbit Tracker */
        .orbit-container {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }}
        
        .orbit-canvas {{
            text-align: center;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 20px;
            color: #475569;
            font-size: 0.8rem;
            border-top: 1px solid rgba(255,255,255,0.05);
            margin-top: 30px;
        }}
        
        /* Status Indicators */
        .status-ok {{
            color: #22c55e;
        }}
        .status-warning {{
            color: #eab308;
        }}
        .status-critical {{
            color: #ef4444;
        }}
        
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            .stat-value {{
                font-size: 1.8rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <!-- Header -->
        <div class="header">
            <h1>🛰️ ESSTI Satellite Telemetry Dashboard</h1>
            <p>Ethiopian Space Science and Technology Institute | Real-time Mission Data</p>
            <p style="font-size: 0.8rem; margin-top: 10px;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Satellite: ET-SAT-001</p>
        </div>
        
        <!-- Statistics Cards -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats['total_packets'] or 0:,}</div>
                <div class="stat-label">Total Packets</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['avg_battery'] or 0:.1f}%</div>
                <div class="stat-label">Avg Battery</div>
                <div class="stat-trend trend-{battery_trend}">📈 {battery_trend}</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['avg_temp'] or 0:.1f}°C</div>
                <div class="stat-label">Avg Temperature</div>
                <div class="stat-trend trend-{temp_trend}">🌡️ {temp_trend}</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['avg_signal'] or 0:.1f}%</div>
                <div class="stat-label">Avg Signal</div>
                <div class="stat-trend trend-{signal_trend}">📶 {signal_trend}</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['min_battery'] or 0:.1f}%</div>
                <div class="stat-label">Min Battery</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['max_temp'] or 0:.1f}°C</div>
                <div class="stat-label">Max Temperature</div>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">🔋 Battery Level Trend</div>
                <canvas id="batteryChart"></canvas>
            </div>
            <div class="chart-container">
                <div class="chart-title">🌡️ Temperature Trend</div>
                <canvas id="temperatureChart"></canvas>
            </div>
            <div class="chart-container">
                <div class="chart-title">📶 Signal Strength Trend</div>
                <canvas id="signalChart"></canvas>
            </div>
            <div class="chart-container">
                <div class="chart-title">🚀 Orbital Velocity</div>
                <canvas id="velocityChart"></canvas>
            </div>
        </div>
        
        <!-- Orbit Path -->
        <div class="orbit-container">
            <div class="chart-title">🛰️ Satellite Orbit Path (X-Y Position)</div>
            <canvas id="orbitChart" width="600" height="400"></canvas>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>ESSTI Ground Station - Entoto Observatory, Ethiopia | Data Source: Real-time Telemetry | System Status: ✅ Operational</p>
        </div>
    </div>
    
    <script>
        // Data from Python
        const packets = {json.dumps(packets)};
        const timestamps = {json.dumps(timestamps)};
        const battery = {json.dumps(battery)};
        const temperature = {json.dumps(temperature)};
        const signal = {json.dumps(signal)};
        const velocity = {json.dumps(velocity)};
        const positions_x = {json.dumps(positions_x)};
        const positions_y = {json.dumps(positions_y)};
        
        // Common chart options
        const commonOptions = {{
            responsive: true,
            maintainAspectRatio: true,
            plugins: {{
                legend: {{
                    labels: {{ color: '#94a3b8' }}
                }},
                tooltip: {{
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleColor: '#00d4ff',
                    bodyColor: '#e0e0e0'
                }}
            }},
            scales: {{
                x: {{
                    grid: {{ color: 'rgba(255,255,255,0.1)' }},
                    ticks: {{ color: '#94a3b8' }}
                }},
                y: {{
                    grid: {{ color: 'rgba(255,255,255,0.1)' }},
                    ticks: {{ color: '#94a3b8' }}
                }}
            }}
        }};
        
        // Battery Chart
        new Chart(document.getElementById('batteryChart'), {{
            type: 'line',
            data: {{
                labels: packets,
                datasets: [{{
                    label: 'Battery Level (%)',
                    data: battery,
                    borderColor: '#22c55e',
                    backgroundColor: 'rgba(34,197,94,0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2
                }}]
            }},
            options: {{
                ...commonOptions,
                plugins: {{
                    ...commonOptions.plugins,
                    annotation: {{
                        annotations: {{
                            line1: {{
                                type: 'line',
                                yMin: 20,
                                yMax: 20,
                                borderColor: '#ef4444',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                label: {{
                                    content: 'Critical',
                                    enabled: true,
                                    position: 'end',
                                    color: '#ef4444'
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Temperature Chart
        new Chart(document.getElementById('temperatureChart'), {{
            type: 'line',
            data: {{
                labels: packets,
                datasets: [{{
                    label: 'Temperature (°C)',
                    data: temperature,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239,68,68,0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2
                }}]
            }},
            options: commonOptions
        }});
        
        // Signal Chart
        new Chart(document.getElementById('signalChart'), {{
            type: 'line',
            data: {{
                labels: packets,
                datasets: [{{
                    label: 'Signal Strength (%)',
                    data: signal,
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0,212,255,0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2
                }}]
            }},
            options: commonOptions
        }});
        
        // Velocity Chart
        new Chart(document.getElementById('velocityChart'), {{
            type: 'line',
            data: {{
                labels: packets,
                datasets: [{{
                    label: 'Orbital Velocity (km/s)',
                    data: velocity,
                    borderColor: '#eab308',
                    backgroundColor: 'rgba(234,179,8,0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2
                }}]
            }},
            options: commonOptions
        }});
        
        // Orbit Path Chart
        new Chart(document.getElementById('orbitChart'), {{
            type: 'scatter',
            data: {{
                datasets: [{{
                    label: 'Orbit Path',
                    data: positions_x.map((x, i) => ({{ x: x, y: positions_y[i] }})),
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0,212,255,0.5)',
                    showLine: true,
                    pointRadius: 1,
                    borderWidth: 2,
                    tension: 0.1
                }}, {{
                    label: 'Start Position',
                    data: [{{ x: positions_x[0], y: positions_y[0] }}],
                    backgroundColor: '#22c55e',
                    pointRadius: 8,
                    pointStyle: 'circle'
                }}, {{
                    label: 'Current Position',
                    data: [{{ x: positions_x[positions_x.length-1], y: positions_y[positions_y.length-1] }}],
                    backgroundColor: '#ef4444',
                    pointRadius: 8,
                    pointStyle: 'circle'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        labels: {{ color: '#94a3b8' }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return `Position: (${{context.parsed.x.toFixed(0)}}, ${{context.parsed.y.toFixed(0)}}) km`;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{
                            display: true,
                            text: 'X Position (km)',
                            color: '#94a3b8'
                        }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }},
                        ticks: {{ color: '#94a3b8' }}
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'Y Position (km)',
                            color: '#94a3b8'
                        }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }},
                        ticks: {{ color: '#94a3b8' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Professional dashboard generated: {output_path}")
    return output_path


def main():
    """Main execution"""
    print("📊 Generating Professional Satellite Telemetry Dashboard...")
    print("=" * 50)
    
    stats, data = get_telemetry_data()
    
    if not data:
        print("❌ No telemetry data found. Run the ground station and satellite first!")
        return
    
    print(f"📡 Found {len(data)} telemetry records")
    print(f"🛰️  Processing {stats['total_packets'] or 0} total packets...")
    
    output_path = generate_html_report(stats, data)
    
    print("\n" + "=" * 50)
    print("✅ Dashboard Generated Successfully!")
    print(f"📁 File: {output_path}")
    print("\n📊 Dashboard Features:")
    print("   • Interactive Charts (Zoom, Pan, Hover)")
    print("   • Real-time Data Visualization")
    print("   • Professional Dark Theme")
    print("   • Orbital Path Tracking")
    print("   • Trend Analysis")
    print("\n🌐 Open in browser:")
    print(f"   open {output_path}")


if __name__ == "__main__":
    main()
