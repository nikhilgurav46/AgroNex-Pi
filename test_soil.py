#!/usr/bin/env python3
"""
AgroNex-Pi Hardware Test: Soil Moisture Sensor (§10)

Tests Capacitive Soil Moisture Sensor via ADS1115 (A0) / MCP3008 ADC.
Prints raw ADC values and calculated moisture percentage.
Optionally syncs live readings directly to the AWS Cloud Dashboard.
"""

import sys
import time
import argparse
import logging

import config
from hardware import initialize_hardware_libs, SoilSensor

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False


def push_to_aws(moisture_pct, raw_adc):
    """Pushes a test telemetry update to the AWS Cloud Command Center."""
    if not _REQUESTS_AVAILABLE or not getattr(config, "AWS_ENABLED", False):
        return
    url = f"{config.AWS_API_URL.rstrip('/')}/telemetry"
    payload = {
        "soil_moisture": moisture_pct,
        "raw_adc": raw_adc,
        "current_state": "SOIL_TEST",
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
    parser = argparse.ArgumentParser(description="Test Soil Moisture Sensor")
    parser.add_argument("--simulate", action="store_true", help="Run test in simulation mode")
    parser.add_argument("--continuous", "-c", action="store_true", default=True, help="Loop continuously until Ctrl+C (default: True)")
    parser.add_argument("--push", "-p", action="store_true", default=True, help="Push live readings directly to AWS Cloud Dashboard (default: True)")
    parser.add_argument("--no-push", action="store_false", dest="push", help="Disable AWS sync")
    args = parser.parse_args()

    print("==================================================")
    print("      AGRONEX: SOIL MOISTURE SENSOR TEST          ")
    print("==================================================")
    print(f"ADC Mode: {'ADS1115 (I2C A0)' if getattr(config, 'USE_ADS1115', True) else 'MCP3008 (SPI CH0)'}")
    print(f"AWS Sync: {'ENABLED -> ' + config.AWS_API_URL if args.push else 'OFF (add --push to sync)'}\n")

    try:
        initialize_hardware_libs(simulate=args.simulate)
        sensor = SoilSensor()
    except Exception as e:
        print(f"❌ FAIL: Hardware driver initialization failed: {e}")
        sys.exit(1)

    try:
        if args.continuous or args.push:
            print("Reading sensor continuously... (Press Ctrl+C to stop)\n")
            count = 0
            while True:
                count += 1
                raw_adc, pct = sensor.read_percentage()
                if pct is not None:
                    status = "DRY (Need Water)" if pct < 35 else ("WET (Saturated)" if pct > 75 else "OPTIMAL")
                    print(f"[{count:03d}] Raw ADC: {raw_adc:5d}  |  Moisture: {pct:5.1f}%  [{status}]")
                    if args.push:
                        push_to_aws(pct, raw_adc)
                else:
                    print(f"[{count:03d}] ❌ IMPLAUSIBLE ADC READING ({raw_adc})")
                time.sleep(1.5)
        else:
            success_count = 0
            readings = []
            for i in range(1, 6):
                raw_adc, pct = sensor.read_percentage()
                if pct is not None:
                    print(f"Reading #{i}: Raw ADC = {raw_adc}, Moisture = {pct:.1f}%")
                    success_count += 1
                    readings.append(pct)
                else:
                    print(f"Reading #{i}: ❌ IMPLAUSIBLE ADC READING ({raw_adc})")
                time.sleep(1.0)

            print("--------------------------------------------------")
            if success_count >= 3:
                avg_pct = sum(readings) / len(readings) if readings else 0.0
                print(f"[PASS] RESULT: PASS ({success_count}/5 successful reads. Average: {avg_pct:.1f}%)")
            else:
                print(f"[FAIL] RESULT: FAIL (Only {success_count}/5 valid reads)")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        sensor.cleanup()


if __name__ == "__main__":
    main()
