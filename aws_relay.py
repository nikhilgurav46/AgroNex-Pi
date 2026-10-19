#!/usr/bin/env python3
"""
AgroNex-Pi: AWS Cloud Relay (§5.8)

Runs as a background thread inside main.py.
Pushes a telemetry snapshot + latest disease scan to AWS API Gateway
every AWS_RELAY_INTERVAL seconds.

AWS Architecture:
  Raspberry Pi  ─ HTTP POST ─►  API Gateway  ─►  Lambda  ─►  S3 bucket
  (this file)                   /telemetry         stores state.json
                                /command           reads pending commands
                                /scan              uploads disease scan image

Environment variables (set on Pi, or in .env):
  AGRONEX_AWS_URL   Full API Gateway invoke URL  e.g. https://abc123.execute-api.ap-south-1.amazonaws.com/prod
  AGRONEX_AWS_KEY   Optional x-api-key header value
"""

import threading
import time
import logging
import json
import base64
import os
import datetime

logger = logging.getLogger("AgroNex.AWSRelay")

try:
    import requests as _requests
    _REQUESTS_OK = True
except ImportError:
    _requests = None
    _REQUESTS_OK = False


class AWSRelay:
    """
    Background thread that periodically pushes AgroNex telemetry to AWS API Gateway.
    Also polls /command endpoint to receive remote control commands from the cloud dashboard.
    """

    def __init__(self, get_telemetry_fn, handle_command_fn=None, run_detection_fn=None):
        """
        Args:
            get_telemetry_fn: callable -> dict  (returns current telemetry snapshot)
            handle_command_fn: callable(cmd: str) -> None  (optional command handler)
            run_detection_fn: callable(image_path: str) -> dict  (optional).
                Should run the same pipeline as DiseaseDetector.detect_from_image_path()
                and return a result dict containing at least: label, common_name,
                confidence, cause, treatment, is_healthy, quality_flag.
        """
        import config
        raw_url = config.AWS_API_URL.strip().rstrip("/")
        if raw_url.endswith("/prod"):
            raw_url = raw_url[:-5]
        self.api_url = raw_url
        self.api_key = config.AWS_API_KEY
        self.interval = config.AWS_RELAY_INTERVAL
        self.enabled = config.AWS_ENABLED
        self.get_telemetry = get_telemetry_fn
        self.handle_command = handle_command_fn
        self.run_detection = run_detection_fn
        self._stop_event = threading.Event()
        self._thread = None
        self._last_scan_id = None     # track which scan we last uploaded
        self._push_count = 0
        self._error_count = 0
        self._scan_req_counter = 0
        self._snapshot_counter = 0
        self._snapshot_interval = getattr(config, 'CAMERA_SNAPSHOT_INTERVAL', 60)   # seconds (default 1m)
        self._latest_snapshot_url = None
        self._latest_snapshot_time = None

        if not _REQUESTS_OK:
            logger.warning("AWS Relay: 'requests' library not installed. Run: pip install requests")
            self.enabled = False

        if not self.enabled:
            logger.info("AWS Relay disabled (set AGRONEX_AWS_URL env var to activate).")
        else:
            logger.info(f"AWS Relay enabled -> {self.api_url}")

    # ─── Public API ──────────────────────────────────────────────────────────

    def start(self):
        if not self.enabled:
            return
        self._thread = threading.Thread(target=self._loop, daemon=True, name="AWSRelay")
        self._thread.start()
        logger.info("AWS Relay thread started.")

    def stop(self):
        self._stop_event.set()

    def push_telemetry_now(self):
        """Immediately pushes telemetry in a background worker (e.g. after state change)."""
        if not self.enabled or not _REQUESTS_OK:
            return
        threading.Thread(target=self._push_telemetry, daemon=True, name="AWSTelemetryPushNow").start()

    def push_scan_image(self, image_path: str, result: dict):
        """Call this immediately after a disease scan to upload the image + result to AWS."""
        if not self.enabled or not _REQUESTS_OK:
            return
        threading.Thread(
            target=self._upload_scan,
            args=(image_path, result),
            daemon=True,
            name="AWSScanUpload"
        ).start()

    def start_camera_snapshot_thread(self):
        """
        Starts a dedicated background thread that captures a camera JPEG every
        CAMERA_SNAPSHOT_INTERVAL seconds and POSTs it to the /snapshot AWS endpoint.
        Call this AFTER the Camera singleton has been initialised in main.py.
        """
        if not self.enabled or not _REQUESTS_OK:
            logger.info("AWS Relay: camera snapshot thread not started (relay disabled).")
            return
        t = threading.Thread(
            target=self._snapshot_loop,
            daemon=True,
            name="AWSCameraSnapshot"
        )
        t.start()
        logger.info(f"AWS Relay: camera snapshot thread started (interval={self._snapshot_interval}s).")

    # ─── Internal ────────────────────────────────────────────────────────────

    def _headers(self):
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["x-api-key"] = self.api_key
        return h

    def _loop(self):
        # Poll commands at 2x frequency of telemetry for fast response
        _cmd_poll_counter = 0
        while not self._stop_event.is_set():
            try:
                self._push_telemetry()
                self._poll_commands()         # always poll commands every cycle
                self._poll_scan_requests()
            except Exception as e:
                self._error_count += 1
                if self._error_count <= 3 or self._error_count % 10 == 0:
                    logger.warning(f"AWS Relay loop error (#{self._error_count}): {e}")
            # Use 2s wait between cycles for faster command acknowledgement
            self._stop_event.wait(min(self.interval, 2.0))

    def _snapshot_loop(self):
        """Dedicated loop: captures Pi camera frame and uploads to AWS /snapshot every N seconds."""
        # Lazy import to avoid crash on PC where Camera is unavailable
        try:
            from hardware import Camera
        except ImportError:
            logger.warning("AWS Relay: cannot import Camera -- snapshot loop exiting.")
            return
        logger.info("AWS Relay: camera snapshot loop running.")
        while not self._stop_event.is_set():
            try:
                cam = Camera.get_instance()
                jpeg_bytes = cam.capture_jpeg()
                self._upload_snapshot(jpeg_bytes)
            except Exception as e:
                # Camera may not be ready yet on startup -- silently retry
                logger.debug(f"AWS snapshot capture skipped: {e}")
            self._stop_event.wait(self._snapshot_interval)

    def _upload_snapshot(self, jpeg_bytes: bytes):
        """POSTs a base64-encoded JPEG to the AWS /snapshot endpoint."""
        if not _REQUESTS_OK:
            return
        try:
            img_b64 = base64.b64encode(jpeg_bytes).decode("utf-8")
            payload = {
                "device_id": "agronex-pi-001",
                "timestamp": datetime.datetime.now().isoformat(),
                "image_b64": img_b64,
                "content_type": "image/jpeg"
            }
            r = _requests.post(
                f"{self.api_url}/snapshot",
                json=payload,
                headers=self._headers(),
                timeout=8
            )
            self._snapshot_counter += 1
            if self._snapshot_counter == 1:
                logger.info(f"AWS Relay: first camera snapshot uploaded! ({len(jpeg_bytes)//1024} KB)")
            elif self._snapshot_counter % 20 == 0:
                logger.info(f"AWS Relay: {self._snapshot_counter} snapshots uploaded.")
            if r.status_code == 200:
                data = r.json()
                # Store the S3 URL in relay and telemetry cache
                snapshot_url = data.get("snapshot_url", "")
                if snapshot_url:
                    self._latest_snapshot_url = snapshot_url
                    self._latest_snapshot_time = payload.get("timestamp")
                    try:
                        from app import _telemetry_cache
                        _telemetry_cache["camera_snapshot_url"] = snapshot_url
                        _telemetry_cache["camera_snapshot_time"] = self._latest_snapshot_time
                    except Exception:
                        pass
        except Exception as e:
            logger.debug(f"AWS snapshot upload error: {e}")

    def _push_telemetry(self):
        telemetry = dict(self.get_telemetry())
        if "device_id" not in telemetry:
            telemetry["device_id"] = "agronex-pi-001"
        if self._latest_snapshot_url:
            telemetry["camera_snapshot_url"] = self._latest_snapshot_url
            telemetry["camera_snapshot_time"] = self._latest_snapshot_time
        payload = {
            "device_id": "agronex-pi-001",
            "timestamp": datetime.datetime.now().isoformat(),
            "telemetry": telemetry
        }
        if self._push_count == 0:
            logger.info(f"AWS Relay: Telemetry payload prepared for POST:\n{json.dumps(payload, indent=2, default=str)}")
        r = _requests.post(
            f"{self.api_url}/telemetry",
            json=payload,
            headers=self._headers(),
            timeout=8
        )
        if r.status_code == 200:
            self._push_count += 1
            if self._push_count == 1:
                logger.info(f"AWS Relay: First push successful! Status 200: {r.text.strip()}")
            elif self._push_count % 12 == 0:   # log every ~60 s
                logger.info(f"AWS Relay: {self._push_count} pushes sent.")
        else:
            logger.warning(f"AWS Relay telemetry push failed: {r.status_code} {r.text[:80]}")

    def _poll_commands(self):
        if self.handle_command is None:
            return
        try:
            r = _requests.get(
                f"{self.api_url}/command",
                headers=self._headers(),
                timeout=5
            )
            if r.status_code == 200:
                data = r.json()
                cmd = data.get("command", "").strip()
                if cmd:
                    logger.info(f"AWS Relay: received command '{cmd}' — EXECUTING NOW")
                    try:
                        self.handle_command(cmd)
                        logger.info(f"AWS Relay: command '{cmd}' executed successfully ✓")
                        # Push telemetry immediately so dashboard sees state change
                        threading.Thread(target=self._push_telemetry, daemon=True).start()
                    except Exception as ex:
                        logger.error(f"AWS Relay: command '{cmd}' execution failed: {ex}")
            elif r.status_code != 200:
                logger.debug(f"AWS Relay: command poll returned {r.status_code}")
        except Exception as e:
            logger.debug(f"AWS Relay: command poll error: {e}")

    def _poll_scan_requests(self):
        """Poll GET /scan_request for a photo queued by the mobile dashboard.
        If found, run the Pi's on-device DiseaseDetector and post result via POST /scan.
        """
        if self.run_detection is None or not _REQUESTS_OK:
            return
        try:
            r = _requests.get(
                f"{self.api_url}/scan_request",
                headers=self._headers(),
                timeout=8
            )
            if r.status_code != 200:
                return
            data = r.json()
            if not data.get("pending"):
                return
            img_b64 = data.get("image_b64", "")
            if not img_b64:
                return
            import config
            os.makedirs(config.SCANS_DIR, exist_ok=True)
            ts = time.strftime("%Y%m%d_%H%M%S")
            saved_path = os.path.join(config.SCANS_DIR, f"scan_cloud_{ts}.jpg")
            with open(saved_path, "wb") as f:
                f.write(base64.b64decode(img_b64))
            self._scan_req_counter += 1
            logger.info(f"AWS Relay: received queued phone photo (#{self._scan_req_counter}), running detection...")
            result = self.run_detection(saved_path)
            # Also log locally so it appears in local dashboard / agronex.db
            try:
                from app import get_db
                db = get_db()
                if db and result.get("success", True):
                    db.log_disease_scan(
                        label=result.get("label", "UNKNOWN"),
                        common_name=result.get("common_name", "Leaf Scan"),
                        confidence=float(result.get("confidence", 0.0)),
                        image_path=f"static/scans/{os.path.basename(saved_path)}",
                        quality_flag=result.get("quality_flag", "QUALITY_OK"),
                        simulated=False,
                    )
            except Exception as e:
                logger.info(f"Local DB log skipped (running standalone?): {e}")
            # Push finished result + image to AWS so it appears in GET /scans
            self._upload_scan(saved_path, result)
        except Exception as e:
            logger.info(f"AWS Relay: scan_request poll skipped ({e})")

    def _upload_scan(self, image_path: str, result: dict):
        try:
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
            payload = {
                "device_id": "agronex-pi-001",
                "timestamp": datetime.datetime.now().isoformat(),
                "image_b64": img_b64,
                "result": result
            }
            r = _requests.post(
                f"{self.api_url}/scan",
                json=payload,
                headers=self._headers(),
                timeout=20
            )
            if r.status_code == 200:
                logger.info("AWS Relay: disease scan image uploaded.")
            else:
                logger.warning(f"AWS scan upload failed: {r.status_code}")
        except Exception as e:
            logger.warning(f"AWS scan upload error: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    print("\n" + "=" * 60)
    print("   AgroNex-Pi AWS Cloud Relay Diagnostic Tool")
    print("=" * 60)

    import config
    print(f"[*] Target AWS URL : {config.AWS_API_URL}")
    print(f"[*] AWS Enabled    : {config.AWS_ENABLED}")

    test_telemetry = {
        "soil_moisture": 58.4,
        "temperature": 27.8,
        "humidity": 65.0,
        "heading_deg": 135.0,
        "gps": {"lat": 19.0760, "lon": 72.8777, "latitude": 19.0760, "longitude": 72.8777},
        "pump_state": False,
        "cutter_state": False,
        "current_state": "DIAGNOSTIC_TEST",
        "simulation_mode": True,
        "uptime_seconds": 120
    }

    relay = AWSRelay(get_telemetry_fn=lambda: test_telemetry)
    print("\n[+] Pushing test telemetry snapshot to AWS...")
    relay._push_telemetry()

    print("[+] Polling for pending remote commands from AWS...")
    relay.handle_command = lambda cmd: print(f"    >>> RECEIVED COMMAND: {cmd}")
    relay._poll_commands()

    print("\n[OK] Diagnostic completed.")
    print("=" * 60 + "\n")
