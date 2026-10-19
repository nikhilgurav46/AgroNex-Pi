#!/usr/bin/env python3
"""
AgroNex-Pi: Multi-Sensor Live Diagnostic & Dashboard Sync Tool

Reads and displays all connected sensors in real-time:
  - Capacitive Soil Moisture Sensor (ADS1115 A0)
  - HW-038 Water Level Sensor (ADS1115 A1)
  - DHT11 Temperature & Humidity (GPIO 4)
  - HMC5883L / QMC5883L Compass (I2C)
  - NEO-7M GPS (UART /dev/serial0)

Pushes live updates to the AWS Cloud Dashboard every 2 seconds.
"""

import sys
import time
import argparse
import logging

import config
from hardware import (
    initialize_hardware_libs,
    SoilSensor,
    WaterLevelSensor,
    DHTSensor,
    CompassSensor,
    GPSSensor
)

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False


def push_to_aws(data: dict):
    if not _REQUESTS_AVAILABLE or not getattr(config, "AWS_ENABLED", False):
        return
    url = f"{config.AWS_API_URL.rstrip('/')}/telemetry"
    try:
        requests.post(url, json=data, timeout=3.0)
    except Exception as e:
        pass


def main():
    parser = argparse.ArgumentParser(description="Multi-Sensor Bench Diagnostic")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode")
    parser.add_argument("--push", "-p", action="store_true", default=True, help="Push to AWS Cloud (default: True)")
    parser.add_argument("--no-push", action="store_false", dest="push", help="Disable AWS sync")
    args = parser.parse_args()

    print("==================================================")
    print("      AGRONEX: ALL-SENSORS BENCH DIAGNOSTIC       ")
    print("==================================================")
    print(f"AWS Sync: {'ENABLED -> ' + config.AWS_API_URL if args.push else 'OFF'}\n")

    # Quick I2C bus hardware pre-check (Raspberry Pi)
    if not args.simulate and sys.platform.startswith("linux"):
        import os
        if not os.path.exists("/dev/i2c-1"):
            print("⚠️ WARNING: /dev/i2c-1 not found! Enable I2C with: sudo raspi-config nonint do_i2c 0")
        try:
            import smbus2
            bus = smbus2.SMBus(config.ADS1115_I2C_BUS)
            try:
                bus.read_byte(config.ADS1115_I2C_ADDRESS)
                print(f"✅ I2C Bus 1 active & ADS1115 responding at 0x{config.ADS1115_I2C_ADDRESS:02X}!")
            except Exception:
                print(f"⚠️ I2C Bus 1 open, but ADS1115 at 0x{config.ADS1115_I2C_ADDRESS:02X} didn't respond. Check wiring or run 'i2cdetect -y 1'")
            bus.close()
        except ImportError:
            print("⚠️ WARNING: 'smbus2' not installed! Run: pip install smbus2")
        except Exception as e:
            print(f"⚠️ I2C check notice: {e}")

    try:
        initialize_hardware_libs(simulate=args.simulate)
    except Exception as e:
        print(f"Notice: {e}")

    # Initialize each sensor safely
    soil = None
    water = None
    dht = None
    compass = None
    gps = None

    try:
        soil = SoilSensor()
        print("✅ Soil Sensor (ADS1115 A0) initialized.")
    except Exception as e:
        print(f"⚠️ Soil Sensor notice: {e}")

    try:
        water = WaterLevelSensor()
        print("✅ HW-038 Water Sensor (ADS1115 A1) initialized.")
    except Exception as e:
        print(f"⚠️ Water Sensor notice: {e}")

    try:
        dht = DHTSensor()
        print("✅ DHT11 Sensor (GPIO 4) initialized.")
    except Exception as e:
        print(f"⚠️ DHT11 notice: {e}")

    try:
        compass = CompassSensor()
        print("✅ Compass (I2C) initialized.")
    except Exception as e:
        print(f"⚠️ Compass notice: {e}")

    try:
        gps = GPSSensor()
        print("✅ NEO-7M GPS (Serial) initialized.")
    except Exception as e:
        print(f"⚠️ GPS notice: {e}")

    print("\nStarting live diagnostic loop... (Press Ctrl+C to stop)\n")
    count = 0
    while True:
        try:
            count += 1
            raw_s, soil_pct = soil.read_percentage() if soil else (0, None)
            raw_w, water_pct, water_status = water.read_percentage() if water else (0, None, "UNKNOWN")
            temp, hum = dht.read() if dht else (None, None)
            heading = compass.read_heading() if compass else None
            gps_fix = gps.read_fix() if gps else None

            s_str = f"{soil_pct:.1f}% (ADC:{raw_s})" if soil_pct is not None else f"-- (ADC:{raw_s})"
            w_str = f"{water_pct:.1f}% [{water_status}] (ADC:{raw_w})" if water_pct is not None else f"-- (ADC:{raw_w})"
            t_str = f"{temp:.1f}°C" if temp is not None else "--"
            h_str = f"{hum:.1f}%" if hum is not None else "--"
            c_str = f"{heading:.1f}°" if heading is not None else "--"
            g_str = f"Lat:{gps_fix.get('lat', '--'):.4f}, Lon:{gps_fix.get('lon', '--'):.4f}" if (gps_fix and gps_fix.get('valid')) else "Searching..."

            print(f"[{count:03d}] Soil: {s_str:<18} | Water: {w_str:<26} | Temp: {t_str:>6} | Hum: {h_str:>6} | Heading: {c_str:>6} | GPS: {g_str}")

            if args.push:
                payload = {
                    "soil_moisture": soil_pct,
                    "raw_adc": raw_s,
                    "water_level": water_pct,
                    "water_status": water_status,
                    "temperature": temp,
                    "humidity": hum,
                    "heading_deg": heading,
                    "gps": gps_fix,
                    "current_state": "BENCH_DIAGNOSTIC",
                    "navigation_status": "IDLE",
                    "pump_state": False,
                    "cutter_state": False,
                    "uptime_seconds": int(time.time())
                }
                push_to_aws(payload)

            time.sleep(2.0)
        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as e:
            print(f"Loop notice: {e}")
            time.sleep(2.0)


if __name__ == "__main__":
    main()
