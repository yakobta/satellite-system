#!/usr/bin/env python3
"""
Satellite Ground Station System - Main Entry Point
Ethiopian Space Science and Technology Institute
"""

import sys
import argparse
from src.utils import setup_logging
from src.config import config
from src.ground_station import GroundStation
from src.satellite import Satellite

logger = setup_logging()


def print_banner():
    """Print application banner"""
    banner = """
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                    🛰️  SATELLITE GROUND STATION SYSTEM                      ║
    ║                     Ethiopian Space Science and Technology Institute        ║
    ║                                   v2.0.0                                    ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    parser = argparse.ArgumentParser(
        description="Professional Satellite Ground Station System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Ground Station (Receiver)
  python main.py --mode ground
  
  # Run Satellite Simulator (Transmitter)
  python main.py --mode satellite
  
  # Run both in separate terminals
  Terminal 1: python main.py --mode ground
  Terminal 2: python main.py --mode satellite
  
  # Use custom port
  python main.py --mode ground --port 5555
  python main.py --mode satellite --port 5555
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["ground", "satellite"],
        required=True,
        help="Operation mode: ground station or satellite simulator"
    )
    
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=5005,
        help="UDP port (default: 5005)"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Configuration file path"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.mode == "ground":
        logger.info(f"Starting Ground Station on port {args.port}")
        station = GroundStation(port=args.port)
        station.start()
    
    elif args.mode == "satellite":
        logger.info(f"Starting Satellite Simulator broadcasting to port {args.port}")
        satellite = Satellite()
        satellite.broadcast(port=args.port)


if __name__ == "__main__":
    main()
