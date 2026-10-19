#!/usr/bin/env python3
"""
AgroNex-Pi Hardware Test: OV5647 CSI Camera (§10)

Tests picamera2 initialization and frame capture.
Saves test frame as 'test_camera_capture.jpg'.
"""

import os
import sys
import time
import argparse

import config
from hardware import initialize_hardware_libs, Camera, cv2

def main():
    parser = argparse.ArgumentParser(description="Test Camera Capture via picamera2")
    parser.add_argument("--simulate", action="store_true", help="Run test in simulation mode")
    args = parser.parse_args()

    print("==================================================")
    print("      TESTING PICAMERA2 CAMERA CAPTURE            ")
    print("==================================================")

    try:
        initialize_hardware_libs(simulate=args.simulate)
        cam = Camera.get_instance()
    except Exception as e:
        print(f"❌ FAIL: Camera initialization failed: {e}")
        sys.exit(1)

    try:
        print("[+] Capturing single test frame array...")
        rgb_frame = cam.capture_array()
        print(f"    Frame shape: {rgb_frame.shape}, Dtype: {rgb_frame.dtype}")

        test_out_path = "test_camera_capture.jpg"
        if cv2 is not None and not args.simulate:
            bgr_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(test_out_path, bgr_frame)
            print(f"    Saved test capture image to '{test_out_path}'")

        cam.cleanup()
        print("--------------------------------------------------")
        print("[PASS] RESULT: PASS (Camera capture verified)")

    except Exception as e:
        cam.cleanup()
        print(f"[FAIL] RESULT: FAIL ({e})")
        sys.exit(1)

if __name__ == "__main__":
    main()
