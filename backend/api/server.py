"""
FastAPI Server - REST API for Satellite Telemetry
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.database_service import DatabaseService

# Initialize FastAPI
app = FastAPI(
    title="ETRSS-1 Satellite Telemetry API",
    description="REST API for satellite telemetry data",
    version="2.0.0"
)

# Enable CORS (allow frontend to access API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database service
db = DatabaseService()

# ------------------------------
# Request/Response Models
# ------------------------------

class TelemetryResponse(BaseModel):
    id: int
    timestamp: str
    satellite_id: str
    packet_id: int
    position_x: float
    position_y: float
    latitude: float
    longitude: float
    battery_level: float
    temperature: float
    signal_strength: float
    ground_contact: int

class StatisticsResponse(BaseModel):
    total_packets: int
    avg_battery: float
    avg_temperature: float
    avg_signal: float
    last_packet: int

# ------------------------------
# API Endpoints
# ------------------------------

@app.get("/")
async def root():
    return {
        "message": "ETRSS-1 Satellite Telemetry API",
        "version": "2.0.0",
        "endpoints": {
            "/telemetry/latest": "Get latest telemetry",
            "/telemetry/statistics": "Get mission statistics",
            "/telemetry/{packet_id}": "Get telemetry by packet ID",
            "/telemetry/export/json": "Export as JSON",
            "/telemetry/export/csv": "Export as CSV"
        }
    }

@app.get("/telemetry/latest", response_model=List[TelemetryResponse])
async def get_latest_telemetry(limit: int = 100):
    """Get latest telemetry records"""
    try:
        data = db.get_latest(limit)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/telemetry/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """Get mission statistics"""
    try:
        return db.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/telemetry/{packet_id}")
async def get_telemetry_by_packet(packet_id: int):
    """Get telemetry by packet ID"""
    try:
        data = db.get_by_packet(packet_id)
        if data:
            return data
        raise HTTPException(status_code=404, detail="Packet not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/telemetry/export/json")
async def export_json(limit: int = 1000):
    """Export telemetry as JSON"""
    try:
        data = db.get_latest(limit)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/telemetry/export/csv")
async def export_csv(limit: int = 1000):
    """Export telemetry as CSV"""
    try:
        csv_data = db.export_csv(limit)
        return JSONResponse(content={"csv": csv_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/telemetry/cleanup")
async def cleanup_old_data(days: int = 30):
    """Delete telemetry older than specified days"""
    try:
        deleted = db.delete_old_data(days)
        return {"deleted": deleted, "message": f"Deleted {deleted} records older than {days} days"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/telemetry/backup")
async def backup_database():
    """Create a database backup"""
    try:
        backup_path = db.backup()
        return {"backup_path": backup_path, "message": "Backup created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "database": db.db_path}

# ------------------------------
# Run Server
# ------------------------------

if __name__ == "__main__":
    print("🚀 Starting ETRSS-1 Telemetry API Server")
    print("📡 Listening on: http://localhost:8000")
    print("📊 API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
