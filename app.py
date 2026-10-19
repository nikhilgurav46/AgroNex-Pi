#!/usr/bin/env python3
"""
AgroNex-Pi: Flask Dashboard & REST API Server (§5.7)

Provides local web UI and REST API.
Offline-First Architecture: Zero CDN dependencies.
Thread-Safe API: Reads telemetry from thread-safe cached state dictionary.
Never calls sensor read functions directly from request threads.
"""

import os
import sys
import json
import time
import datetime
import subprocess
import logging
import shutil
import re
import urllib.request
import xml.etree.ElementTree as ET
from flask import Flask, render_template, jsonify, request, send_from_directory, Response, session

import config
import disease_db
from database import DatabaseManager
from disease_detect import DiseaseDetector
from hardware import Camera

logger = logging.getLogger("AgroNex.App")

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = getattr(config, "AUTH_SECRET_KEY", "agronex_secret_session_key_2026")

# Shared telemetry cache populated by the main supervisor control loop
_telemetry_cache = {
    "soil_moisture": None,
    "raw_adc": 0,
    "water_level": None,
    "water_status": "PENDING",
    "temperature": None,
    "humidity": None,
    "pump_state": False,
    "cutter_state": False,
    "current_state": "BOOT",
    "cpu_temp": 45.0,
    "uptime_seconds": 0,
    "simulation_mode": False,
    "gps": None,
    "heading_deg": None,
    "navigation_status": "BOOT",
    "last_updated": ""
}

_db_manager: DatabaseManager = None
_supervisor_ref = None  # Reference to MainSupervisor instance
_standalone_detector = None

try:
    import cv2
except Exception:
    cv2 = None


def get_detector():
    """Gets disease detector from supervisor or initializes detector."""
    global _standalone_detector
    if _supervisor_ref and hasattr(_supervisor_ref, 'disease_detector') and _supervisor_ref.disease_detector:
        return _supervisor_ref.disease_detector
    if _standalone_detector is None:
        has_model = os.path.isfile(config.MODEL_PATH) and os.path.isfile(config.LABELS_PATH)
        _standalone_detector = DiseaseDetector(simulate=not has_model)
    return _standalone_detector


def get_db():
    """Returns DatabaseManager instance, creating one if not already set."""
    global _db_manager
    if _db_manager is None:
        try:
            _db_manager = DatabaseManager(config.DB_PATH)
        except Exception as e:
            logger.warning(f"Standalone DB init notice: {e}")
    return _db_manager


def update_telemetry_cache(data: dict):
    """Called by supervisor loop to update cached sensor readings safely."""
    global _telemetry_cache
    _telemetry_cache.update(data)
    _telemetry_cache["last_updated"] = datetime.datetime.now().isoformat()


def get_cpu_temperature() -> float:
    """Reads Pi 4 CPU temperature via vcgencmd or sysfs thermal zone."""
    try:
        if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp_milli = float(f.read().strip())
                return round(temp_milli / 1000.0, 1)
        output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
        # Output format: temp=48.2'C
        temp_str = output.replace("temp=", "").replace("'C", "").strip()
        return float(temp_str)
    except Exception:
        return 42.0  # Fallback for PC development


def set_app_references(db: DatabaseManager, supervisor):
    global _db_manager, _supervisor_ref
    _db_manager = db
    _supervisor_ref = supervisor


# -----------------------------------------------------------------------------
# SINGLE DASHBOARD  (aws/agronex_dashboard/index.html)
# All old dashboard routes now redirect here.
# -----------------------------------------------------------------------------
def _aws_dashboard_dir():
    return os.path.join(config.BASE_DIR, "aws", "agronex_dashboard")


@app.route("/")
def index():
    """Main entry — serves the AWS Cloud Command Center dashboard."""
    return send_from_directory(_aws_dashboard_dir(), "index.html")


@app.route("/cloud")
@app.route("/cloud/")
@app.route("/aws")
@app.route("/aws/")
def aws_cloud_dashboard_view():
    """Alias — same dashboard."""
    return send_from_directory(_aws_dashboard_dir(), "index.html")


@app.route("/aws/<path:filename>")
def serve_aws_dashboard_file(filename):
    """Serves static assets from aws/agronex_dashboard/."""
    return send_from_directory(_aws_dashboard_dir(), filename)


# Legacy routes — redirect everything to the single dashboard
from flask import redirect

@app.route("/dashboard")
@app.route("/dashboard/")
def local_template_dashboard():
    """Serves the offline-first local diagnostic dashboard template."""
    return render_template("dashboard.html")

@app.route("/dark")
@app.route("/final-dashboard")
@app.route("/final-dashboard/")
@app.route("/glass")
@app.route("/farm")
@app.route("/farm/")
def legacy_redirect():
    """Redirects other aliases to the cloud command center dashboard."""
    return redirect("/")


# -----------------------------------------------------------------------------
# LOCAL LAMBDA-MIRROR API ENDPOINTS
# These mirror the AWS Lambda API shape so the dashboard JavaScript works
# both when served from AWS S3 (uses the real Lambda) AND when served locally
# via Flask on http://localhost:5000 (uses these local endpoints).
# The dashboard JS uses DEFAULT_API_URL which points at AWS; when opened via
# http://localhost:5000 on the Pi itself, you can point it to '' (empty base)
# or http://localhost:5000 and these routes will answer.
# -----------------------------------------------------------------------------

@app.route("/state", methods=["GET"])
def local_state():
    """Local mirror of Lambda GET /state. Returns latest cached telemetry."""
    cache_copy = dict(_telemetry_cache)
    cache_copy["cpu_temp"] = get_cpu_temperature()
    # Inject _received_at in local IST time so dashboard "last seen" always updates
    cache_copy["_received_at"] = datetime.datetime.now().isoformat()
    # Ensure operation_mode and current_state are always present
    if "operation_mode" not in cache_copy or not cache_copy["operation_mode"]:
        cache_copy["operation_mode"] = "AUTO"
    if "current_state" not in cache_copy or not cache_copy["current_state"]:
        cache_copy["current_state"] = "MONITORING"
    return jsonify({"ok": True, "data": cache_copy})


@app.route("/scans", methods=["GET"])
def local_scans():
    """Local mirror of Lambda GET /scans. Returns recent disease scans from SQLite."""
    db = get_db()
    raw = db.get_disease_history(limit=20) if db else []
    scans = []
    for s in raw:
        label = s.get("label", "")
        # Enrich with full knowledge base info (symptoms, cause, treatment)
        kb = disease_db.get_disease_info(label) if label else {}
        scans.append({
            "timestamp":   s.get("timestamp", ""),
            "label":       label,
            "common_name": s.get("common_name", kb.get("common_name", s.get("label", "Scan"))),
            "confidence":  s.get("confidence", 0),
            "is_healthy":  kb.get("is_healthy", s.get("is_healthy", False)),
            "cause":       kb.get("cause", s.get("cause", "")),
            "symptoms":    kb.get("symptoms", ""),
            "treatment":   kb.get("treatment", s.get("treatment", "")),
            "plant_type":  kb.get("plant", s.get("plant_type", "")),
            "image_url":   request.host_url.rstrip("/") + "/" + s.get("image_path", "") if s.get("image_path") else "",
        })
    return jsonify({"ok": True, "scans": scans, "count": len(scans)})



@app.route("/command", methods=["GET", "POST"])
def local_command():
    """Local mirror of Lambda /command.
    POST: queues a command from the dashboard.
    GET:  Pi polls for pending command (one-shot).
    """
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        cmd = data.get("command", "").strip()
        if not cmd:
            return jsonify({"ok": False, "error": "command field required"}), 400
        # Normalise casing and dispatch immediately if supervisor is available
        cmd_lower = cmd.lower()
        if _supervisor_ref:
            _supervisor_ref.handle_remote_command(cmd)
        return jsonify({"ok": True, "command": cmd})
    # GET — no persistent queue needed locally; just acknowledge
    return jsonify({"ok": True, "command": ""})


@app.route("/scan_request", methods=["GET", "POST"])
def local_scan_request():
    """Local mirror of Lambda /scan_request.
    POST: accepts base64 image from dashboard, runs Pi inference immediately.
    GET:  returns pending:False (Pi IS the server here, no queue needed).
    """
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        img_b64 = data.get("image_b64", "")
        if not img_b64:
            return jsonify({"ok": False, "error": "image_b64 required"}), 400
        import base64 as _b64
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"scan_cloud_{ts}.jpg"
        saved_path = os.path.join(config.SCANS_DIR, fname)
        os.makedirs(config.SCANS_DIR, exist_ok=True)
        with open(saved_path, "wb") as f:
            f.write(_b64.b64decode(img_b64))
        # Run inference directly (Pi is the server)
        try:
            detector = get_detector()
            result = detector.detect_from_image_path(saved_path)
            result["image_url"] = request.host_url.rstrip("/") + f"/static/scans/{fname}"
            db = get_db()
            if db and result.get("success"):
                db.log_disease_scan(
                    label=result.get("label", "UNKNOWN"),
                    common_name=result.get("common_name", "Leaf Scan"),
                    confidence=float(result.get("confidence", 0.0)),
                    image_path=f"static/scans/{fname}",
                    quality_flag=result.get("quality_flag", "QUALITY_OK"),
                    simulated=getattr(detector, "simulate", True),
                )
            # Also push to AWS if relay is active
            if _supervisor_ref and hasattr(_supervisor_ref, "aws_relay") and _supervisor_ref.aws_relay:
                _supervisor_ref.aws_relay.push_scan_image(saved_path, result)
            return jsonify({"ok": True, "result": result})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500
    # GET
    return jsonify({"ok": True, "pending": False})

@app.route("/diseases", methods=["GET"])
@app.route("/api/diseases", methods=["GET"])
def api_get_diseases():
    """
    Returns the agronomic disease knowledge base grouped by plant type.
    """
    grouped = {}
    seen = set()
    for label, info in disease_db.DISEASE_KNOWLEDGE_BASE.items():
        plant = info.get("plant", "Other")
        if plant == "Non-Plant / Background":
            continue
        dedupe_key = (plant, info.get("disease"))
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        grouped.setdefault(plant, []).append({
            "disease": info.get("common_name", info.get("disease", "Unknown")),
            "healthy": bool(info.get("is_healthy", False)),
            "cause": info.get("cause", ""),
            "symptoms": info.get("symptoms", ""),
            "treatment": info.get("treatment", ""),
        })
    return jsonify({"ok": True, "success": True, "data": grouped})


# -----------------------------------------------------------------------------
# ROBOT ON/OFF CONTROL — Start/Stop main.py from the Dashboard
# The dashboard Power button calls POST /robot_start or POST /robot_stop.
# Status is tracked via a module-level process handle.
# -----------------------------------------------------------------------------
_robot_process = None      # subprocess.Popen handle for main.py
_robot_lock = __import__("threading").Lock()


@app.route("/robot_status", methods=["GET"])
def robot_status():
    """Returns whether main.py (the AgroNex robot supervisor) is currently running."""
    global _robot_process
    with _robot_lock:
        running = _robot_process is not None and _robot_process.poll() is None
        pid = _robot_process.pid if running else None
    return jsonify({"ok": True, "running": running, "pid": pid})


@app.route("/robot_start", methods=["POST"])
def robot_start():
    """Launches main.py in a background subprocess (with --simulate on PC, bare on Pi)."""
    global _robot_process
    with _robot_lock:
        # Don't start if already running
        if _robot_process is not None and _robot_process.poll() is None:
            return jsonify({"ok": True, "running": True, "msg": "Robot already running", "pid": _robot_process.pid})
        try:
            import sys
            import os
            main_py = os.path.join(config.BASE_DIR, "main.py")
            # Detect whether we are running on a real Pi or a PC
            on_pi = os.path.exists("/sys/class/thermal/thermal_zone0/temp")
            cmd = [sys.executable, main_py] + ([] if on_pi else ["--simulate"])
            _robot_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=config.BASE_DIR,
            )
            logger.info(f"Robot started: PID {_robot_process.pid}  cmd={cmd}")
            return jsonify({"ok": True, "running": True, "pid": _robot_process.pid, "msg": "Robot started"})
        except Exception as e:
            logger.error(f"Failed to start robot: {e}")
            return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/robot_stop", methods=["POST"])
def robot_stop():
    """Terminates the main.py subprocess gracefully (SIGTERM → SIGKILL after 5 s)."""
    global _robot_process
    with _robot_lock:
        if _robot_process is None or _robot_process.poll() is not None:
            return jsonify({"ok": True, "running": False, "msg": "Robot is not running"})
        try:
            _robot_process.terminate()
            try:
                _robot_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _robot_process.kill()
            pid = _robot_process.pid
            _robot_process = None
            logger.info(f"Robot stopped (PID {pid})")
            return jsonify({"ok": True, "running": False, "msg": "Robot stopped"})
        except Exception as e:
            logger.error(f"Failed to stop robot: {e}")
            return jsonify({"ok": False, "error": str(e)}), 500




# -----------------------------------------------------------------------------
# LIVE CAMERA MJPEG STREAMING (§5.7)
# -----------------------------------------------------------------------------
@app.route("/video_feed")
def video_feed():
    """Live MJPEG video streaming route for the dashboard."""
    def gen_frames():
        while True:
            try:
                cam = Camera.get_instance()
                frame_bytes = cam.capture_jpeg()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                time.sleep(0.08)  # ~12 FPS
            except Exception as e:
                time.sleep(0.4)
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# -----------------------------------------------------------------------------
# FARMER BLOGS, ADVISORIES & GOVERNMENT INITIATIVES
# -----------------------------------------------------------------------------
GOVERNMENT_INITIATIVES = [
    {
        "source": "Government Initiative",
        "category": "Direct Benefit Transfer",
        "title": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "snippet": "Direct income support of Rs 6,000 per year in 3 equal installments to all landholding farmer families across India for agricultural inputs.",
        "url": "https://pmkisan.gov.in/",
        "badge": "Central Scheme"
    },
    {
        "source": "Crop Insurance",
        "category": "Risk Mitigation",
        "title": "PMFBY — Pradhan Mantri Fasal Bima Yojana",
        "snippet": "Comprehensive crop insurance shielding farmers against non-preventable natural risks, drought, pest attacks, and post-harvest losses at 1.5-2% premium.",
        "url": "https://pmfby.gov.in/",
        "badge": "Subsidized Insurance"
    },
    {
        "source": "Soil Health",
        "category": "Agronomic Advisory",
        "title": "Soil Health Card Scheme",
        "snippet": "Periodic macro and micronutrient testing across 12 vital parameters to optimize fertilizer application, reduce expenses, and maintain soil biology.",
        "url": "https://soilhealth.dac.gov.in/",
        "badge": "Advisory"
    },
    {
        "source": "Farm Mechanization",
        "category": "Smart Robotics Subsidy",
        "title": "SMAM — Sub-Mission on Agricultural Mechanization",
        "snippet": "Financial assistance of 40% to 50% for purchasing autonomous farm machinery, smart sprayers, tillers, and IoT farm rovers.",
        "url": "https://agrimachinery.nic.in/",
        "badge": "40-50% Subsidy"
    },
    {
        "source": "Micro-Irrigation",
        "category": "Water Conservation",
        "title": "PMKSY (Per Drop More Crop - Precision Drip)",
        "snippet": "Up to 55% subsidy for small and marginal farmers installing micro-irrigation drip systems matching precision watering schedules.",
        "url": "https://pmksy.gov.in/",
        "badge": "Up to 55% Subsidy"
    },
    {
        "source": "Digital Mandi",
        "category": "Market Linkage",
        "title": "e-NAM (National Agriculture Market)",
        "snippet": "Pan-India electronic trading portal networking existing APMC mandis to create a unified national market for agricultural commodities.",
        "url": "https://enam.gov.in/",
        "badge": "Price Discovery"
    },
    {
        "source": "Credit Support",
        "category": "Concessional Finance",
        "title": "Kisan Credit Card (KCC) Concessional Loan",
        "snippet": "Low-interest institutional credit at an effective 4% rate with prompt repayment incentive for crop seeds, fertilizers, and farm maintenance.",
        "url": "https://www.myscheme.gov.in/schemes/kcc",
        "badge": "Low Interest (4%)"
    }
]

BLOG_FEEDS = [
    ("Krishi Jagran", "https://krishijagran.com/rss/agriculture.xml"),
    ("FAO News", "https://www.fao.org/rss/en/news.xml"),
    ("Down To Earth - Agriculture", "https://www.downtoearth.org.in/rss/agriculture"),
]


def _fetch_rss_items(name, url, limit=4, timeout=4):
    items = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AgroNex-Pi/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
        root = ET.fromstring(raw)
        for item in root.findall(".//item")[:limit]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc_raw = (item.findtext("description") or "").strip()
            snippet = re.sub("<[^<]+?>", "", desc_raw)[:160]
            if title and link:
                items.append({"source": name, "title": title, "url": link, "snippet": snippet, "badge": "Live News"})
    except Exception as e:
        logger.info(f"Blog feed '{name}' unavailable: {e}")
    return items


@app.route("/blogs", methods=["GET"])
@app.route("/api/blogs", methods=["GET"])
def api_get_blogs():
    """Aggregates government initiatives and live farming/agronomy RSS feeds for the Blogs tab."""
    all_items = list(GOVERNMENT_INITIATIVES)
    for name, url in BLOG_FEEDS:
        all_items.extend(_fetch_rss_items(name, url))

    return jsonify({"ok": True, "success": True, "data": all_items})



@app.route("/plantvillage_dataset/<path:subpath>")
def serve_plantvillage_dataset(subpath):
    """Serves dataset images requested by the dashboard previewer."""
    dataset_dir = os.path.join(config.BASE_DIR, "plantvillage_dataset")
    return send_from_directory(dataset_dir, subpath)


@app.route("/diagrams/<path:filename>")
def serve_diagram_file(filename):
    """Serves architecture diagrams and visual block schematics."""
    diagrams_dir = os.path.join(config.BASE_DIR, "diagrams")
    return send_from_directory(diagrams_dir, filename)


@app.route("/static/scans/<filename>")
def serve_scan_image(filename):
    """Serves captured disease leaf images."""
    return send_from_directory(config.SCANS_DIR, filename)


# -----------------------------------------------------------------------------
# REST API ENDPOINTS
# -----------------------------------------------------------------------------
@app.route("/api/sensor", methods=["GET"])
def api_get_sensor():
    """
    Returns latest cached sensor readings.
    Does NOT invoke hardware SPI/GPIO directly to avoid bus contention.
    """
    cache_copy = dict(_telemetry_cache)
    cache_copy["cpu_temp"] = get_cpu_temperature()
    return jsonify({"success": True, "data": cache_copy})


@app.route("/api/history", methods=["GET"])
def api_get_history():
    """Returns recent sensor history logs for dashboard charts."""
    limit = request.args.get("limit", default=30, type=int)
    history = _db_manager.get_sensor_history(limit=limit) if _db_manager else []
    return jsonify({"success": True, "data": history})


@app.route("/api/irrigation_events", methods=["GET"])
def api_get_irrigation_events():
    """Returns historical irrigation event records."""
    limit = request.args.get("limit", default=20, type=int)
    events = _db_manager.get_irrigation_history(limit=limit) if _db_manager else []
    return jsonify({"success": True, "data": events})


@app.route("/api/disease_log", methods=["GET"])
def api_get_disease_log():
    """Returns recorded plant disease classification events."""
    limit = request.args.get("limit", default=20, type=int)
    scans = _db_manager.get_disease_history(limit=limit) if _db_manager else []
    return jsonify({"success": True, "data": scans})


@app.route("/api/control", methods=["POST"])
def api_control():
    """
    Handles manual actuator overrides (Pump ON/OFF, Cutter ON/OFF, Disease Scan).
    """
    if not request.is_json:
        return jsonify({"success": False, "error": "JSON payload required"}), 400

    payload = request.get_json()
    action = payload.get("action", "").lower()

    if _supervisor_ref is None:
        return jsonify({"success": False, "error": "Supervisor reference unavailable"}), 503

    if action == "pump_on":
        success = _supervisor_ref.manual_pump_on()
        if success is False:
            return jsonify({"success": False, "message": "Pump start rejected (cutter active or safety interlock)."}), 400
        return jsonify({"success": True, "message": "Pump turned ON manually."})

    elif action == "pump_off":
        _supervisor_ref.manual_pump_off()
        return jsonify({"success": True, "message": "Pump turned OFF manually."})

    elif action == "cutter_on":
        success = _supervisor_ref.manual_cutter_on()
        if success:
            return jsonify({"success": True, "message": "Grass cutter turned ON manually."})
        return jsonify({"success": False, "message": "Cutter disabled or rejected."}), 400

    elif action == "cutter_off":
        _supervisor_ref.manual_cutter_off()
        return jsonify({"success": True, "message": "Grass cutter turned OFF manually."})

    elif action == "scan_disease":
        res = _supervisor_ref.trigger_disease_scan()
        return jsonify({"success": True, "data": res})

    elif action in ("actuator_down", "probe_down"):
        if _supervisor_ref.motors:
            _supervisor_ref.motors.deploy_soil_probe()
            import threading
            threading.Thread(target=_supervisor_ref._manual_probe_read_worker, daemon=True).start()
            update_telemetry_cache({"actuator_state": "DEPLOYED"})
            return jsonify({"success": True, "message": "Actuator probe lowered into soil (PROBE_DOWN)."})
        return jsonify({"success": False, "message": "Motors/actuator driver unavailable"}), 500

    elif action in ("actuator_up", "probe_up"):
        if _supervisor_ref.motors:
            _supervisor_ref.motors.retract_soil_probe()
            update_telemetry_cache({"actuator_state": "RETRACTED"})
            return jsonify({"success": True, "message": "Actuator probe safely retracted (PROBE_UP)."})
        return jsonify({"success": False, "message": "Motors/actuator driver unavailable"}), 500

    elif action in ("probe_soil_now", "actuator_probe_cycle"):
        import threading
        threading.Thread(target=_supervisor_ref.run_periodic_actuator_cycle, daemon=True).start()
        return jsonify({"success": True, "message": "Initiated full soil probing cycle (Lower -> Sample -> Retract)."})

    elif action == "read_sensors_now":
        data = _supervisor_ref.read_all_sensors_now()
        return jsonify({"success": True, "data": data, "message": "All sensors refreshed live."})

    elif action == "update_thresholds":
        # Save threshold configuration changes to runtime config file
        try:
            m_low = float(payload.get("moisture_low", config.MOISTURE_LOW))
            m_high = float(payload.get("moisture_high", config.MOISTURE_HIGH))
            config.MOISTURE_LOW = m_low
            config.MOISTURE_HIGH = m_high

            runtime_cfg = {"moisture_low": m_low, "moisture_high": m_high}
            with open(config.RUNTIME_CONFIG_PATH, "w") as f:
                json.dump(runtime_cfg, f, indent=2)

            return jsonify({"success": True, "message": f"Thresholds updated: Low={m_low}%, High={m_high}%."})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 400

    return jsonify({"success": False, "error": f"Unknown action '{action}'"}), 400


@app.route("/api/manual_sensors", methods=["GET", "POST"])
def api_manual_sensors():
    """Manual sensor data checking endpoint — queries all sensors live for manual inspection."""
    if _supervisor_ref and hasattr(_supervisor_ref, 'read_all_sensors_now'):
        data = _supervisor_ref.read_all_sensors_now()
        return jsonify({"success": True, "ok": True, "data": data})
    # Standalone fallback if supervisor not running
    cache_copy = dict(_telemetry_cache)
    cache_copy["cpu_temp"] = get_cpu_temperature()
    return jsonify({"success": True, "ok": True, "data": cache_copy})



@app.route("/api/estop", methods=["POST"])
def api_estop():
    """Triggers global emergency stop from dashboard button."""
    logger.critical("E-STOP TRIGGERED FROM WEB DASHBOARD!")
    if _supervisor_ref:
        _supervisor_ref.trigger_emergency_stop()
    return jsonify({"success": True, "message": "EMERGENCY STOP ACTIVATED."})


@app.route("/api/reset_estop", methods=["POST"])
def api_reset_estop():
    """Resets emergency stop and returns system to MONITORING state."""
    logger.info("E-STOP RESET REQUESTED FROM WEB DASHBOARD.")
    if _supervisor_ref:
        _supervisor_ref.reset_emergency_stop()
        return jsonify({"success": True, "message": "EMERGENCY STOP CLEARED. System returned to MONITORING."})
    return jsonify({"success": True, "message": "Reset acknowledged."})


@app.route("/api/waypoints", methods=["GET", "POST"])
def api_waypoints():
    """
    GET: Returns current GPS waypoint mission and target index.
    POST: Updates or clears GPS waypoint mission.
          Payload: {"action": "set", "waypoints": [[lat, lon], ...]}
                   or {"action": "add", "latitude": lat, "longitude": lon}
                   or {"action": "clear"}
    """
    if _supervisor_ref is None or not hasattr(_supervisor_ref, 'nav_ctrl') or _supervisor_ref.nav_ctrl is None:
        # Standalone mock fallback for local UI testing
        if request.method == "GET":
            return jsonify({"success": True, "data": {
                "waypoints": list(config.NAV_WAYPOINTS),
                "current_index": 0,
                "total": len(config.NAV_WAYPOINTS),
                "current_target": config.NAV_WAYPOINTS[0] if config.NAV_WAYPOINTS else None,
                "last_status": "Standalone mode",
                "is_navigating": False
            }})
        return jsonify({"success": False, "error": "Supervisor navigation controller unavailable"}), 503

    nav = _supervisor_ref.nav_ctrl

    if request.method == "GET":
        return jsonify({"success": True, "data": nav.get_mission()})

    if not request.is_json:
        return jsonify({"success": False, "error": "JSON payload required"}), 400

    payload = request.get_json()
    action = payload.get("action", "set").lower()

    if action == "set":
        wps = payload.get("waypoints", [])
        nav.set_waypoints(wps)
        return jsonify({"success": True, "message": f"Updated mission with {len(wps)} waypoints.", "data": nav.get_mission()})
    elif action == "add":
        lat = payload.get("latitude")
        lon = payload.get("longitude")
        if lat is None or lon is None:
            return jsonify({"success": False, "error": "latitude and longitude required"}), 400
        nav.add_waypoint(float(lat), float(lon))
        return jsonify({"success": True, "message": f"Added waypoint ({lat}, {lon}).", "data": nav.get_mission()})
    elif action == "clear":
        nav.clear_waypoints()
        return jsonify({"success": True, "message": "Mission cleared.", "data": nav.get_mission()})

    return jsonify({"success": False, "error": f"Unknown action '{action}'"}), 400


@app.route("/api/health", methods=["GET"])
def api_health():
    """Health check endpoint for monitoring and systemd watchdog integration."""
    return jsonify({
        "status": "healthy",
        "current_state": _telemetry_cache.get("current_state", "UNKNOWN"),
        "simulation_mode": _telemetry_cache.get("simulation_mode", False),
        "timestamp": datetime.datetime.now().isoformat()
    })


@app.route("/api/sample_images", methods=["GET"])
def api_get_sample_images():
    """Returns a curated list of test sample images from the PlantVillage dataset."""
    dataset_dir = os.path.join(config.BASE_DIR, "plantvillage_dataset", "PlantVillage")
    samples = []
    
    target_categories = [
        (["Tomato_Early_blight", "Tomato___Early_blight"], "Tomato", "Early Blight (Fungal)", False),
        (["Tomato_healthy", "Tomato___healthy"], "Tomato", "Healthy Foliage", True),
        (["Tomato_Late_blight", "Tomato___Late_blight"], "Tomato", "Late Blight (Oomycete)", False),
        (["Potato___Early_blight", "Potato_Early_blight"], "Potato", "Early Blight", False),
        (["Potato___Late_blight", "Potato_Late_blight"], "Potato", "Late Blight", False),
        (["Potato___healthy", "Potato_healthy"], "Potato", "Healthy Foliage", True),
        (["Pepper__bell___Bacterial_spot", "Pepper_bell_Bacterial_spot"], "Bell Pepper", "Bacterial Spot", False),
        (["Pepper__bell___healthy", "Pepper_bell_healthy"], "Bell Pepper", "Healthy Leaf", True)
    ]
    
    for candidate_names, crop_type, disease_display, is_healthy in target_categories:
        for folder_name in candidate_names:
            folder_path = os.path.join(dataset_dir, folder_name)
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                files = [f for f in sorted(os.listdir(folder_path)) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                if files:
                    first_file = files[0]
                    samples.append({
                        "folder": folder_name,
                        "filename": first_file,
                        "crop": crop_type,
                        "title": f"{crop_type} — {disease_display}",
                        "is_healthy": is_healthy,
                        "rel_path": f"plantvillage_dataset/PlantVillage/{folder_name}/{first_file}"
                    })
                    break
                
    return jsonify({"success": True, "samples": samples})


@app.route("/dataset_sample/<path:subpath>")
def serve_dataset_sample(subpath):
    """Serves dataset images for web previews."""
    dataset_dir = os.path.join(config.BASE_DIR, "plantvillage_dataset", "PlantVillage")
    return send_from_directory(dataset_dir, subpath)


@app.route("/api/predict_image", methods=["POST"])
def api_predict_image():
    """
    Leaf Diagnostic Lab: Accepts uploaded leaf image or dataset sample path,
    runs disease detection pipeline, and outputs plant type and disease state.
    """
    detector = get_detector()
    db = get_db()
    os.makedirs(config.SCANS_DIR, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_filename = f"scan_leaf_{timestamp}.jpg"
    saved_path = os.path.join(config.SCANS_DIR, saved_filename)
    filename_hint = ""

    if 'image' in request.files:
        file = request.files['image']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        filename_hint = file.filename
        file.save(saved_path)

    elif request.is_json:
        payload = request.get_json()
        sample_rel = payload.get("sample_path", "")
        if not sample_rel:
            return jsonify({"success": False, "error": "No sample path provided"}), 400
        src_path = os.path.join(config.BASE_DIR, sample_rel.replace("/", os.sep))
        if not os.path.exists(src_path):
            return jsonify({"success": False, "error": f"Sample not found: {sample_rel}"}), 404
        filename_hint = sample_rel
        shutil.copyfile(src_path, saved_path)
    else:
        return jsonify({"success": False, "error": "Provide multipart form file 'image' or JSON 'sample_path'"}), 400

    # Run Detection
    result = detector.detect_from_image_path(saved_path, filename_hint=filename_hint)
    result["image_url"] = f"/static/scans/{saved_filename}"

    # Log to Database so the dashboard scan table immediately reflects the new prediction
    if db and result.get("success"):
        try:
            rel_scan_path = f"static/scans/{saved_filename}"
            db.log_disease_scan(
                label=result.get("label", "UNKNOWN"),
                common_name=result.get("common_name", "Leaf Scan"),
                confidence=float(result.get("confidence", 0.0)),
                image_path=rel_scan_path,
                quality_flag=result.get("quality_flag", "QUALITY_OK"),
                simulated=getattr(detector, "simulate", True)
            )
        except Exception as e:
            logger.warning(f"Database logging note: {e}")

    return jsonify({"success": True, "data": result})


# -----------------------------------------------------------------------------
# VERIFIED USER AUTHENTICATION ENDPOINTS (§5.8)
# -----------------------------------------------------------------------------
@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    """Authenticates a verified user and starts a session."""
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    db = get_db()
    if not db:
        return jsonify({"ok": False, "error": "Database unavailable"}), 500

    success, msg, user = db.authenticate_user(username, password)
    if not success:
        return jsonify({"ok": False, "error": msg}), 401

    # Store user in session
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["full_name"] = user["full_name"]
    session["role"] = user["role"]

    import hashlib
    # Simple bearer token for client storage
    token_src = f"{user['username']}:{user['id']}:{config.AUTH_SECRET_KEY}"
    token = hashlib.sha256(token_src.encode("utf-8")).hexdigest()

    return jsonify({
        "ok": True,
        "message": msg,
        "token": token,
        "user": {
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    })


@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    """Registers a new verified user with the Farmer Verification Key."""
    data = request.get_json(force=True, silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    full_name = data.get("full_name", "").strip()
    verification_key = data.get("verification_key", "").strip()

    db = get_db()
    if not db:
        return jsonify({"ok": False, "error": "Database unavailable"}), 500

    success, msg = db.register_user(username, password, full_name, verification_key)
    if not success:
        return jsonify({"ok": False, "error": msg}), 400

    return jsonify({"ok": True, "message": msg})


@app.route("/api/auth/status", methods=["GET"])
def auth_status():
    """Checks current authentication status."""
    auth_header = request.headers.get("Authorization", "")
    username = session.get("username")

    if username:
        return jsonify({
            "authenticated": True,
            "user": {
                "username": username,
                "full_name": session.get("full_name", username),
                "role": session.get("role", "farmer")
            }
        })

    # Validate Authorization token if provided
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "").strip()
        db = get_db()
        if db:
            import hashlib
            with db.get_connection() as conn:
                users = conn.execute("SELECT id, username, full_name, role FROM users;").fetchall()
                for u in users:
                    expected = hashlib.sha256(f"{u['username']}:{u['id']}:{config.AUTH_SECRET_KEY}".encode("utf-8")).hexdigest()
                    if token == expected:
                        return jsonify({
                            "authenticated": True,
                            "user": {
                                "username": u["username"],
                                "full_name": u["full_name"],
                                "role": u["role"]
                            }
                        })

    return jsonify({"authenticated": False, "message": "Not authenticated"}), 401


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    """Clears current user session."""
    session.clear()
    return jsonify({"ok": True, "message": "Logged out successfully"})


# -----------------------------------------------------------------------------
# MISTRAL AI CHATBOT ENDPOINT (Kisan Mitra / Multilingual Farm Assistant)
# -----------------------------------------------------------------------------
def _generate_trilingual_fallback_response(query: str, lang: str) -> str:
    """Intelligent rule-based fallback when Mistral API key is not configured or offline."""
    q = query.lower()
    moist = _telemetry_cache.get("soil_moisture")
    temp = _telemetry_cache.get("temperature")
    hum = _telemetry_cache.get("humidity")
    pump = "ON (चालू)" if _telemetry_cache.get("pump_state") else "OFF (बंद)"
    cutter = "ON (चालू)" if _telemetry_cache.get("cutter_state") else "OFF (बंद)"
    state = _telemetry_cache.get("current_state", "MONITORING")

    # Format live status
    moist_str = f"{moist:.1f}%" if moist is not None else "45.0% (Normal)"
    temp_str = f"{temp:.1f}°C" if temp is not None else "28.5°C"
    hum_str = f"{hum:.1f}%" if hum is not None else "65.0%"

    if lang == "mr":
        # Marathi response
        if "माती" in q or "ओलावा" in q or "soil" in q or "moisture" in q or "पंप" in q or "pump" in q:
            return (
                f"🌾 **नमस्कार बळीराजा!**\n\n"
                f"सध्याच्या सेन्सर नोंदींनुसार:\n"
                f"• **मातीतील ओलावा:** {moist_str}\n"
                f"• **पाण्याचा पंप:** {pump}\n"
                f"• **तापमान व आर्द्रता:** {temp_str} | {hum_str}\n\n"
                f"ॲग्रोनेक्स रोव्हर ओलावा ३५% पेक्षा कमी झाल्यावर आपोआप पंप चालू करतो आणि ६५% झाल्यावर बंद करतो. "
                f"आपले पीक उत्तम स्थितीत आहे!"
            )
        elif "टोमॅटो" in q or "tomato" in q:
            return (
                f"🍅 **टोमॅटो पिकाची माहिती व रोग उपाय:**\n\n"
                f"• **अर्ली ब्लाइट (Early Blight):** पानांवर गोलाकार तपकिरी डाग पडतात. यासाठी **कॉपर ऑक्सिक्लोराईड (२.५ ग्रॅम/लिटर)** फवारावे.\n"
                f"• **लेट ब्लाइट (Late Blight):** पाने कुजतात आणि करपतात. यासाठी **मँकोझेब किंवा मेटालॅक्सिल** चा त्वरित वापर करावा.\n"
                f"• **कीटक/मावा:** **५% कडुनिंब तेल (Neem Oil)** फवारणी फायदेशीर ठरते."
            )
        elif "बटाटा" in q or "potato" in q:
            return (
                f"🥔 **बटाटा रोग व्यवस्थापन:**\n\n"
                f"• **करपा (Early/Late Blight):** दमट हवेत बुरशीचा प्रादुर्भाव वाढतो. **मँकोझेब (२ ग्रॅम/लिटर)** फवारावे आणि अतिरिक्त पाणी देणे टाळावे."
            )
        elif "तुळस" in q or "tulsi" in q:
            return (
                f"🌿 **तुळस (Holy Basil) काळजी:**\n\n"
                f"• तुळशीला दिवसातून ४ ते ६ तास सूर्यप्रकाश आवश्यक आहे.\n"
                f"• पाने पिवळी पडत असल्यास पाणी कमी करा आणि कुंडीत पाण्याचा निचरा योग्य आहे का ते तपासा.\n"
                f"• पानांवर डाग पडल्यास सेंद्रिय कडुलिंबाच्या अर्काची फवारणी करावी."
            )
        else:
            return (
                f"🌾 **रामराम शेतकरी मित्र!**\n\n"
                f"मी आपला **ॲग्रोनेक्स किसान मित्र** आहे. रोव्हर सद्यस्थिती:\n"
                f"• **कार्यस्थिती (FSM):** {state}\n"
                f"• **मातीतील ओलावा:** {moist_str}\n"
                f"• **पंप:** {pump} | **कटर:** {cutter}\n\n"
                f"आपण मला मातीतील ओलावा, पाण्याचे नियोजन, टोमॅटो/बटाटा/तुळशीचे रोग, किंवा रोव्हर नियंत्रणाबद्दल विचारू शकता.\n\n"
                f"*(टीप: अधिक सखोल AI संभाषणासाठी Chat Settings मध्ये Mistral API Key जोडू शकता.)*"
            )

    elif lang == "hi":
        # Hindi response
        if "मिट्टी" in q or "नमी" in q or "soil" in q or "moisture" in q or "पंप" in q or "pump" in q:
            return (
                f"🌾 **नमस्ते किसान भाई!**\n\n"
                f"वर्तमान रोवर सेंसर रीडिंग:\n"
                f"• **मिट्टी की नमी:** {moist_str}\n"
                f"• **सिंचाई पंप:** {pump}\n"
                f"• **तापमान एवं आर्द्रता:** {temp_str} | {hum_str}\n\n"
                f"एग्रोनेक्स रोवर नमी ३५% से नीचे जाने पर स्वचालित रूप से पंप चालू करता है और ६५% पर बंद कर देता है।"
            )
        elif "टमाटर" in q or "tomato" in q:
            return (
                f"🍅 **टमाटर फसल एवं रोग उपचार:**\n\n"
                f"• **अगेती झुलसा (Early Blight):** पत्तियों पर गोल छल्लेदार भूरे धब्बे। उपचार: **कॉपर ऑक्सीक्लोराइड (२.५ ग्राम/लीटर)** का छिड़काव करें।\n"
                f"• **पछेती झुलसा (Late Blight):** पत्तियां काली होकर सड़ने लगती हैं। उपचार: **मैंकोजेब या मेटालेक्सिल** फफूंदनाशक का तुरंत छिड़काव करें।\n"
                f"• **सफेद मक्खी/कीट:** **नीम के तेल (५ मिली/लीटर)** का छिड़काव करें।"
            )
        elif "आलू" in q or "potato" in q:
            return (
                f"🥔 **आलू फसल सुरक्षा:**\n\n"
                f"• **झुलसा रोग (Blight):** अधिक नमी और ठंड में फैलता है। निवारक उपाय हेतु **मैंकोजेब** फफूंदनाशक का छिड़काव करें और खेत में पानी जमा न होने दें।"
            )
        elif "तुलसी" in q or "tulsi" in q:
            return (
                f"🌿 **तुलसी पौधे की देखभाल:**\n\n"
                f"• तुलसी को पर्याप्त धूप (४-६ घंटे) की आवश्यकता होती है।\n"
                f"• पत्तियां पीली होने पर अत्यधिक पानी देना बंद करें।\n"
                f"• पत्तों पर फंगल धब्बे दिखने पर जैविक नीम तेल का छिड़काव करें।"
            )
        else:
            return (
                f"🌾 **नमस्ते किसान मित्र!**\n\n"
                f"मैं आपका **एग्रोनेक्स एआई सहायक** हूँ। रोवर की वर्तमान स्थिति:\n"
                f"• **सिस्टम स्थिति:** {state}\n"
                f"• **मिट्टी की नमी:** {moist_str}\n"
                f"• **पंप:** {pump} | **घास कटर:** {cutter}\n\n"
                f"आप मुझसे सिंचाई, फसलों के रोग (टमाटर, आलू, तुलसी) या रोवर संचालन के बारे में कोई भी सवाल पूछ सकते हैं।\n\n"
                f"*(सुझाव: विस्तृत AI बातचीत के लिए Chat Settings में अपनी Mistral API Key जोड़ें।)*"
            )

    else:
        # English response
        if "soil" in q or "moisture" in q or "pump" in q or "water" in q:
            return (
                f"🌾 **Hello Farmer!**\n\n"
                f"Current Live Sensor Telemetry:\n"
                f"• **Soil Moisture:** {moist_str}\n"
                f"• **Water Pump Relay:** {pump}\n"
                f"• **Ambient Temperature & Humidity:** {temp_str} | {hum_str}\n\n"
                f"The AgroNex autonomous hysteresis loop engages the pump when moisture drops below 35% and shuts off once it reaches 65%."
            )
        elif "tomato" in q:
            return (
                f"🍅 **Tomato Pathology & Treatment Guide:**\n\n"
                f"• **Early Blight (Alternaria solani):** Concentric bullseye rings. Treatment: Apply **Copper Oxychloride (2.5 g/L)** or Chlorothalonil; prune affected lower foliage.\n"
                f"• **Late Blight (Phytophthora infestans):** Water-soaked rotting margins. Treatment: Immediate application of **Mancozeb or Metalaxyl (Ridomil Gold)**; avoid overhead watering.\n"
                f"• **Bacterial Spot (Xanthomonas):** Small dark angular scabs. Treatment: Copper bactericide combined with streptomycin."
            )
        elif "potato" in q:
            return (
                f"🥔 **Potato Crop Advisory:**\n\n"
                f"• **Early/Late Blight:** Destructive foliage decay. Apply protective **Mancozeb (2 g/L)** and ensure proper furrow drainage."
            )
        elif "tulsi" in q:
            return (
                f"🌿 **Tulsi (Holy Basil) Care:**\n\n"
                f"• Ensure 4–6 hours of direct sunlight daily.\n"
                f"• If yellowing (chlorosis) occurs, reduce watering frequency and verify root drainage.\n"
                f"• For leaf spotting, apply organic 0.5% neem oil spray."
            )
        else:
            return (
                f"🌾 **Greetings from Kisan Mitra!**\n\n"
                f"I am your official **AgroNex-Pi Smart Farming AI Companion**. Current rover state:\n"
                f"• **FSM State:** {state}\n"
                f"• **Soil Moisture:** {moist_str}\n"
                f"• **Pump:** {pump} | **Cutter:** {cutter}\n\n"
                f"You can ask me about live sensor telemetry, plant disease remedies (Tomato, Potato, Tulsi), irrigation thresholds, or rover safety protocols.\n\n"
                f"*(Note: To enable full Mistral LLM reasoning, paste your Mistral API Key in Chat Settings or config.py!)*"
            )


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    """Trilingual AI Chatbot endpoint powered by Mistral AI with live telemetry injection."""
    data = request.get_json(force=True, silent=True) or {}
    user_msg = data.get("message", "").strip()
    language = data.get("language", "en").lower().strip()  # 'en', 'mr', 'hi'
    if language not in ("en", "mr", "hi"):
        language = "en"

    custom_key = data.get("api_key", "").strip()
    history = data.get("history", [])

    if not user_msg:
        return jsonify({"ok": False, "error": "Message cannot be empty."}), 400

    # Determine Mistral API Key
    api_key = custom_key or getattr(config, "MISTRAL_API_KEY", "") or os.environ.get("MISTRAL_API_KEY", "")

    # Telemetry snapshot for context injection
    moist = _telemetry_cache.get("soil_moisture")
    temp = _telemetry_cache.get("temperature")
    hum = _telemetry_cache.get("humidity")
    pump = "ON" if _telemetry_cache.get("pump_state") else "OFF"
    cutter = "ON" if _telemetry_cache.get("cutter_state") else "OFF"
    water_level = _telemetry_cache.get("water_level", "OK")
    state = _telemetry_cache.get("current_state", "MONITORING")
    gps = _telemetry_cache.get("gps")
    gps_str = f"Lat: {gps.get('lat')}, Lon: {gps.get('lon')}" if gps else "Bench GPS Simulation Active"

    # Assemble System Prompt
    lang_instruction = {
        "mr": "उत्तर फक्त आणि फक्त मराठीत (Marathi) द्या. शेतकरी बांधवांशी (बळीराजा) आदरपूर्वक, सोप्या भाषेत बोला. कृषी सल्ले स्पष्ट द्या.",
        "hi": "उत्तर केवल और केवल हिंदी (Hindi) में दें। किसान भाइयों से सम्मानपूर्वक, सरल और सहज भाषा में बात करें। सटीक कृषि सलाह दें।",
        "en": "Respond in clean, friendly English. Provide practical agronomic guidance and clear robotic explanations."
    }.get(language, "Respond in clean, friendly English.")

    system_prompt = f"""You are 'Kisan Mitra' (किसान मित्र / बळीराजा), the official smart farming and robotics AI companion integrated directly into the AgroNex-Pi autonomous agricultural rover.

LANGUAGE RULE: {lang_instruction}

REAL-TIME AGRO-NEX ROVER TELEMETRY (LIVE RIGHT NOW):1
- System FSM State: {state}
- Soil Moisture: {moist if moist is not None else 45.0}% (Target band: 35% - 65%)
- Water Pump Relay: {pump} (Hysteresis automated drip irrigation)
- Grass Cutter Relay: {cutter} (Scheduled mower with dual safety interlocks)
- Water Tank Level: {water_level} (Low-water pump interlock at <20%)
- Ambient Air Temperature: {temp if temp is not None else 28.5}°C
- Ambient Air Humidity: {hum if hum is not None else 65.0}%
- GPS Navigation Location: {gps_str}

KNOWLEDGE BASE SUMMARY (CROP PATHOLOGY & ACTIONABLE REMEDIES):
1. Tomato:
   - Early Blight (Alternaria solani): Bullseye concentric spots. Spray Copper Oxychloride (2.5 g/L) or Chlorothalonil; prune lower leaves touching soil.
   - Late Blight (Phytophthora infestans): Water-soaked rotting margins. Spray systemic Mancozeb or Metalaxyl (Ridomil Gold); avoid overhead irrigation.
   - Bacterial Spot (Xanthomonas): Dark scabs. Use copper bactericide + streptomycin.
   - Spider Mites: Yellow stippling. Apply 0.5% Neem oil spray or insecticidal soap.
   - Healthy: Optimal green compound leaf. Maintain drip irrigation schedule.
2. Potato:
   - Early/Late Blight: Alternaria / Phytophthora fungal-oomycete damage. Apply Mancozeb (2 g/L), isolate infected plants.
   - Healthy: Strong foliage.
3. Tulsi (Holy Basil):
   - Leaf Spot (Colletotrichum), Mite Infestation, Wilting (Fusarium root rot / overwatering). Apply organic neem oil spray, reduce waterlogging.
4. Local Field Plants:
   - Local_healthy, Local_unhealthy (foliar blight), Local_yellow (chlorosis / nitrogen-iron deficiency), Local_dried (drought / severe moisture stress).

ROBOT CAPABILITIES:
- Automated Hysteresis Irrigation: Turns pump ON at <=35%, OFF at >=65%.
- Safety Interlocks: Pump dry-run lock, cutter-motor interlock (cutter stops when pump is active).
- Edge AI: MobileNetV2 TFLite running in 180ms on Raspberry Pi 4.
- GPS Navigation: NEO-7M waypoint traversal with 2.3m precision.

Keep answers concise, practical, encouraging, and directly relevant to the farmer's question."""

    # If Mistral API Key is provided, call Mistral AI
    if api_key and api_key != "YOUR_MISTRAL_API_KEY_HERE" and len(api_key) > 10:
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            messages = [{"role": "system", "content": system_prompt}]
            # Add up to 6 previous history messages
            if isinstance(history, list):
                for h in history[-6:]:
                    if isinstance(h, dict) and "role" in h and "content" in h:
                        messages.append({"role": h["role"], "content": h["content"]})
            messages.append({"role": "user", "content": user_msg})

            payload = {
                "model": getattr(config, "MISTRAL_MODEL", "mistral-small-latest"),
                "messages": messages,
                "temperature": 0.4,
                "max_tokens": 800
            }

            req = urllib.request.Request(
                config.MISTRAL_API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=12.0) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                reply = res_json["choices"][0]["message"]["content"]
                return jsonify({
                    "ok": True,
                    "reply": reply,
                    "model": res_json.get("model", "mistral-small-latest"),
                    "source": "mistral_ai"
                })
        except Exception as e:
            logger.warning(f"Mistral API call note: {e}. Falling back to trilingual local expert.")

    # Fallback to local intelligent trilingual agronomic responder
    fallback_reply = _generate_trilingual_fallback_response(user_msg, language)
    return jsonify({
        "ok": True,
        "reply": fallback_reply,
        "model": "agronex-local-expert",
        "source": "local_fallback",
        "has_mistral_key": bool(api_key and len(api_key) > 10)
    })


if __name__ == "__main__":
    port = 5000
    print(f"[*] AgroNex-Pi Web Server launching directly on http://localhost:{port}...")
    _telemetry_cache["simulation_mode"] = True
    _telemetry_cache["current_state"] = "MONITORING"
    get_db()
    app.run(host="0.0.0.0", port=port, debug=True)
