"""
AgroNex-Pi: AWS Lambda Function  (v2 — Farm Dashboard edition)
API Gateway routes -> Lambda -> S3

Routes handled:
  POST /telemetry     — Pi pushes sensor data -> stored in S3 state.json
  GET  /state         — Dashboard polls current Pi state
  POST /scan          — Pi pushes a completed disease scan (image + result) -> S3
  GET  /scans          — Dashboard fetches last N scan results
  POST /command        — Dashboard sends a command (pump_on, cutter_on, e_stop, ...)
  GET  /command         — Pi polls for a pending command (one-shot)
  POST /scan_request   — NEW. Dashboard (e.g. a phone) uploads a leaf photo (base64) that
                          the Pi should analyze with its on-device model. Queued in S3.
  GET  /scan_request    — NEW. Pi polls for a pending scan request (one-shot, like /command).
                          After running inference the Pi posts the result via the existing
                          POST /scan route, so it shows up in GET /scans automatically.
  GET  /diseases        — NEW. Static agronomic disease knowledge base, grouped by plant,
                          for the dashboard's Disease Library tab.
  GET  /blogs           — NEW. Aggregates a coup.le of agriculture RSS feeds for the
                          Farmer Blogs tab. Falls back to an empty list on network failure
                          (never a 500) — the dashboard has its own static fallback list too.

Deploy:
  1. S3 bucket: agronex-pi-data (already exists)
  2. Lambda (Python 3.11, 512 MB, 30s timeout) — paste this file as lambda_function.py
  3. IAM policy: S3 read/write scoped to your bucket
  4. API Gateway HTTP API — integrate ALL routes (including the 3 new ones) to this Lambda
  5. Leave the Lambda OUTSIDE any VPC (or attach a NAT gateway) so /blogs can reach the
     public internet for RSS. If it can't, /blogs just returns an empty list — harmless.

Environment variables:
  S3_BUCKET     -> your-bucket-name   (default: agronex-pi-data)
"""

import json
import os
import re
import time
import base64
import urllib.request
import xml.etree.ElementTree as ET
import boto3
from datetime import datetime, timezone

REGION = os.environ.get("AWS_REGION", "ap-south-1")
BUCKET = os.environ.get("S3_BUCKET", "agronex-pi-data-nikhil")
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "agronex_users")
S3 = boto3.client("s3")
DYNAMODB = boto3.resource("dynamodb", region_name=REGION)

STATE_KEY = "state.json"
SCANS_PREFIX = "scans/"
SCANS_LOG_KEY = "scans_log.json"
COMMAND_KEY = "pending_command.json"
COMMANDS_LOG_KEY = "commands_log.json"
SCAN_REQUEST_KEY = "pending_scan_request.json"
USERS_KEY = "users.json"
USER_ACTIVITY_CSV_KEY = "user_activity_log.csv"
MAX_SCANS = 20
MAX_COMMANDS = 50

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,x-api-key,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
}

# ---------------------------------------------------------------------------
# Disease knowledge base for the Disease Library tab.
# Mirrors disease_db.py on the Pi — kept as a plain dict here since the
# Lambda deployment package doesn't share a filesystem with the Pi.
# ---------------------------------------------------------------------------
DISEASE_LIBRARY = {
    "Tomato": [
        {"disease": "Healthy", "healthy": True, "cause": "N/A — optimal physiological vigor.",
         "symptoms": "Vibrant uniform green foliage, no lesions.",
         "treatment": "Maintain regular drip irrigation and balanced N-P-K feeding."},
        {"disease": "Early Blight (Alternaria solani)", "healthy": False,
         "cause": "Fungal pathogen, favored by warm temps and prolonged leaf wetness.",
         "symptoms": "Concentric target-spot rings on older leaves with yellow halos.",
         "treatment": "Copper fungicide or chlorothalonil; remove lower leaves touching soil; drip-irrigate."},
        {"disease": "Late Blight (Phytophthora infestans)", "healthy": False,
         "cause": "Oomycete pathogen, spreads fast in cool humid weather.",
         "symptoms": "Dark water-soaked lesions with white fuzzy sporulation underneath.",
         "treatment": "Mancozeb or systemic metalaxyl; destroy infected foliage; avoid overhead watering."},
        {"disease": "Bacterial Spot", "healthy": False,
         "cause": "Xanthomonas spp., spread by splashing water and contaminated tools.",
         "symptoms": "Small dark water-soaked spots drying with yellow borders.",
         "treatment": "Copper hydroxide + mancozeb; sanitize tools; avoid overhead sprinklers."},
        {"disease": "Leaf Mold (Passalora fulva)", "healthy": False,
         "cause": "Fungus thriving in greenhouse humidity above 85%.",
         "symptoms": "Pale spots on top, olive velvety patches underneath.",
         "treatment": "Ventilate to reduce humidity; remove affected foliage; bio-fungicide spray."},
        {"disease": "Septoria Leaf Spot", "healthy": False,
         "cause": "Septoria lycopersici overwintering in crop debris.",
         "symptoms": "Small circular grey-centered spots with dark margins.",
         "treatment": "Rotate crops 2-3 years; chlorothalonil or copper spray; mulch the base."},
        {"disease": "Yellow Leaf Curl Virus (TYLCV)", "healthy": False,
         "cause": "Begomovirus spread exclusively by whitefly.",
         "symptoms": "Upward leaf curl, yellowing, stunted growth.",
         "treatment": "Yellow sticky traps + imidacloprid to control whitefly; remove infected plants."},
    ],
    "Potato": [
        {"disease": "Healthy", "healthy": True, "cause": "N/A — optimal vigor.",
         "symptoms": "Uniform deep green leaves, no wilt.",
         "treatment": "Standard field management, balanced N fertilization, monitor soil moisture."},
        {"disease": "Early Blight (Alternaria solani)", "healthy": False,
         "cause": "Survives in crop debris and volunteer tubers.",
         "symptoms": "Dark angular spots with concentric rings on lower leaves.",
         "treatment": "Preventative mancozeb/azoxystrobin; rotate with non-solanaceous crops."},
        {"disease": "Late Blight (Phytophthora infestans)", "healthy": False,
         "cause": "Highly destructive under cool, damp conditions.",
         "symptoms": "Irregular dark, water-soaked lesions expanding from leaf edges.",
         "treatment": "Systemic fungicide (metalaxyl/cymoxanil); destroy infected tubers."},
    ],
    "Bell Pepper": [
        {"disease": "Healthy", "healthy": True, "cause": "N/A — optimal vigor.",
         "symptoms": "Smooth glossy deep-green foliage.",
         "treatment": "Regular watering and organic compost mulching."},
        {"disease": "Bacterial Spot", "healthy": False,
         "cause": "Xanthomonas spp., enters through stomata/wounds.",
         "symptoms": "Raised blister spots darkening to greasy black.",
         "treatment": "Copper bactericide + mancozeb; sanitize seed stock; rotate hosts."},
    ],
    "Corn": [
        {"disease": "Healthy", "healthy": True, "cause": "N/A",
         "symptoms": "Uniform green blades, no lesions.",
         "treatment": "Maintain nitrogen schedule and adequate spacing."},
        {"disease": "Common Rust (Puccinia sorghi)", "healthy": False,
         "cause": "Windborne fungal spores, cool moist conditions.",
         "symptoms": "Small reddish-brown pustules on both leaf surfaces.",
         "treatment": "Resistant hybrids; foliar fungicide if severe before tasseling."},
        {"disease": "Gray Leaf Spot", "healthy": False,
         "cause": "Cercospora zeae-maydis, favored by humidity and residue.",
         "symptoms": "Rectangular tan-to-gray lesions parallel to veins.",
         "treatment": "Crop rotation, residue management, triazole/strobilurin fungicide."},
    ],
    "Grape": [
        {"disease": "Healthy", "healthy": True, "cause": "N/A",
         "symptoms": "Firm green leaves, no discoloration.",
         "treatment": "Standard canopy management and irrigation."},
        {"disease": "Black Rot", "healthy": False,
         "cause": "Guignardia bidwellii, warm humid weather.",
         "symptoms": "Tan circular lesions with dark borders and black fruiting bodies.",
         "treatment": "Remove mummified berries; mancozeb spray from bud break; improve canopy airflow."},
    ],
    "Apple": [
        {"disease": "Healthy", "healthy": True, "cause": "N/A",
         "symptoms": "Glossy uniform green leaves.",
         "treatment": "Routine pruning and balanced fertilization."},
        {"disease": "Apple Scab", "healthy": False,
         "cause": "Venturia inaequalis, cool wet spring weather.",
         "symptoms": "Olive-green to black velvety spots on leaves and fruit.",
         "treatment": "Captan or myclobutanil sprays timed to bud break; rake and destroy fallen leaves."},
    ],
    "Strawberry": [
        {"disease": "Healthy", "healthy": True, "cause": "N/A",
         "symptoms": "Bright green trifoliate leaves.",
         "treatment": "Balanced fertigation and mulching."},
        {"disease": "Leaf Scorch", "healthy": False,
         "cause": "Diplocarpon earlianum, humid conditions.",
         "symptoms": "Small purple blotches merging into scorched patches.",
         "treatment": "Remove infected leaves after harvest; captan/myclobutanil spray; avoid overhead watering."},
    ],
}

BLOG_FEEDS = [
    ("Krishi Jagran", "https://krishijagran.com/rss/agriculture.xml"),
    ("FAO News", "https://www.fao.org/rss/en/news.xml"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def respond(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {**CORS, "Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }


def s3_get_json(key: str, default=None):
    try:
        obj = S3.get_object(Bucket=BUCKET, Key=key)
        return json.loads(obj["Body"].read())
    except Exception:
        return default


def s3_put_json(key: str, data):
    S3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(data, default=str),
        ContentType="application/json",
    )


def get_dynamo_table():
    """Returns DynamoDB table resource if table exists and accessible, else None."""
    try:
        table = DYNAMODB.Table(DYNAMODB_TABLE_NAME)
        _ = table.table_status
        return table
    except Exception:
        return None


def s3_append_activity_csv(event_type, username, full_name, role, status, client_ip=""):
    """Appends login/signup/admin audit records to user_activity_log.csv in S3 (Excel compatible)."""
    try:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        header = "Timestamp,Username,Full Name,Role,Event,Status,IP Address\n"
        row = f'"{now_str}","{username}","{full_name}","{role}","{event_type}","{status}","{client_ip}"\n'

        existing = ""
        try:
            obj = S3.get_object(Bucket=BUCKET, Key=USER_ACTIVITY_CSV_KEY)
            existing = obj["Body"].read().decode("utf-8")
        except Exception:
            existing = header

        if not existing.startswith("Timestamp"):
            existing = header + existing

        new_content = existing + row
        S3.put_object(
            Bucket=BUCKET,
            Key=USER_ACTIVITY_CSV_KEY,
            Body=new_content.encode("utf-8"),
            ContentType="text/csv",
        )
    except Exception as e:
        print(f"[CSV LOG WARNING] {e}")


def db_get_all_users():
    """Fetches users from DynamoDB if active, otherwise syncs with S3 users.json."""
    users = {}
    table = get_dynamo_table()
    if table:
        try:
            resp = table.scan()
            for item in resp.get("Items", []):
                u = item.get("username")
                if u:
                    users[u] = item
            if users:
                s3_put_json(USERS_KEY, users)
                return users
        except Exception as e:
            print(f"[DYNAMODB SCAN FALLBACK] {e}")

    # Fallback to S3 users.json
    s3_users = s3_get_json(USERS_KEY, default={
        "admin": {
            "username": "admin",
            "password": "agronex2026",
            "name": "AgroNex Farm Admin",
            "role": "admin",
            "status": "active",
            "registered_at": "2026-01-01T00:00:00Z",
            "last_login": None,
            "login_count": 0
        }
    })
    for u, data in s3_users.items():
        if "username" not in data:
            data["username"] = u
        if "status" not in data:
            data["status"] = "active"
        if "role" not in data:
            data["role"] = "farmer" if u != "admin" else "admin"
        if "login_count" not in data:
            data["login_count"] = 0
    return s3_users


def db_save_user(user_dict):
    """Saves user to DynamoDB and syncs to S3 users.json."""
    username = user_dict.get("username")
    if not username:
        return
    # 1. DynamoDB
    table = get_dynamo_table()
    if table:
        try:
            table.put_item(Item=user_dict)
        except Exception as e:
            print(f"[DYNAMODB PUT FALLBACK] {e}")

    # 2. S3 mirror
    all_users = db_get_all_users()
    all_users[username] = user_dict
    s3_put_json(USERS_KEY, all_users)


def db_delete_user(username):
    """Deletes user from DynamoDB and S3."""
    table = get_dynamo_table()
    if table:
        try:
            table.delete_item(Key={"username": username})
        except Exception as e:
            print(f"[DYNAMODB DELETE FALLBACK] {e}")

    all_users = db_get_all_users()
    if username in all_users:
        del all_users[username]
        s3_put_json(USERS_KEY, all_users)


def fetch_rss(name, url, limit=4, timeout=4):
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
                items.append({"source": name, "title": title, "url": link, "snippet": snippet})
    except Exception:
        pass
    return items


def parse_body(event):
    """Safely extracts and parses JSON body from API Gateway event (raw or base64)."""
    body_raw = event.get("body", "") or ""
    if event.get("isBase64Encoded"):
        try:
            body_raw = base64.b64decode(body_raw).decode("utf-8")
        except Exception:
            pass
    if isinstance(body_raw, str) and body_raw.strip():
        try:
            return json.loads(body_raw)
        except Exception:
            return {}
    if isinstance(body_raw, dict):
        return body_raw
    return {}


# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------
def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
    path = event.get("requestContext", {}).get("http", {}).get("path", "/")
    client_ip = event.get("requestContext", {}).get("http", {}).get("sourceIp", "unknown")

    if method == "OPTIONS":
        return respond(200, {"ok": True})

    body = parse_body(event)

    # POST /telemetry
    if path.endswith("/telemetry") and method == "POST":
        telemetry = body.get("telemetry", body)
        # Store UTC ISO8601 with explicit Z suffix — JS new Date("...Z") correctly converts to local IST
        telemetry["_received_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        telemetry["_device_id"] = body.get("device_id", "unknown")

        # Preserve and merge existing state so partial sensor updates don't wipe out other metrics
        existing_state = s3_get_json(STATE_KEY, default={})
        merged = dict(existing_state)
        merged.update(telemetry)

        if "camera_snapshot_url" in existing_state and "camera_snapshot_url" not in telemetry:
            merged["camera_snapshot_url"] = existing_state["camera_snapshot_url"]
        if "camera_snapshot_time" in existing_state and "camera_snapshot_time" not in telemetry:
            merged["camera_snapshot_time"] = existing_state["camera_snapshot_time"]

        s3_put_json(STATE_KEY, merged)
        return respond(200, {"ok": True, "stored": "state.json"})

    # GET /state
    if path.endswith("/state") and method == "GET":
        state = s3_get_json(STATE_KEY, default={})
        # Inject a fresh _polled_at timestamp (UTC with Z) so dashboard "last seen" always refreshes
        state["_polled_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        # Ensure required fields always present so dashboard renders fully
        if "operation_mode" not in state:
            state["operation_mode"] = "AUTO"
        if "current_state" not in state:
            state["current_state"] = "MONITORING"
        return respond(200, {"ok": True, "data": state})


    # POST /scan  (Pi posts a completed inference result)
    if path.endswith("/scan") and method == "POST":
        result = body.get("result", {})
        img_b64 = body.get("image_b64", "")
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        img_key = f"{SCANS_PREFIX}scan_{ts}.jpg"

        img_url = ""
        if img_b64:
            img_bytes = base64.b64decode(img_b64)
            S3.put_object(
                Bucket=BUCKET,
                Key=img_key,
                Body=img_bytes,
                ContentType="image/jpeg",
                CacheControl="public, max-age=31536000"
            )
            # Permanent direct public S3 URL (never expires)
            img_url = f"https://{BUCKET}.s3.{REGION}.amazonaws.com/{img_key}"

        log = s3_get_json(SCANS_LOG_KEY, default=[])
        log.insert(0, {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "image_url": img_url,
            **result,
        })
        log = log[:MAX_SCANS]
        s3_put_json(SCANS_LOG_KEY, log)
        return respond(200, {"ok": True, "image_url": img_url})

    # GET /scans
    if path.endswith("/scans") and method == "GET":
        log = s3_get_json(SCANS_LOG_KEY, default=[])
        # Clean any expired presigned query params so images load directly and permanently
        for item in log:
            url = item.get("image_url", "")
            if url and ("?" in url or "s3.amazonaws.com" in url):
                m = re.search(r"(scans/[a-zA-Z0-9_\-\.]+)", url)
                if m:
                    item["image_url"] = f"https://{BUCKET}.s3.{REGION}.amazonaws.com/{m.group(1)}"
        return respond(200, {"ok": True, "scans": log, "count": len(log)})

    # POST /command
    if path.endswith("/command") and method == "POST":
        cmd = body.get("command", "").strip()
        if not cmd:
            return respond(400, {"ok": False, "error": "command field required"})

        now_iso = datetime.now(timezone.utc).isoformat()
        print(f"[AGRONEX COMMAND] Button pressed: '{cmd}' | Timestamp: {now_iso}")

        # 1. Store one-shot pending command for Pi to execute
        s3_put_json(COMMAND_KEY, {"command": cmd, "issued_at": now_iso})

        # 2. Append to permanent command audit log in S3 (retains last 50 commands)
        cmd_log = s3_get_json(COMMANDS_LOG_KEY, default=[])
        cmd_log.insert(0, {
            "command": cmd,
            "issued_at": now_iso,
            "source": body.get("source", "dashboard")
        })
        cmd_log = cmd_log[:MAX_COMMANDS]
        s3_put_json(COMMANDS_LOG_KEY, cmd_log)

        return respond(200, {"ok": True, "command": cmd, "issued_at": now_iso})

    # GET /commands  (Audit trail of last 50 button presses)
    if path.endswith("/commands") and method == "GET":
        cmd_log = s3_get_json(COMMANDS_LOG_KEY, default=[])
        return respond(200, {"ok": True, "commands": cmd_log, "count": len(cmd_log)})

    # GET /command  (Pi polls, one-shot)
    if path.endswith("/command") and method == "GET":
        pending = s3_get_json(COMMAND_KEY, default={})
        cmd = pending.get("command", "")
        if cmd:
            s3_put_json(COMMAND_KEY, {})
        return respond(200, {"ok": True, "command": cmd})

    # POST /scan_request  (NEW — dashboard/phone queues a photo for the Pi to analyze)
    if path.endswith("/scan_request") and method == "POST":
        img_b64 = body.get("image_b64", "")
        if not img_b64:
            return respond(400, {"ok": False, "error": "image_b64 field required"})
        s3_put_json(SCAN_REQUEST_KEY, {
            "image_b64": img_b64,
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "device_id": body.get("device_id", "dashboard"),
        })
        return respond(200, {"ok": True, "queued": True})

    # GET /scan_request  (NEW — Pi polls, one-shot; clears after delivery)
    if path.endswith("/scan_request") and method == "GET":
        pending = s3_get_json(SCAN_REQUEST_KEY, default={})
        if pending.get("image_b64"):
            s3_put_json(SCAN_REQUEST_KEY, {})
            return respond(200, {"ok": True, "pending": True, "image_b64": pending["image_b64"]})
        return respond(200, {"ok": True, "pending": False})

    # POST /snapshot  (Pi uploads latest camera JPEG snapshot)
    if path.endswith("/snapshot") and method == "POST":
        img_b64 = body.get("image_b64", "")
        if not img_b64:
            return respond(400, {"ok": False, "error": "image_b64 field required"})
        try:
            img_bytes = base64.b64decode(img_b64)
            snapshot_key = "camera_latest.jpg"
            S3.put_object(
                Bucket=BUCKET,
                Key=snapshot_key,
                Body=img_bytes,
                ContentType="image/jpeg",
                CacheControl="no-cache, no-store, must-revalidate"
            )
            try:
                snapshot_url = S3.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": BUCKET, "Key": snapshot_key},
                    ExpiresIn=604800,
                )
            except Exception:
                snapshot_url = f"https://{BUCKET}.s3.amazonaws.com/{snapshot_key}"

            # Also update state.json with latest snapshot URL and timestamp
            try:
                state = s3_get_json(STATE_KEY, default={})
                state["camera_snapshot_url"] = snapshot_url
                state["camera_snapshot_time"] = datetime.now(timezone.utc).isoformat()
                s3_put_json(STATE_KEY, state)
            except Exception:
                pass

            return respond(200, {"ok": True, "snapshot_url": snapshot_url})
        except Exception as e:
            return respond(500, {"ok": False, "error": f"Snapshot save error: {str(e)}"})

    # GET /snapshot  (Dashboard / client gets current camera snapshot URL)
    if path.endswith("/snapshot") and method == "GET":
        try:
            snapshot_key = "camera_latest.jpg"
            url = S3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": BUCKET, "Key": snapshot_key},
                ExpiresIn=604800,
            )
            return respond(200, {"ok": True, "snapshot_url": url})
        except Exception as e:
            return respond(200, {"ok": True, "snapshot_url": f"https://{BUCKET}.s3.amazonaws.com/camera_latest.jpg"})

    # GET /diseases  (NEW)
    if path.endswith("/diseases") and method == "GET":
        return respond(200, {"ok": True, "data": DISEASE_LIBRARY})

    # GET /blogs  (NEW)
    if path.endswith("/blogs") and method == "GET":
        items = []
        for name, url in BLOG_FEEDS:
            items.extend(fetch_rss(name, url))
        return respond(200, {"ok": True, "data": items})

    # =========================================================================
    # POST /chat or /api/chat  (Trilingual AI Chatbot with Live Telemetry)
    # =========================================================================
    if (path.endswith("/chat") or path.endswith("/api/chat")) and method == "POST":
        try:
            body = parse_body(event)
            user_msg = body.get("message", "").strip()
            language = body.get("language", "en").lower().strip()
            custom_key = body.get("api_key", "").strip()
            history = body.get("history", [])

            if not user_msg:
                return respond(400, {"ok": False, "error": "Message required"})

            # Load live state from S3
            state = s3_get_json(STATE_KEY, default={})
            moist = state.get("soil_moisture", 45.0)
            temp = state.get("temperature", 28.5)
            hum = state.get("humidity", 65.0)
            pump = "ON" if state.get("pump_state") else "OFF"
            cutter = "ON" if state.get("cutter_state") else "OFF"
            fsm = state.get("current_state", "MONITORING")

            api_key = custom_key or os.environ.get("MISTRAL_API_KEY", "mstrl_MTvPBRlJLRVQnpnk61HDpurJoT7L9Deb_0Jt5kr")
            model = os.environ.get("MISTRAL_MODEL", "open-mistral-7b")

            lang_rules = {
                "mr": "उत्तर फक्त मराठीत (Marathi) द्या. शेतकरी बांधवांशी (बळीराजा) आदरपूर्वक, सोप्या भाषेत बोला.",
                "hi": "उत्तर केवल हिंदी (Hindi) में दें। किसान भाइयों से सम्मानपूर्वक, सरल भाषा में बात करें।",
                "en": "Respond in clean, friendly English with clear agricultural and robotics advice."
            }.get(language, "Respond in clean, friendly English.")

            system_prompt = f"""You are 'Kisan Mitra' (किसान मित्र / बळीराजा), the official smart agricultural AI assistant for AgroNex-Pi rover.
LANGUAGE RULE: {lang_rules}
LIVE ROVER SENSORS (FROM AWS S3):
- Soil Moisture: {moist}% (Optimal band: 35% - 65%)
- Water Pump Relay: {pump}
- Grass Cutter Relay: {cutter}
- Air Temperature: {temp}°C | Humidity: {hum}%
- FSM State: {fsm}
CROPS: Tomato, Potato, Bell Pepper, Tulsi. Provide practical agronomic remedies for diseases (Early/Late Blight: Copper Oxychloride or Mancozeb; Pests: Neem oil)."""

            # Call Mistral AI
            if api_key and len(api_key) > 10:
                try:
                    msgs = [{"role": "system", "content": system_prompt}]
                    if isinstance(history, list):
                        for h in history[-4:]:
                            if isinstance(h, dict) and "role" in h and "content" in h:
                                msgs.append({"role": h["role"], "content": h["content"]})
                    msgs.append({"role": "user", "content": user_msg})

                    payload = {
                        "model": model,
                        "messages": msgs,
                        "temperature": 0.4,
                        "max_tokens": 500
                    }
                    req = urllib.request.Request(
                        "https://api.mistral.ai/v1/chat/completions",
                        data=json.dumps(payload).encode("utf-8"),
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        method="POST"
                    )
                    with urllib.request.urlopen(req, timeout=10.0) as resp:
                        res_json = json.loads(resp.read().decode("utf-8"))
                        reply = res_json["choices"][0]["message"]["content"]
                        return respond(200, {"ok": True, "reply": reply, "source": "mistral_ai"})
                except Exception:
                    pass

            # Trilingual Fallback Response
            if language == "mr":
                fb = f"🌾 **नमस्कार बळीराजा!**\n\nसध्याच्या नोंदी: मातीतील ओलावा: {moist}%, पंप: {pump}, तापमान: {temp}°C. रोव्हर उत्तम रितीने कार्यरत आहे!"
            elif language == "hi":
                fb = f"🌾 **नमस्ते किसान भाई!**\n\nवर्तमान स्थिति: मिट्टी की नमी: {moist}%, पंप: {pump}, तापमान: {temp}°C. एग्रोनेक्स रोवर सक्रिय है।"
            else:
                fb = f"🌾 **Hello Farmer!**\n\nLive Telemetry: Soil Moisture: {moist}%, Pump: {pump}, Temp: {temp}°C. AgroNex rover is operational."
            return respond(200, {"ok": True, "reply": fb, "source": "local_fallback"})
        except Exception as e:
            return respond(500, {"ok": False, "error": str(e)})

    # =========================================================================
    # POST /auth/login or /api/auth/login  (Verified Login with DynamoDB/S3)
    # =========================================================================
    if (path.endswith("/auth/login") or path.endswith("/api/auth/login")) and method == "POST":
        try:
            body = parse_body(event)
            username = body.get("username", "").strip().lower()
            password = body.get("password", "").strip()

            users = db_get_all_users()
            user = users.get(username)

            if not user or user.get("password") != password:
                print(f"[AGRONEX LOGIN FAILED] Invalid attempt for username '{username}'.")
                s3_append_activity_csv("LOGIN_FAILED", username, username, "unknown", "REJECTED", client_ip)
                return respond(401, {"ok": False, "error": "Invalid username or password"})

            # Check if account is blocked by admin
            if user.get("status") == "blocked":
                print(f"[AGRONEX LOGIN BLOCKED] Blocked user '{username}' attempted to sign in.")
                s3_append_activity_csv("LOGIN_BLOCKED", username, user.get("name", username), user.get("role", "farmer"), "BLOCKED", client_ip)
                return respond(403, {"ok": False, "error": "This account has been BLOCKED by the administrator. Please contact your farm admin."})

            # Update login telemetry
            now_iso = datetime.now(timezone.utc).isoformat()
            user["last_login"] = now_iso
            user["login_count"] = int(user.get("login_count", 0)) + 1
            user["last_ip"] = client_ip
            db_save_user(user)

            s3_append_activity_csv("LOGIN", username, user.get("name", username), user.get("role", "farmer"), "SUCCESS", client_ip)
            print(f"[AGRONEX LOGIN SUCCESS] User '{username}' logged in successfully (login count: {user['login_count']}).")

            return respond(200, {
                "ok": True,
                "token": f"token_{username}_{int(time.time())}",
                "user": {
                    "username": username,
                    "full_name": user.get("name", username),
                    "role": user.get("role", "farmer"),
                    "status": user.get("status", "active"),
                    "last_login": now_iso,
                    "login_count": user["login_count"]
                }
            })
        except Exception as e:
            return respond(500, {"ok": False, "error": str(e)})

    # =========================================================================
    # POST /auth/register or /api/auth/register  (Farmer Verification Sign Up)
    # =========================================================================
    if (path.endswith("/auth/register") or path.endswith("/api/auth/register")) and method == "POST":
        try:
            body = parse_body(event)
            username = body.get("username", "").strip().lower()
            password = body.get("password", "").strip()
            name = body.get("full_name", "").strip()
            verify_key = body.get("verification_key", "").strip()

            if verify_key != os.environ.get("AGRONEX_VERIFY_KEY", "AGRONEX_FARM_2026"):
                print(f"[AGRONEX SIGNUP REJECTED] Invalid verification key used for username '{username}'.")
                return respond(400, {"ok": False, "error": "Invalid Farmer Verification Key"})

            users = db_get_all_users()
            if username in users:
                return respond(400, {"ok": False, "error": "Username is already registered"})

            now_iso = datetime.now(timezone.utc).isoformat()
            new_user = {
                "username": username,
                "password": password,
                "name": name or username,
                "role": "farmer",
                "status": "active",
                "registered_at": now_iso,
                "last_login": None,
                "login_count": 0,
                "last_ip": client_ip
            }
            db_save_user(new_user)
            s3_append_activity_csv("SIGNUP", username, name or username, "farmer", "SUCCESS", client_ip)
            print(f"[AGRONEX SIGNUP SUCCESS] New user registered: '{username}' (Name: '{name or username}') | Total users: {len(users) + 1}")

            return respond(200, {"ok": True, "message": "User registered successfully", "user": new_user})
        except Exception as e:
            return respond(500, {"ok": False, "error": str(e)})

    # =========================================================================
    # ADMIN USER MANAGEMENT ROUTES (DynamoDB & S3 Authority)
    # =========================================================================
    # GET /admin/users or /api/admin/users  (Retrieve all users)
    if (path.endswith("/admin/users") or path.endswith("/api/admin/users")) and method == "GET":
        try:
            users = db_get_all_users()
            user_list = []
            for u, data in users.items():
                item = dict(data)
                # Ensure default values
                item["username"] = u
                item["name"] = item.get("name", u)
                item["role"] = item.get("role", "farmer" if u != "admin" else "admin")
                item["status"] = item.get("status", "active")
                item["login_count"] = item.get("login_count", 0)
                user_list.append(item)
            # Admin first, then sorted by username
            user_list.sort(key=lambda x: (x.get("role") != "admin", x.get("username", "")))
            return respond(200, {"ok": True, "users": user_list, "count": len(user_list)})
        except Exception as e:
            return respond(500, {"ok": False, "error": str(e)})

    # POST /admin/user/status or /api/admin/user/status  (Block / Unblock user)
    if (path.endswith("/admin/user/status") or path.endswith("/api/admin/user/status")) and method == "POST":
        try:
            body = parse_body(event)
            username = body.get("username", "").strip().lower()
            new_status = body.get("status", "active").strip().lower()

            if not username:
                return respond(400, {"ok": False, "error": "Username required"})
            if username == "admin":
                return respond(400, {"ok": False, "error": "Master administrator account cannot be blocked"})
            if new_status not in ["active", "blocked"]:
                return respond(400, {"ok": False, "error": "Status must be 'active' or 'blocked'"})

            users = db_get_all_users()
            if username not in users:
                return respond(404, {"ok": False, "error": "User not found"})

            users[username]["status"] = new_status
            db_save_user(users[username])
            s3_append_activity_csv(f"ADMIN_{new_status.upper()}", username, users[username].get("name", username), users[username].get("role", "farmer"), new_status.upper(), client_ip)
            print(f"[AGRONEX ADMIN] User '{username}' status changed to '{new_status}'")

            return respond(200, {"ok": True, "message": f"User '{username}' is now {new_status}", "user": users[username]})
        except Exception as e:
            return respond(500, {"ok": False, "error": str(e)})

    # POST /admin/user/update or /api/admin/user/update  (Update user details)
    if (path.endswith("/admin/user/update") or path.endswith("/api/admin/user/update")) and method == "POST":
        try:
            body = parse_body(event)
            username = body.get("username", "").strip().lower()
            name = body.get("name", "").strip()
            role = body.get("role", "").strip()
            new_password = body.get("password", "").strip()

            if not username:
                return respond(400, {"ok": False, "error": "Username required"})

            users = db_get_all_users()
            if username not in users:
                return respond(404, {"ok": False, "error": "User not found"})

            if name:
                users[username]["name"] = name
            if role and username != "admin":
                users[username]["role"] = role
            if new_password:
                users[username]["password"] = new_password

            db_save_user(users[username])
            s3_append_activity_csv("ADMIN_UPDATE", username, users[username].get("name", username), users[username].get("role", "farmer"), "UPDATED", client_ip)
            print(f"[AGRONEX ADMIN] Updated user '{username}' details.")

            return respond(200, {"ok": True, "message": f"User '{username}' updated successfully", "user": users[username]})
        except Exception as e:
            return respond(500, {"ok": False, "error": str(e)})

    # POST /admin/user/delete or /api/admin/user/delete  (Delete user)
    if (path.endswith("/admin/user/delete") or path.endswith("/api/admin/user/delete")) and method == "POST":
        try:
            body = parse_body(event)
            username = body.get("username", "").strip().lower()

            if not username:
                return respond(400, {"ok": False, "error": "Username required"})
            if username == "admin":
                return respond(400, {"ok": False, "error": "Cannot delete master administrator account"})

            users = db_get_all_users()
            if username not in users:
                return respond(404, {"ok": False, "error": "User not found"})

            db_delete_user(username)
            s3_append_activity_csv("ADMIN_DELETE", username, users[username].get("name", username), users[username].get("role", "farmer"), "DELETED", client_ip)
            print(f"[AGRONEX ADMIN] Deleted user '{username}' from DynamoDB and S3.")

            return respond(200, {"ok": True, "message": f"User '{username}' deleted successfully"})
        except Exception as e:
            return respond(500, {"ok": False, "error": str(e)})

    # GET /admin/export_users_csv or /api/admin/export_users_csv  (Export activity / excel sheet)
    if (path.endswith("/admin/export_users_csv") or path.endswith("/api/admin/export_users_csv")) and method == "GET":
        try:
            try:
                obj = S3.get_object(Bucket=BUCKET, Key=USER_ACTIVITY_CSV_KEY)
                csv_content = obj["Body"].read().decode("utf-8")
            except Exception:
                # Generate fresh CSV if log file does not exist yet
                users = db_get_all_users()
                lines = ["Timestamp,Username,Full Name,Role,Event,Status,IP Address"]
                for u, d in users.items():
                    ts = d.get("registered_at", "N/A")
                    lines.append(f'"{ts}","{u}","{d.get("name", u)}","{d.get("role", "farmer")}","ACTIVE_USER","{d.get("status", "active")}","{d.get("last_ip", "")}"')
                csv_content = "\n".join(lines)

            return {
                "statusCode": 200,
                "headers": {
                    **CORS,
                    "Content-Type": "text/csv; charset=utf-8",
                    "Content-Disposition": 'attachment; filename="agronex_user_activity.csv"'
                },
                "body": csv_content
            }
        except Exception as e:
            return respond(500, {"ok": False, "error": str(e)})

    # GET /auth/status or /api/auth/status
    if (path.endswith("/auth/status") or path.endswith("/api/auth/status")) and method == "GET":
        auth_h = event.get("headers", {}).get("authorization", "")
        if auth_h:
            return respond(200, {"authenticated": True, "user": {"username": "farmer", "full_name": "Verified Farmer", "role": "farmer", "status": "active"}})
        return respond(200, {"authenticated": True, "user": {"username": "admin", "full_name": "AgroNex Farm Admin", "role": "admin", "status": "active"}})

    # POST /auth/logout or /api/auth/logout
    if (path.endswith("/auth/logout") or path.endswith("/api/auth/logout")) and method == "POST":
        return respond(200, {"ok": True, "message": "Logged out successfully"})

    return respond(404, {"ok": False, "error": f"Unknown route {method} {path}"})

