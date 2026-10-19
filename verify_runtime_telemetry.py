#!/usr/bin/env python3
"""
AgroNex-Pi: Real Telemetry Runtime Verification Script
Starts main.py as a subprocess, monitors AWSRelay telemetry pushing,
validates payload fields, verifies AWS /state API, and tracks timestamp updates over 30s.
"""

import subprocess
import sys
import time
import json
import requests

AWS_STATE_URL = "https://fyxosg11ad.execute-api.ap-south-1.amazonaws.com/state"
PYTHON_EXE = sys.executable

def main():
    print("=" * 70)
    print("  AGRONEX-PI RUNTIME & AWS TELEMETRY VERIFICATION")
    print("=" * 70)

    # 1. Start the actual AgroNex-Pi supervisor/runtime
    cmd = [PYTHON_EXE, "-u", "main.py", "--simulate", "--port", "5055"]
    print(f"\n[1] Starting AgroNex-Pi supervisor runtime:\n    {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace"
    )

    relay_started = False
    first_payload = None
    first_push_success = False
    captured_logs = []

    start_wait = time.time()
    # Read process output until the first payload and push are observed (up to 45 seconds)
    print("\n[2] Monitoring runtime output for AWSRelay initialization and first telemetry push...")
    while time.time() - start_wait < 45:
        line = proc.stdout.readline()
        if line:
            clean_line = line.rstrip()
            captured_logs.append(clean_line)
            # Print relevant log lines
            if any(k in clean_line for k in ["AWSRelay", "SELF_TEST", "Flask Dashboard", "prepared for POST", "First push"]):
                print(f"    {clean_line}")

            if "AWS Relay thread started" in clean_line:
                relay_started = True

            if "First push successful" in clean_line:
                first_push_success = True
                break
        else:
            if proc.poll() is not None:
                print(f"[-] Subprocess exited prematurely with code {proc.returncode}")
                break
            time.sleep(0.1)

    print(f"\n    -> AWSRelay started: {relay_started}")
    print(f"    -> First push confirmed by runtime: {first_push_success}")

    # Find the payload from captured logs
    payload_lines = []
    recording = False
    for l in captured_logs:
        if "Telemetry payload prepared for POST:" in l:
            recording = True
            continue
        if recording:
            payload_lines.append(l)
            if l.strip() == "}":
                # Check if it closes the root object
                candidate = "\n".join(payload_lines)
                try:
                    first_payload = json.loads(candidate)
                    break
                except Exception:
                    continue

    print("\n[3] Actual Telemetry Payload Prepared by Runtime:")
    if first_payload:
        print(json.dumps(first_payload, indent=2))
    else:
        print("    (Raw payload log captured)")

    # 4. Verify required fields
    required_fields = [
        "soil_moisture", "temperature", "humidity", "heading_deg",
        "gps", "pump_state", "cutter_state", "current_state", "device_id"
    ]
    print("\n[4] Verifying payload fields:")
    telemetry_data = first_payload.get("telemetry", {}) if (first_payload and isinstance(first_payload, dict)) else {}
    fields_present = {}
    for f in required_fields:
        if f == "device_id":
            val = (first_payload.get("device_id") if first_payload else None) or telemetry_data.get("device_id")
        else:
            val = telemetry_data.get(f)
        fields_present[f] = val is not None
        print(f"    - {f:15s} : {str(val):25s} [{'PASS' if fields_present[f] else 'FAIL'}]")

    # 5 & 6. GET /state from AWS
    print("\n[5 & 6] Querying AWS GET /state immediately...")
    try:
        r = requests.get(AWS_STATE_URL, timeout=8)
        print(f"    HTTP Status: {r.status_code}")
        aws_json = r.json()
        print(f"    AWS /state response:\n{json.dumps(aws_json, indent=2)}")
    except Exception as e:
        print(f"[-] Failed to fetch AWS /state: {e}")
        aws_json = {}

    # 7. Confirm returned AWS state contains the same fields
    print("\n[7] Comparing AWS returned state fields:")
    aws_data = aws_json.get("data", {})
    for f in required_fields:
        val = aws_data.get(f)
        if f == "device_id" and val is None:
            val = aws_data.get("_device_id")
        print(f"    - AWS state.{f:13s} : {str(val):25s} [{'PASS' if val is not None else 'FAIL'}]")

    # 8 & 9. Run for at least 15-30 seconds and check timestamp updates
    print("\n[8 & 9] Monitoring AWS /state over the next 20 seconds for periodic updates...")
    timestamps = [aws_data.get("_received_at")]
    print(f"    Initial timestamp (t=0s) : {timestamps[0]}")

    for i in range(1, 4):
        time.sleep(7)
        try:
            r = requests.get(AWS_STATE_URL, timeout=8)
            curr_data = r.json().get("data", {})
            curr_ts = curr_data.get("_received_at")
            timestamps.append(curr_ts)
            print(f"    Poll #{i} (t~{i*7}s)      : {curr_ts} (State: {curr_data.get('current_state')}, Soil: {curr_data.get('soil_moisture')}%)")
        except Exception as e:
            print(f"    Poll #{i} failed: {e}")

    # Check that timestamps updated and did not revert
    unique_ts = set(t for t in timestamps if t)
    print(f"\n    -> Total distinct timestamps recorded: {len(unique_ts)}")
    print(f"    -> Telemetry streaming continuously : {'YES (PASS)' if len(unique_ts) > 1 else 'NO (FAIL)'}")

    # Check for payload completeness during stream
    intact = all(curr_data.get(f) is not None or (f == "device_id" and curr_data.get("_device_id")) for f in required_fields)
    print(f"    -> Payload remains complete (no overwrite with incomplete data): {'YES (PASS)' if intact else 'NO (FAIL)'}")

    # Graceful shutdown of runtime
    print("\n[10] Shutting down supervisor runtime cleanly...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    print("    -> Subprocess terminated.")

    print("\n" + "=" * 70)
    print("  VERIFICATION COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    main()
