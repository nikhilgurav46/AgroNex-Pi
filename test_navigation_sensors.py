#!/usr/bin/env python3
"""Check NEO-7M GPS transport and HMC5883L heading without moving the rover."""

import argparse
from hardware import initialize_hardware_libs, GPSSensor, CompassSensor


def main():
    parser = argparse.ArgumentParser(description="Test NEO-7M GPS and HMC5883L compass")
    parser.add_argument("--simulate", action="store_true")
    args = parser.parse_args()
    initialize_hardware_libs(simulate=args.simulate)
    gps, compass = GPSSensor(), CompassSensor()
    try:
        print(f"Compass heading: {compass.read_heading():.1f} degrees")
        fix = gps.read_fix()
        if fix:
            print(f"GPS fix: {fix['latitude']:.6f}, {fix['longitude']:.6f}; satellites={fix['satellites']}")
        else:
            print("GPS transport is open; no satellite fix yet (test outdoors with clear sky).")
    finally:
        gps.cleanup()
        compass.cleanup()


if __name__ == "__main__":
    main()
