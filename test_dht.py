#!/usr/bin/env python3
"""
AgroNex-Pi Hardware Test: DHT11/22 Temperature & Humidity Sensor (§10)

Tests adafruit_dht sensor read on GPIO4.
Handles intermittent 1-wire timing retries gracefully.
"""

import sys
import time
import argparse

import config
from hardware import initialize_hardware_libs, DHTSensor

def main():
    parser = argparse.ArgumentParser(description="Test DHT Temperature & Humidity Sensor")
    parser.add_argument("--simulate", action="store_true", help="Run test in simulation mode")
    args = parser.parse_args()

    print("==================================================")
    print("      TESTING DHT11/22 TEMPERATURE & HUMIDITY      ")
    print("==================================================")

    try:
        initialize_hardware_libs(simulate=args.simulate)
        sensor = DHTSensor()
    except Exception as e:
        print(f"❌ FAIL: Sensor initialization failed: {e}")
        sys.exit(1)

    success_count = 0

    for i in range(1, 6):
        temp, hum = sensor.read(max_retries=3)
        if temp is not None and hum is not None:
            print(f"Reading #{i}: Temperature = {temp} °C, Humidity = {hum} %")
            success_count += 1
        else:
            print(f"Reading #{i}: ❌ Read Timeout / Failed")
        time.sleep(2.0)

    sensor.cleanup()

    print("--------------------------------------------------")
    if success_count >= 2:
        print(f"[PASS] RESULT: PASS ({success_count}/5 successful reads)")
    else:
        print(f"[FAIL] RESULT: FAIL (Only {success_count}/5 valid reads)")
        sys.exit(1)

if __name__ == "__main__":
    main()
