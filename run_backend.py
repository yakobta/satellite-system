#!/usr/bin/env python3
"""
Backend Launcher for Satellite Ground Station System
"""

import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("🛰️  ETRSS-1 Backend System Launcher")
    print("=" * 60)
    print("")
    
    # Check if virtual environment is active
    if not os.getenv("VIRTUAL_ENV"):
        print("⚠️  Virtual environment not activated!")
        print("   Run: source venv/bin/activate")
        print("")
        sys.exit(1)
    
    # Install backend dependencies
    print("📦 Installing backend dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "backend/requirements.txt"])
    print("✅ Dependencies installed")
    print("")
    
    # Start the API server
    print("🚀 Starting API Server on http://localhost:8000")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("")
    print("Press Ctrl+C to stop")
    print("-" * 60)
    print("")
    
    subprocess.run([sys.executable, "backend/api/server.py"])

if __name__ == "__main__":
    main()
