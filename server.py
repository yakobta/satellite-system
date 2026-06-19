#!/usr/bin/env python3
"""
Real-time Telemetry Server
Serves live data via WebSocket and HTTP
"""

import json
import sqlite3
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

DB_PATH = "data/telemetry.db"
PORT = 8080

class TelemetryServer:
    """Handles real-time telemetry data"""
    
    def __init__(self):
        self.latest_data = {'packets': 0, 'battery': 0, 'temp': 0, 'signal': 0}
        self.running = True
        self.clients = []
        self._lock = threading.Lock()
        
    def update_data(self):
        """Fetch latest telemetry from database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Total packets
            c.execute("SELECT COUNT(*) FROM telemetry")
            count = c.fetchone()[0]
            
            if count > 0:
                # Latest values
                c.execute("""
                    SELECT battery_level, temperature, signal_strength 
                    FROM telemetry 
                    ORDER BY packet_id DESC 
                    LIMIT 1
                """)
                row = c.fetchone()
                
                with self._lock:
                    self.latest_data = {
                        'packets': count,
                        'battery': round(row[0], 1) if row else 0,
                        'temp': round(row[1], 1) if row else 0,
                        'signal': round(row[2], 1) if row else 0,
                        'timestamp': time.time()
                    }
            else:
                with self._lock:
                    self.latest_data = {'packets': 0, 'battery': 0, 'temp': 0, 'signal': 0, 'timestamp': time.time()}
            
            conn.close()
        except Exception as e:
            print(f"DB Error: {e}")
    
    def get_data(self):
        """Get latest telemetry data"""
        with self._lock:
            return self.latest_data.copy()


# Global server instance
server = TelemetryServer()

class Handler(BaseHTTPRequestHandler):
    """HTTP Handler for serving dashboard and API"""
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(302)
            self.send_header('Location', '/dashboard')
            self.end_headers()
            
        elif self.path == '/dashboard':
            self.serve_html()
            
        elif self.path == '/api/data':
            self.serve_json()
            
        elif self.path == '/api/stream':
            self.serve_stream()
            
        elif self.path.startswith('/images/'):
            self.serve_image()
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def serve_html(self):
        """Serve the dashboard HTML"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode())
    
    def serve_json(self):
        """Serve JSON data"""
        data = server.get_data()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def serve_stream(self):
        """Server-Sent Events for real-time updates"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            while True:
                data = server.get_data()
                self.wfile.write(f"data: {json.dumps(data)}\n\n".encode())
                self.wfile.flush()
                time.sleep(1)
        except:
            pass
    
    def serve_image(self):
        """Serve PNG images"""
        filename = self.path.replace('/images/', '')
        try:
            with open(filename, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(f.read())
        except:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass


# HTML Page
HTML_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ETRSS-1 Live Telemetry</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e27;
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        
        /* Header */
        .header {
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #0f1535, #1a1f3a);
            border-radius: 20px;
            margin-bottom: 30px;
            border: 1px solid rgba(0,212,255,0.1);
        }
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .status {
            display: inline-block;
            padding: 6px 20px;
            border-radius: 20px;
            font-size: 14px;
            margin-top: 10px;
        }
        .status.live {
            background: rgba(34,197,94,0.2);
            color: #22c55e;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        .update-time { color: #94a3b8; font-size: 14px; margin-top: 8px; }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #1a1f3a;
            padding: 25px;
            border-radius: 16px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.05);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }
        .stat-value {
            font-size: 36px;
            font-weight: bold;
            color: #00d4ff;
            font-variant-numeric: tabular-nums;
        }
        .stat-label {
            font-size: 13px;
            color: #94a3b8;
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Charts Grid */
        .charts-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin-bottom: 30px;
        }
        .chart-card {
            background: #1a1f3a;
            padding: 20px;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .chart-card h3 {
            color: #00d4ff;
            font-size: 16px;
            margin-bottom: 15px;
        }
        .chart-card img {
            width: 100%;
            border-radius: 10px;
        }
        
        /* Orbit */
        .orbit-card {
            background: #1a1f3a;
            padding: 20px;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 30px;
            text-align: center;
        }
        .orbit-card img {
            max-width: 100%;
            border-radius: 10px;
            max-height: 500px;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            color: #475569;
            font-size: 13px;
            padding: 20px;
            border-top: 1px solid rgba(255,255,255,0.05);
        }
        
        @media (max-width: 768px) {
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .charts-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🛰️ ETRSS-1 Live Telemetry</h1>
            <div class="status live">● LIVE</div>
            <div class="update-time" id="updateTime">Connecting...</div>
        </div>
        
        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="packets">0</div>
                <div class="stat-label">Total Packets</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="battery">0%</div>
                <div class="stat-label">Battery Level</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="temp">0°C</div>
                <div class="stat-label">Temperature</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="signal">0%</div>
                <div class="stat-label">Signal Strength</div>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="charts-grid">
            <div class="chart-card">
                <h3>🔋 Battery Trend</h3>
                <img src="/images/battery_trend.png" alt="Battery Trend" id="batteryImg">
            </div>
            <div class="chart-card">
                <h3>🌡️ Temperature Trend</h3>
                <img src="/images/temperature_trend.png" alt="Temperature Trend" id="tempImg">
            </div>
            <div class="chart-card">
                <h3>📶 Signal Quality</h3>
                <img src="/images/signal_quality.png" alt="Signal Quality" id="signalImg">
            </div>
            <div class="chart-card">
                <h3>🚀 Orbital Velocity</h3>
                <img src="/images/orbit_path.png" alt="Orbit Path" id="orbitImg">
            </div>
        </div>
        
        <!-- Orbit -->
        <div class="orbit-card">
            <h3 style="color:#00d4ff;">🛰️ Orbit Path</h3>
            <img src="/images/orbit_path.png" alt="Orbit Path" id="orbitFullImg">
        </div>
        
        <div class="footer">
            Entoto Observatory, Addis Ababa, Ethiopia | ESSTI Ground Station
        </div>
    </div>
    
    <script>
        // Update stats every second
        function updateStats() {
            fetch('/api/data')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('packets').textContent = data.packets;
                    document.getElementById('battery').textContent = data.battery + '%';
                    document.getElementById('temp').textContent = data.temp + '°C';
                    document.getElementById('signal').textContent = data.signal + '%';
                    document.getElementById('updateTime').textContent = 'Updated: ' + new Date().toLocaleTimeString();
                })
                .catch(() => {});
        }
        
        // Refresh images every 5 seconds
        function refreshImages() {
            const timestamp = Date.now();
            document.getElementById('batteryImg').src = '/images/battery_trend.png?' + timestamp;
            document.getElementById('tempImg').src = '/images/temperature_trend.png?' + timestamp;
            document.getElementById('signalImg').src = '/images/signal_quality.png?' + timestamp;
            document.getElementById('orbitImg').src = '/images/orbit_path.png?' + timestamp;
            document.getElementById('orbitFullImg').src = '/images/orbit_path.png?' + timestamp;
        }
        
        // Initial update
        updateStats();
        
        // Set intervals
        setInterval(updateStats, 1000);
        setInterval(refreshImages, 5000);
    </script>
</body>
</html>
'''

def update_loop():
    """Background thread to update data"""
    while True:
        server.update_data()
        time.sleep(1)

def main():
    print("=" * 60)
    print("🛰️  ETRSS-1 LIVE TELEMETRY SERVER")
    print("=" * 60)
    print(f"📡 HTTP Server: http://localhost:{PORT}")
    print(f"📊 Dashboard: http://localhost:{PORT}/dashboard")
    print(f"📡 API: http://localhost:{PORT}/api/data")
    print("=" * 60)
    print("🔄 Updating every 1 second...")
    print("Press Ctrl+C to stop\n")
    
    # Start update thread
    thread = threading.Thread(target=update_loop, daemon=True)
    thread.start()
    
    # Start HTTP server
    httpd = HTTPServer(('0.0.0.0', PORT), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()
