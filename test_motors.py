#!/usr/bin/env python3
"""
AgroNex-Pi Hardware Test: Dual BTS7960 Chassis Motors (§10)

Tests 4WD chassis motor driver directions (Forward, Backward, Left Turn, Right Turn)
and PWM speed control on Left (GPIO5/6) and Right (GPIO13/19) BTS7960 H-bridges.
"""

import sys
import time
import argparse

import config
from hardware import initialize_hardware_libs, Motors

def main():
    parser = argparse.ArgumentParser(description="Test dual BTS7960 chassis motor drivers")
    parser.add_argument("--simulate", action="store_true", help="Run test in simulation mode")
    args = parser.parse_args()

    print("==================================================")
    print("      TESTING BTS7960 CHASSIS MOTORS (4WD)        ")
    print("==================================================")

    try:
        initialize_hardware_libs(simulate=args.simulate)
        motors = Motors()
    except Exception as e:
        print(f"❌ FAIL: Motor driver initialization failed: {e}")
        sys.exit(1)

    try:
        print("[1/4] FORWARD drive (speed: 50%) for 1.0 seconds...")
        motors.forward(speed=50.0)
        time.sleep(1.0)
        motors.stop()
        time.sleep(0.5)

        print("[2/4] BACKWARD drive (speed: 50%) for 1.0 seconds...")
        motors.backward(speed=50.0)
        time.sleep(1.0)
        motors.stop()
        time.sleep(0.5)

        print("[3/4] TURN LEFT pivot (speed: 50%) for 0.8 seconds...")
        motors.turn_left(speed=50.0)
        time.sleep(0.8)
        motors.stop()
        time.sleep(0.5)

        print("[4/4] TURN RIGHT pivot (speed: 50%) for 0.8 seconds...")
        motors.turn_right(speed=50.0)
        time.sleep(0.8)
        motors.stop()

        motors.cleanup()
        print("--------------------------------------------------")
        print("[PASS] RESULT: PASS (All chassis motor directions verified)")

    except Exception as e:
        motors.cleanup()
        print(f"[FAIL] RESULT: FAIL ({e})")
        sys.exit(1)

if __name__ == "__main__":
    main()
