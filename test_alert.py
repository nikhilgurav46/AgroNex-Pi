#!/usr/bin/env python3
"""
AgroNex-Pi Hardware Test: Buzzer & Red LED Alerts (§10)

Tests piezo buzzer on GPIO22 and red alert LED on GPIO23.
Fires a 2-second pulsed alert pattern.
"""

import sys
import time
import argparse

import config
from hardware import initialize_hardware_libs, Alerts

def main():
    parser = argparse.ArgumentParser(description="Test Buzzer & LED Alert Outputs")
    parser.add_argument("--simulate", action="store_true", help="Run test in simulation mode")
    args = parser.parse_args()

    print("==================================================")
    print("      TESTING BUZZER (GPIO22) & LED (GPIO23)      ")
    print("==================================================")

    try:
        initialize_hardware_libs(simulate=args.simulate)
        alerts = Alerts()
    except Exception as e:
        print(f"❌ FAIL: Alert driver initialization failed: {e}")
        sys.exit(1)

    try:
        print("[+] Triggering 2-second alert pulse pattern...")
        alerts.alert_disease(duration=2.0)
        time.sleep(2.5)
        alerts.cleanup()

        print("--------------------------------------------------")
        print("[PASS] RESULT: PASS (Buzzer and LED alert test complete)")

    except Exception as e:
        alerts.cleanup()
        print(f"[FAIL] RESULT: FAIL ({e})")
        sys.exit(1)

if __name__ == "__main__":
    main()
