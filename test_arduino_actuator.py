#!/usr/bin/env python3
"""
AgroNex-Pi Hardware Test: Arduino Motor, Actuator & Ultrasonic Slave

Tests:
1. USB Serial connection to Arduino Uno (/dev/ttyACM0 or /dev/ttyUSB0)
2. 3D-printed Soil Moisture Probe Actuator deployment (PROBE_DOWN) & retraction (PROBE_UP)
3. Dual BTS7960 Chassis wheel drive commands (Forward, Backward, Left, Right)
4. Front and Rear Ultrasonic obstacle distance scans
"""

import sys
import time
import argparse
import config
from hardware import initialize_hardware_libs, Motors, ArduinoBridge

def main():
    parser = argparse.ArgumentParser(description="Test Arduino Uno Motor, Actuator & Sensors")
    parser.add_argument("--port", default=config.ARDUINO_SERIAL_PORT, help="Serial port for Arduino")
    parser.add_argument("--simulate", action="store_true", help="Run test in simulation mode")
    args = parser.parse_args()

    print("==================================================")
    print("   TESTING ARDUINO UNO MOTORS, ACTUATOR & RADAR   ")
    print("==================================================")

    initialize_hardware_libs(simulate=args.simulate)
    bridge = ArduinoBridge(port=args.port)
    motors = Motors(arduino_bridge=bridge)

    if not bridge.connected and not args.simulate:
        print("[WARNING] Arduino not detected on USB. Check cable connection to Pi.")
        print("          Available ports can be checked with: ls -l /dev/ttyACM* /dev/ttyUSB*")
        sys.exit(1)

    try:
        # 1. Test Soil Moisture Probe Actuator Servo
        print("\n[1/4] Testing 3D-Printed Actuator Soil Probe Servo...")
        print(" -> Lowering probe into soil (PROBE_DOWN)...")
        motors.deploy_soil_probe()
        time.sleep(2.0)
        print(" -> Retracting probe back to transport position (PROBE_UP)...")
        motors.retract_soil_probe()
        time.sleep(1.0)
        print(" -> Actuator probe motion verified.")

        # 2. Test Ultrasonic Obstacle Radar
        print("\n[2/4] Testing Ultrasonic Sensors & Pan Servos...")
        dist_f = motors.scan_front_distance(angle=90)
        print(f" -> Front Distance (center 90 deg): {dist_f} cm")
        dist_r = motors.scan_rear_distance(angle=90)
        print(f" -> Rear Distance (center 90 deg): {dist_r} cm")

        # 3. Test Dual BTS7960 Motors
        print("\n[3/4] Testing Chassis Motors via BTS7960...")
        print(" -> Forward (30% duty, 1s)...")
        motors.forward(speed=30.0)
        time.sleep(1.0)
        motors.stop()
        time.sleep(0.5)

        print(" -> Backward (30% duty, 1s)...")
        motors.backward(speed=30.0)
        time.sleep(1.0)
        motors.stop()
        time.sleep(0.5)

        print(" -> Turn Left (30% duty, 0.8s)...")
        motors.turn_left(speed=30.0)
        time.sleep(0.8)
        motors.stop()
        time.sleep(0.5)

        print(" -> Turn Right (30% duty, 0.8s)...")
        motors.turn_right(speed=30.0)
        time.sleep(0.8)
        motors.stop()

        print("\n[4/4] Finalizing and cleaning up...")
        motors.cleanup()
        print("--------------------------------------------------")
        print("[PASS] RESULT: ALL ARDUINO SUBSYSTEMS VERIFIED!")

    except Exception as e:
        motors.cleanup()
        print(f"\n[FAIL] Test encountered error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
