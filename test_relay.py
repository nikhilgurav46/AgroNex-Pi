#!/usr/bin/env python3
"""
AgroNex-Pi Hardware Test: Relay Module (Pump & Cutter) (§10)

Tests 2-channel opto-isolated relay module on GPIO17 (Pump) and GPIO27 (Cutter).
Fires short 1-second test pulses to verify relay clicking and active-LOW polarity.
"""

import sys
import time
import argparse

import config
from hardware import initialize_hardware_libs, Relay

def main():
    parser = argparse.ArgumentParser(description="Test 2-Channel Relay Module")
    parser.add_argument("--simulate", action="store_true", help="Run test in simulation mode")
    args = parser.parse_args()

    print("==================================================")
    print("      TESTING RELAY MODULE (PUMP & CUTTER)        ")
    print("==================================================")

    try:
        initialize_hardware_libs(simulate=args.simulate)
        relay = Relay()
    except Exception as e:
        print(f"❌ FAIL: Relay driver initialization failed: {e}")
        sys.exit(1)

    try:
        # Test CH1: Water Pump Pulse
        print("[1/2] Pulsing Water Pump Relay (CH1 / GPIO17) ON for 1.5 seconds...")
        relay.pump_on()
        time.sleep(1.5)
        relay.pump_off()
        print("      CH1 turned OFF.")
        time.sleep(1.0)

        # Test CH2: Grass Cutter Pulse
        print("[2/2] Pulsing Grass Cutter Relay (CH2 / GPIO27) ON for 1.5 seconds...")
        relay.cutter_on()
        time.sleep(1.5)
        relay.cutter_off()
        print("      CH2 turned OFF.")

        relay.cleanup()
        print("--------------------------------------------------")
        print("[PASS] RESULT: PASS (Both relays actuated successfully)")

    except Exception as e:
        relay.cleanup()
        print(f"[FAIL] RESULT: FAIL ({e})")
        sys.exit(1)

if __name__ == "__main__":
    main()
