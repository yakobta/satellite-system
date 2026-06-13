#!/usr/bin/env python3
"""
ETRSS-1 Mission Control Launcher
Launch either:
  - Realistic ETRSS-1 Simulator
  - Real Satellite Tracker (via API)
  - Ground Station Receiver
"""

import sys
import argparse
import subprocess
import threading
import time
import os


def print_banner():
    banner = """
    ╔════════════════════════════════════════════════════════════════════════════╗
    ║                                                                            ║
    ║          🛰️  ETRSS-1 MISSION CONTROL SYSTEM                              ║
    ║          Ethiopian Space Science and Technology Institute                  ║
    ║                                                                            ║
    ║          🇪🇹 Ethiopia's First Satellite (2019-12-20)                      ║
    ║          NORAD: 44880 | Sun-Synchronous Orbit | 628 km                    ║
    ║                                                                            ║
    ╚════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_ground_station():
    """Run the ground station receiver"""
    print("\n📡 Starting Ground Station (Receiver)...")
    os.system("python3 src/ground_station.py")


def run_etrss1_simulator():
    """Run the realistic ETRSS-1 simulator"""
    print("\n🛰️  Starting ETRSS-1 Realistic Simulator...")
    os.system("python3 src/etrss1_satellite.py")


def run_real_tracker():
    """Run the real satellite tracker"""
    print("\n🛰️  Starting Real Satellite Tracker...")
    os.system("python3 src/real_satellite_tracker.py")


def run_both():
    """Run both simulator and ground station in parallel"""
    print("\n🚀 Launching Complete ETRSS-1 Mission...")
    
    # Start ground station in background
    def start_ground():
        os.system("python3 src/ground_station.py")
    
    # Start satellite in background
    def start_satellite():
        time.sleep(2)  # Wait for ground station to initialize
        os.system("python3 src/etrss1_satellite.py")
    
    ground_thread = threading.Thread(target=start_ground)
    satellite_thread = threading.Thread(target=start_satellite)
    
    ground_thread.start()
    satellite_thread.start()
    
    try:
        ground_thread.join()
        satellite_thread.join()
    except KeyboardInterrupt:
        print("\n\n🛑 Mission terminated by user")


def main():
    parser = argparse.ArgumentParser(
        description="ETRSS-1 Mission Control System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Ground Station only
  python launch_etrss1.py --mode ground
  
  # Run ETRSS-1 Simulator only
  python launch_etrss1.py --mode etrss1
  
  # Run Real Satellite Tracker
  python launch_etrss1.py --mode tracker
  
  # Run Complete Mission (Both)
  python launch_etrss1.py --mode both
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["ground", "etrss1", "tracker", "both"],
        required=True,
        help="Operation mode"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.mode == "ground":
        run_ground_station()
    elif args.mode == "etrss1":
        run_etrss1_simulator()
    elif args.mode == "tracker":
        run_real_tracker()
    elif args.mode == "both":
        run_both()


if __name__ == "__main__":
    main()
