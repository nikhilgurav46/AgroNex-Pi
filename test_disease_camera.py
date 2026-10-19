#!/usr/bin/env python3
"""
AgroNex-Pi: Live Camera Disease Detection Diagnostic Tool

Tests the camera (Picamera2 CSI or USB webcam) and runs the trained
TensorFlow Lite plant disease classification model in real time.

Usage on Raspberry Pi:
  python test_disease_camera.py
  python test_disease_camera.py --loop       # Continuous detection every 3 seconds
  python test_disease_camera.py --image path # Test on a saved image file
  python test_disease_camera.py --simulate   # Test on PC with sample leaf
"""

import os
import sys
import time
import argparse
import numpy as np

# Force UTF-8 terminal encoding
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import config
from disease_detect import DiseaseDetector
from disease_db import get_disease_info

try:
    import cv2
except ImportError:
    cv2 = None


def get_camera_frame(cam_instance=None):
    """Captures RGB frame from Picamera2 or USB Webcam."""
    # 1. Try Picamera2 (CSI camera on Raspberry Pi)
    if cam_instance is not None:
        try:
            frame = cam_instance.capture_array()
            if frame is not None and frame.size > 0:
                return frame
        except Exception as e:
            print(f"  [!] Picamera2 capture error: {e}")

    # 2. Try OpenCV VideoCapture (webcam fallback, checking video devices)
    if cv2 is not None:
        for dev_idx in [0, 1, 2, 4]:
            try:
                cap = cv2.VideoCapture(dev_idx)
                if cap.isOpened():
                    ret, bgr = None, None
                    for _ in range(5):
                        ret, bgr = cap.read()
                    cap.release()
                    if ret and bgr is not None and bgr.size > 0:
                        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            except Exception:
                pass

    return None



def print_diagnosis_report(res: dict, saved_path: str = None):
    """Displays a clean, professional agronomic diagnosis card in the terminal."""
    common_name = res.get("common_name", res.get("label", "Unknown"))
    is_healthy = bool(res.get("is_healthy", False))
    conf = res.get("confidence", 0.0) * 100
    plant = res.get("plant_type", "Crop")
    cause = res.get("cause", "N/A")
    symptoms = res.get("symptoms", "N/A")
    treatment = res.get("treatment", "Maintain balanced soil nutrition and proper irrigation.")
    infer_time = res.get("inference_time_ms", 0.0)
    leaf_count = res.get("leaf_count", 1)

    print("\n" + "=" * 65)
    print("        🌱  AGRONEX-PI PLANT HEALTH DIAGNOSTIC REPORT  🌱")
    print("=" * 65)
    print(f"  Crop / Plant     : {plant}")
    print(f"  Diagnosis        : {common_name}")
    if is_healthy:
        print("  Health Status    : \033[92m[PASS] HEALTHY VIGOR (No Disease Detected)\033[0m")
    else:
        print("  Health Status    : \033[91m[ALERT] DISEASE / PATHOGEN DETECTED\033[0m")
    print(f"  Confidence Score : {conf:.1f}%")
    print(f"  Inference Latency: {infer_time} ms")
    if leaf_count > 1:
        print(f"  Leaves Segmented : {leaf_count} individual leaves analyzed")
    print("-" * 65)
    print("  SYMPTOMS:")
    print(f"    {symptoms}")
    print("\n  AGRONOMIC ACTION / CURE:")
    print(f"    {treatment}")
    print("-" * 65)
    if saved_path:
        print(f"  Saved Image      : {saved_path}")
    print("=" * 65 + "\n")


def annotate_and_save(frame_rgb: np.ndarray, res: dict, out_path: str):
    """Draws leaf bounding boxes and diagnosis text on the image."""
    if cv2 is None:
        try:
            from PIL import Image
            Image.fromarray(frame_rgb).save(out_path)
        except Exception:
            pass
        return

    bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
    h, w = bgr.shape[:2]

    # Draw segmented leaf boxes if available
    for leaf in res.get("per_leaf_results", []):
        bbox = leaf.get("bbox")
        if bbox:
            bx, by, bw, bh = bbox
            color = (0, 220, 0) if leaf.get("is_healthy", False) else (0, 0, 220)
            cv2.rectangle(bgr, (bx, by), (bx + bw, by + bh), color, 2)

    # Top overlay banner
    is_healthy = res.get("is_healthy", False)
    banner_color = (30, 140, 30) if is_healthy else (30, 30, 190)
    cv2.rectangle(bgr, (0, 0), (w, 55), banner_color, -1)

    label_text = f"{res.get('common_name', res.get('label'))} ({res.get('confidence', 0)*100:.1f}%)"
    cv2.putText(bgr, label_text, (12, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imwrite(out_path, bgr)


def main():
    parser = argparse.ArgumentParser(description="AgroNex-Pi Camera Disease Detection Test")
    parser.add_argument("--image", type=str, default="", help="Path to existing image file to test")
    parser.add_argument("--loop", action="store_true", help="Continuously detect leaf every 3 seconds")
    parser.add_argument("--simulate", action="store_true", help="Run with simulated frame on PC")
    parser.add_argument("--model", type=str, default=config.MODEL_PATH, help="Path to TFLite model file")
    parser.add_argument("--labels", type=str, default=config.LABELS_PATH, help="Path to labels.txt file")
    args = parser.parse_args()

    print("\n" + "=" * 65)
    print("       AgroNex-Pi Camera & TFLite Model Live Tester")
    print("=" * 65)

    # 1. Initialize TFLite Detector
    print("[1/3] Loading TFLite model & labels...")
    try:
        detector = DiseaseDetector(
            model_path=args.model,
            labels_path=args.labels,
            simulate=args.simulate
        )
        print(f"      Loaded {len(detector.labels)} target classes from '{args.labels}'.")
    except Exception as e:
        print(f"[!] Failed to load disease detector: {e}")
        print(f"   Make sure '{args.model}' and '{args.labels}' exist.")
        sys.exit(1)

    # If test image provided, process directly
    if args.image:
        if not os.path.exists(args.image):
            print(f"[!] Image not found: {args.image}")
            sys.exit(1)
        print(f"[2/3] Analyzing image file '{args.image}'...")
        res = detector.detect_from_image_path(args.image)
        print_diagnosis_report(res)
        return

    # 2. Initialize Camera
    print("[2/3] Initializing Camera...")
    cam = None
    if not args.simulate:
        try:
            from hardware import initialize_hardware_libs, Camera
            initialize_hardware_libs(simulate=False)
            cam = Camera.get_instance(resolution=(640, 480))
            print("      Picamera2 CSI camera active.")
        except Exception as e:
            print(f"      Picamera2 not detected ({e}). Checking USB webcam fallback...")
            found_cam = False
            if cv2 is not None:
                for dev in [0, 1, 2, 4]:
                    test_cap = cv2.VideoCapture(dev)
                    if test_cap.isOpened():
                        ret, test_frame = test_cap.read()
                        test_cap.release()
                        if ret and test_frame is not None and test_frame.size > 0:
                            print(f"      USB Webcam (device {dev}) detected and active.")
                            found_cam = True
                            break
            if not found_cam and cam is None:
                print("[!] No functional camera frame captured! Run with '--simulate' to test with sample leaves.")
                sys.exit(1)
    else:
        print("      Running in SIMULATION mode.")


    # 3. Detection Routine
    print("[3/3] Ready for leaf disease detection.")
    os.makedirs(config.SCANS_DIR, exist_ok=True)

    iteration = 0
    try:
        while True:
            iteration += 1
            if not args.loop and iteration > 1:
                break

            print("\n📸 Hold a leaf in front of the camera...")
            if not args.loop:
                input("   Press ENTER to take photo and analyze...")

            print("   Capturing frame...")
            if args.simulate:
                # Load sample from PlantVillage if present, else synthetic
                frame_rgb = None
                for test_folder in ["Tomato_Early_blight", "Tomato___Early_blight", "Tomato_healthy", "Potato___Early_blight"]:
                    folder_path = os.path.join(config.BASE_DIR, "plantvillage_dataset", "PlantVillage", test_folder)
                    if os.path.exists(folder_path):
                        files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                        if files:
                            sample_bgr = cv2.imread(os.path.join(folder_path, files[0])) if cv2 else None
                            if sample_bgr is not None:
                                frame_rgb = cv2.cvtColor(sample_bgr, cv2.COLOR_BGR2RGB)
                                print(f"   (Using sample leaf: {test_folder}/{files[0]})")
                                break
                if frame_rgb is None:
                    frame_rgb = (np.random.randint(60, 210, (480, 640, 3))).astype(np.uint8)
            else:
                frame_rgb = get_camera_frame(cam)

            if frame_rgb is None:
                print("[!] Failed to capture image from camera.")
                if not args.loop:
                    break
                time.sleep(2.0)
                continue

            # Run inference with leaf segmentation
            t0 = time.time()
            res = detector.detect_with_leaf_segmentation(frame_rgb)
            res["inference_time_ms"] = round((time.time() - t0) * 1000.0, 1)

            # Save annotated image
            ts = time.strftime("%Y%m%d_%H%M%S")
            out_filename = f"scan_test_{ts}.jpg"
            out_path = os.path.join(config.SCANS_DIR, out_filename)
            annotate_and_save(frame_rgb, res, out_path)

            print_diagnosis_report(res, saved_path=out_path)

            if args.loop:
                print("   Next scan in 3 seconds... (Press Ctrl+C to stop)")
                time.sleep(3.0)

    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        if cam is not None:
            try:
                cam.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
