#!/usr/bin/env python3
"""
Simple Live Dashboard - Opens in your browser
Run: python3 live_dashboard.py
"""

import sqlite3
import os
import webbrowser
from datetime import datetime
import time

DB_PATH = "data/telemetry.db"

def get_data():
    """Get latest telemetry data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM telemetry")
        count = cursor.fetchone()[0]
        
        if count == 0:
            conn.close()
            return {'packets': 0, 'battery': 0, 'temp': 0, 'signal': 0}
        
        cursor.execute("""
            SELECT battery_level, temperature, signal_strength 
            FROM telemetry 
            ORDER BY packet_id DESC 
            LIMIT 1
        """)
        latest = cursor.fetchone()
        conn.close()
        
        return {
            'packets': count,
            'battery': round(latest[0], 1) if latest else 0,
            'temp': round(latest[1], 1) if latest else 0,
            'signal': round(latest[2], 1) if latest else 0
        }
    except:
        return {'packets': 0, 'battery': 0, 'temp': 0, 'signal': 0}

# Generate HTML
html = f'''<!DOCTYPE html>
<html>
<head>
    <title>ETRSS-1 Live Telemetry</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #0a0e27;
            color: #e0e0e0;
            text-align: center;
            padding: 20px;
        }}
        h1 {{ color: #00d4ff; font-size: 36px; }}
        .live {{ color: #22c55e; font-weight: bold; animation: blink 1s infinite; }}
        @keyframes blink {{ 50% {{ opacity: 0.3; }} }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            max-width: 800px;
            margin: 30px auto;
        }}
        .card {{
            background: #1a1f3a;
            padding: 25px;
            border-radius: 15px;
            border: 1px solid #2a2f4a;
        }}
        .value {{
            font-size: 32px;
            font-weight: bold;
            color: #00d4ff;
        }}
        .label {{
            font-size: 14px;
            color: #94a3b8;
            margin-top: 5px;
        }}
        .footer {{
            color: #475569;
            margin-top: 30px;
            font-size: 14px;
        }}
        img {{
            max-width: 100%;
            margin: 20px 0;
            border-radius: 10px;
            border: 1px solid #2a2f4a;
        }}
        .update-time {{
            color: #94a3b8;
            font-size: 14px;
            margin: 10px 0;
        }}
        .row {{
            display: flex;
            gap: 20px;
            max-width: 800px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <h1>🛰️ ETRSS-1 Telemetry</h1>
    <p class="live">● LIVE</p>
    <p class="update-time" id="time">Updating...</p>
    
    <div class="grid">
        <div class="card">
            <div class="value" id="packets">0</div>
            <div class="label">Total Packets</div>
        </div>
        <div class="card">
            <div class="value" id="battery">0%</div>
            <div class="label">Battery</div>
        </div>
        <div class="card">
            <div class="value" id="temp">0°C</div>
            <div class="label">Temperature</div>
        </div>
        <div class="card">
            <div class="value" id="signal">0%</div>
            <div class="label">Signal</div>
        </div>
    </div>
    
    <h2 style="color:#00d4ff; margin-top:40px;">📈 Trends</h2>
    <div class="row" style="flex-direction:column;">
        <img src="battery_trend.png" alt="Battery Trend">
        <img src="temperature_trend.png" alt="Temperature Trend">
        <img src="signal_quality.png" alt="Signal Quality">
        <img src="orbit_path.png" alt="Orbit Path">
    </div>
    
    <div class="footer">Entoto Observatory, Ethiopia | ESSTI</div>
    
    <script>
        function updateData() {{
            fetch('/data')
                .then(r => r.json())
                .then(d => {{
                    document.getElementById('packets').textContent = d.packets;
                    document.getElementById('battery').textContent = d.battery + '%';
                    document.getElementById('temp').textContent = d.temp + '°C';
                    document.getElementById('signal').textContent = d.signal + '%';
                    document.getElementById('time').textContent = 'Updated: ' + new Date().toLocaleTimeString();
                }})
                .catch(() => {{}});
        }}
        setInterval(updateData, 2000);
        updateData();
    </script>
</body>
</html>'''

with open('live_dashboard.html', 'w') as f:
    f.write(html)
print("✅ live_dashboard.html created")

# Create a simple server
cat > server.py << 'EOF'
import http.server
import socketserver
import json
import sqlite3
import os

PORT = 8000
DB_PATH = "data/telemetry.db"

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/data':
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM telemetry")
                count = c.fetchone()[0]
                if count > 0:
                    c.execute("SELECT battery_level, temperature, signal_strength FROM telemetry ORDER BY packet_id DESC LIMIT 1")
                    r = c.fetchone()
                    data = {'packets': count, 'battery': round(r[0],1), 'temp': round(r[1],1), 'signal': round(r[2],1)}
                else:
                    data = {'packets': 0, 'battery': 0, 'temp': 0, 'signal': 0}
                conn.close()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except:
                self.send_response(500)
                self.end_headers()
        else:
            super().do_GET()

print("🌐 Server: http://localhost:8000")
print("📡 Open live_dashboard.html in browser")
httpd = socketserver.TCPServer(("", PORT), Handler)
httpd.serve_forever()
