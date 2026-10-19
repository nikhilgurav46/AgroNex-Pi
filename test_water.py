#!/usr/bin/env python3
"""
AgroNex-Pi Hardware Test: HW-038 Water Level Sensor (§10)

Tests HW-038 analog water level sensor connected to ADS1115 Channel A1.
Prints raw ADC value (0-32767) and calculated reservoir percentage (0-100%).
Optionally pushes live readings to the AWS Cloud Command Center dashboard.
"""

import sys
import time
import argparse

import config
from hardware import initialize_hardware_libs, WaterLevelSensor

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False


def push_to_aws(water_pct, raw_adc, status):
    """Pushes water level reading directly to AWS Cloud Command Center."""
    if not _REQUESTS_AVAILABLE or not getattr(config, "AWS_ENABLED", False):
        return
    url = f"{config.AWS_API_URL.rstrip('/')}/telemetry"
    payload = {
        "water_level": water_pct,
        "water_status": status,
        "raw_water_adc": raw_adc,
        "current_state": "WATER_TEST",
        "navigation_status": "BENCH_TEST",
        "pump_state": False,
        "cutter_state": False,
        "uptime_seconds": int(time.time())
    }
    try:
        requests.post(url, json=payload, timeout=3.0)
    except Exception as e:
        print(f"   [AWS Push Notice]: {e}")


def main():
    parser = argparse.ArgumentParser(description="Test HW-038 Water Level Sensor")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode")
    parser.add_argument("--continuous", "-c", action="store_true", default=True, help="Loop continuously until Ctrl+C (default: True)")
    parser.add_argument("--push", "-p", action="store_true", default=True, help="Push live readings directly to AWS Cloud Dashboard (default: True)")
    parser.add_argument("--no-push", action="store_false", dest="push", help="Disable AWS sync")
    args = parser.parse_args()

    print("==================================================")
    print("      AGRONEX: HW-038 WATER LEVEL SENSOR TEST     ")
    print("==================================================")
    print(f"ADC Channel: ADS1115 Channel A1 (I2C 0x48)")
    print(f"AWS Sync   : {'ENABLED -> ' + config.AWS_API_URL if args.push else 'OFF (add --push to sync)'}\n")

    try:
        initialize_hardware_libs(simulate=args.simulate)
        sensor = WaterLevelSensor(channel=config.ADS1115_CH_WATER)
    except Exception as e:
        print(f"❌ FAIL: Driver initialization failed: {e}")
        sys.exit(1)

    try:
        if args.continuous or args.push:
            print("Reading water level continuously... (Press Ctrl+C to stop)\n")
            count = 0
            while True:
                count += 1
                raw, pct, status = sensor.read_percentage()
                print(f"[{count:03d}] Raw ADC: {raw:5d}  |  Water Level: {pct:5.1f}%  [{status}]")
                if args.push:
                    push_to_aws(pct, raw, status)
                time.sleep(1.5)
        else:
            print("Taking 5 test readings...\n")
            for i in range(1, 6):
                raw, pct, status = sensor.read_percentage()
                print(f"Reading #{i}: Raw ADC = {raw:5d}, Water Level = {pct:5.1f}%  [{status}]")
                time.sleep(1.0)
            print("\n--------------------------------------------------")
            print("Test complete. Pass --continuous or --push to stream live to dashboard.")

    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        sensor.cleanup()


if __name__ == "__main__":
    main()
