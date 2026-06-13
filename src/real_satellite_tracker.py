"""
Real-Time Satellite Tracker
Fetches live satellite positions from public APIs (N2YO, Celestrak)
Tracks ETRSS-1, ISS, NOAA, and other satellites
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class RealSatelliteTracker:
    """
    Track real satellites using public APIs
    Requires internet connection
    """
    
    # Public satellite databases (free, no API key required for basic queries)
    CELESTRAK_URL = "https://celestrak.com/NORAD/elements/gp.php"
    N2YO_BASE = "https://api.n2yo.com/rest/v1/satellite"
    
    # Notable satellites to track
    SATELLITES = {
        "iss": {"norad": 25544, "name": "International Space Station"},
        "etrss1": {"norad": 44880, "name": "ETRSS-1 (Ethiopia)"},
        "noaa_15": {"norad": 25338, "name": "NOAA-15"},
        "noaa_18": {"norad": 28654, "name": "NOAA-18"},
        "noaa_19": {"norad": 33591, "name": "NOAA-19"},
        "hubble": {"norad": 20580, "name": "Hubble Space Telescope"},
        "tianhe": {"norad": 48274, "name": "Tianhe (China Space Station)"}
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key  # Optional, free tier available
        self.cache = {}
    
    def get_tle(self, norad_id: int) -> Optional[Dict]:
        """Get TLE data for a satellite from Celestrak"""
        try:
            url = f"{self.CELESTRAK_URL}?CATNR={norad_id}&FORMAT=JSON"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                if data:
                    return data[0] if isinstance(data, list) else data
        except Exception as e:
            logger.error(f"Failed to fetch TLE for {norad_id}: {e}")
        return None
    
    def get_satellite_positions(self, norad_id: int) -> Optional[Dict]:
        """
        Get current satellite position
        Note: Free API has rate limits, use sparingly
        """
        if not self.api_key:
            logger.warning("No API key provided. Using simulated positions.")
            return self._simulate_position(norad_id)
        
        try:
            url = f"{self.N2YO_BASE}/positions/{norad_id}/41/-98/0/1/&apiKey={self.api_key}"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data
        except Exception as e:
            logger.error(f"API error for {norad_id}: {e}")
            return self._simulate_position(norad_id)
    
    def _simulate_position(self, norad_id: int) -> Dict:
        """Simulate position when API is unavailable"""
        import math
        import time
        
        # Simple orbital simulation for demonstration
        t = time.time() % 5400  # ~90 minute period
        angle = 2 * math.pi * t / 5400
        
        return {
            "info": {
                "norad_id": norad_id,
                "simulated": True
            },
            "positions": [{
                "satlatitude": 30 * math.sin(angle),
                "satlongitude": 20 * math.cos(angle),
                "sataltitude": 400 + 50 * math.sin(2 * angle),
                "timestamp": int(time.time())
            }]
        }
    
    def get_visible_passes(self, norad_id: int, lat: float, lon: float, days: int = 1) -> Optional[List]:
        """Get upcoming visible passes for a satellite"""
        if not self.api_key:
            logger.warning("API key required for pass predictions")
            return None
        
        try:
            url = f"{self.N2YO_BASE}/visualpasses/{norad_id}/{lat}/{lon}/0/{days}/&apiKey={self.api_key}"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data.get("passes", [])
        except Exception as e:
            logger.error(f"Failed to get passes: {e}")
            return None
    
    def get_all_satellite_positions(self) -> Dict:
        """Get positions for all tracked satellites"""
        positions = {}
        
        for name, info in self.SATELLITES.items():
            norad = info["norad"]
            result = self.get_satellite_positions(norad)
            if result:
                positions[name] = {
                    "name": info["name"],
                    "norad_id": norad,
                    "data": result
                }
        
        return positions
    
    def get_etrss1_status(self) -> Dict:
        """Get specific status for Ethiopia's ETRSS-1"""
        return self.get_satellite_positions(self.SATELLITES["etrss1"]["norad"]) or {}


# Simple function for quick tracking
def track_etrss1():
    """Quick function to track ETRSS-1"""
    tracker = RealSatelliteTracker()
    position = tracker.get_etrss1_status()
    
    if position:
        print("\n" + "=" * 60)
        print("🛰️  ETRSS-1 REAL-TIME TRACKING")
        print("=" * 60)
        
        if position.get("info", {}).get("simulated"):
            print("📡 Using simulated position (API key required for real data)")
        else:
            pos = position.get("positions", [{}])[0]
            print(f"📍 Latitude: {pos.get('satlatitude', 'N/A')}°")
            print(f"📍 Longitude: {pos.get('satlongitude', 'N/A')}°")
            print(f"📏 Altitude: {pos.get('sataltitude', 'N/A')} km")
            print(f"🕐 Time: {datetime.fromtimestamp(pos.get('timestamp', 0))}")
    
    return position


if __name__ == "__main__":
    track_etrss1()
