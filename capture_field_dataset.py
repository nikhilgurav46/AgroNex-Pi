#!/usr/bin/env python3
"""
AgroNex-Pi: Live Camera Dataset Studio (§9.2)

Provides a real-time LIVE CAMERA FEED for visual judgment and photo capture:
  1. Web Studio (Default): Open http://<pi-ip>:8080 on your laptop or phone.
     - Live 30 FPS camera stream with focus/sharpness & lighting gauges.
     - Press [SPACEBAR] or click 'Snap Photo' to capture high-res training photos.
     - Automatic classification into class folders under ./field_dataset/<class_name>/
     - Instant thumbnail preview & photo counter per class.
  2. OpenCV GUI Mode (--gui): For Raspberry Pi with HDMI monitor / VNC.
     - Shows live window with HUD overlay (press SPACE to snap, N for next class).

Usage:
  python3 capture_field_dataset.py            # Starts Live Web Studio on port 8080
  python3 capture_field_dataset.py --port 8080 # Custom port
  python3 capture_field_dataset.py --gui       # Enable local desktop window too
"""

import os
import sys
import time
import datetime
import logging
import threading
import argparse
import socket
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("DatasetStudio")

try:
    import cv2
except ImportError:
    logger.critical("FATAL: 'opencv-python' (cv2) is required. Run: pip install opencv-python")
    sys.exit(1)

try:
    from flask import Flask, Response, request, jsonify, render_template_string
except ImportError:
    logger.critical("FATAL: 'Flask' is required. Run: pip install Flask")
    sys.exit(1)

# Default target classes for AgroNex-Pi
DEFAULT_CLASSES = [
    "Tulsi___Healthy",
    "Tulsi___Infected",
    "Tulsi___Infested",
    "Tulsi___Wilting",
    "background_not_a_leaf",
    "Tomato___healthy",
    "Tomato___Early_blight",
]

OUTPUT_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "field_dataset")
os.makedirs(OUTPUT_BASE, exist_ok=True)


def get_local_ip():
    """Detects the Raspberry Pi's local network IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class CameraStreamer:
    """Threaded camera capture for smooth 30 FPS streaming and low-latency snaps."""

    def __init__(self):
        self.backend = None
        self.cam = None
        self.running = False
        self.lock = threading.Lock()
        self.raw_frame = None
        self.display_frame = None
        self.jpeg_bytes = None
        self.metrics = {"sharpness": 0.0, "brightness": 0.0, "is_sharp": False, "is_lit": False}

        self._init_camera()

    def _init_camera(self):
        # 1. Try Picamera2 (CSI Camera)
        try:
            from picamera2 import Picamera2
            picam2 = Picamera2()
            cfg = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"})
            picam2.configure(cfg)
            picam2.start()
            time.sleep(1.0)
            self.backend = "picamera2"
            self.cam = picam2
            logger.info("Camera: Picamera2 (CSI Camera) initialized.")
            return
        except Exception as e:
            logger.warning(f"Picamera2 init bypassed/failed: {e}")

        # 2. Try OpenCV VideoCapture (USB / V4L2 Webcam)
        for dev_idx in [0, 1, 2, 4]:
            try:
                cap = cv2.VideoCapture(dev_idx)
                if cap.isOpened():
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    ret, test_frame = cap.read()
                    if ret and test_frame is not None and test_frame.size > 0:
                        self.backend = "cv2"
                        self.cam = cap
                        logger.info(f"Camera: OpenCV VideoCapture({dev_idx}) initialized.")
                        return
                    cap.release()
            except Exception:
                pass

        logger.warning("No hardware camera found. Running in color test pattern mode.")
        self.backend = "mock"

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        while self.running:
            bgr = None
            if self.backend == "picamera2":
                try:
                    rgb = self.cam.capture_array("main")
                    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                except Exception as e:
                    logger.debug(f"Picam capture error: {e}")
            elif self.backend == "cv2":
                try:
                    ret, frame = self.cam.read()
                    if ret and frame is not None:
                        bgr = frame
                except Exception as e:
                    logger.debug(f"OpenCV capture error: {e}")
            elif self.backend == "mock":
                # Simulated camera frame for bench development
                bgr = np.zeros((480, 640, 3), dtype=np.uint8)
                bgr[:] = (35, 75, 45)
                cv2.putText(bgr, "MOCK CAMERA FEED", (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

            if bgr is not None:
                # Compute image metrics for user feedback
                gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                brightness = float(np.mean(gray))
                sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())

                # Generate clean preview with HUD guidelines
                preview = bgr.copy()
                h, w = preview.shape[:2]

                # Center target box (focus region of interest)
                box_w, box_h = int(w * 0.65), int(h * 0.70)
                x1, y1 = (w - box_w) // 2, (h - box_h) // 2
                x2, y2 = x1 + box_w, y1 + box_h
                box_color = (0, 230, 100) if sharpness >= 15.0 else (0, 140, 255)
                cv2.rectangle(preview, (x1, y1), (x2, y2), box_color, 2)
                cv2.putText(preview, "PLACE LEAF HERE", (x1 + 10, y1 + 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

                # Quality Badges
                sharp_txt = f"Sharpness: {sharpness:.1f} {'[CRISP]' if sharpness >= 15 else '[BLURRY - TURN LENS]'}"
                sharp_col = (0, 255, 0) if sharpness >= 15 else (0, 0, 255)
                cv2.putText(preview, sharp_txt, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, sharp_col, 2)

                bright_txt = f"Brightness: {brightness:.0f} {'[GOOD]' if 30 <= brightness <= 225 else '[POOR LIGHT]'}"
                bright_col = (0, 255, 0) if 30 <= brightness <= 225 else (0, 165, 255)
                cv2.putText(preview, bright_txt, (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, bright_col, 2)

                # Encode to JPEG for MJPEG stream
                ret, jpeg = cv2.imencode('.jpg', preview, [cv2.IMWRITE_JPEG_QUALITY, 80])

                with self.lock:
                    self.raw_frame = bgr.copy()
                    self.display_frame = preview
                    if ret:
                        self.jpeg_bytes = jpeg.tobytes()
                    self.metrics = {
                        "sharpness": round(sharpness, 1),
                        "brightness": round(brightness, 1),
                        "is_sharp": sharpness >= 15.0,
                        "is_lit": 30 <= brightness <= 225
                    }

            time.sleep(0.033)  # ~30 FPS

    def get_latest_jpeg(self):
        with self.lock:
            return self.jpeg_bytes

    def snap_photo(self, class_name: str):
        with self.lock:
            if self.raw_frame is None:
                raise RuntimeError("No camera frame available to capture.")
            frame_to_save = self.raw_frame.copy()
            metrics = dict(self.metrics)

        class_dir = os.path.join(OUTPUT_BASE, class_name)
        os.makedirs(class_dir, exist_ok=True)

        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
        filename = f"{class_name}_{ts}.jpg"
        filepath = os.path.join(class_dir, filename)

        # Save pristine raw frame without any overlay text
        cv2.imwrite(filepath, frame_to_save, [cv2.IMWRITE_JPEG_QUALITY, 95])
        count = len([f for f in os.listdir(class_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

        logger.info(f"📸 Captured #{count} for '{class_name}': {filename} (Sharpness: {metrics['sharpness']}, Brightness: {metrics['brightness']})")
        return {
            "filename": filename,
            "filepath": filepath,
            "count": count,
            "metrics": metrics
        }

    def close(self):
        self.running = False
        if self.backend == "picamera2" and self.cam:
            try:
                self.cam.stop()
                self.cam.close()
            except Exception:
                pass
        elif self.backend == "cv2" and self.cam:
            try:
                self.cam.release()
            except Exception:
                pass


# ── Web Application for Live Studio ──────────────────────────────────────────
app = Flask(__name__)
camera: CameraStreamer = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AgroNex-Pi: Live Camera Dataset Studio</title>
  <style>
    :root {
      --bg: #0f172a;
      --card: #1e293b;
      --border: #334155;
      --emerald: #10b981;
      --emerald-dark: #059669;
      --rose: #f43f5e;
      --amber: #f59e0b;
      --cyan: #06b6d4;
      --text: #f8fafc;
      --muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background-color: var(--bg); color: var(--text); padding: 18px; display: flex; flex-direction: column; align-items: center; min-height: 100vh; }
    
    header { text-align: center; margin-bottom: 16px; }
    header h1 { font-size: 24px; font-weight: 700; color: #fff; display: flex; align-items: center; justify-content: center; gap: 8px; }
    header p { color: var(--muted); font-size: 13px; margin-top: 4px; }
    
    .main-container { display: flex; flex-direction: column; lg-flex-direction: row; gap: 20px; width: 100%; max-width: 1080px; }
    @media (min-width: 900px) { .main-container { flex-direction: row; align-items: flex-start; } }

    .video-card { flex: 1.3; background: var(--card); border: 1px solid var(--border); border-radius: 14px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5); }
    .video-viewport { position: relative; width: 100%; background: #000; aspect-ratio: 4/3; display: flex; align-items: center; justify-content: center; overflow: hidden; }
    .video-viewport img { width: 100%; height: 100%; object-fit: contain; }
    
    .hud-bar { padding: 12px 16px; background: #131c2e; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
    .badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; }
    .badge-good { background: rgba(16, 185, 129, 0.2); color: var(--emerald); border: 1px solid var(--emerald); }
    .badge-warn { background: rgba(245, 158, 11, 0.2); color: var(--amber); border: 1px solid var(--amber); }
    .badge-bad { background: rgba(244, 63, 94, 0.2); color: var(--rose); border: 1px solid var(--rose); }

    .control-card { flex: 1; background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 20px; display: flex; flex-direction: column; gap: 16px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5); }
    
    label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); }
    select, input { width: 100%; background: #0f172a; border: 1px solid var(--border); color: #fff; padding: 10px 12px; border-radius: 8px; font-size: 14px; outline: none; margin-top: 6px; }
    select:focus, input:focus { border-color: var(--emerald); }

    .btn { display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; padding: 14px; border: none; border-radius: 10px; font-size: 16px; font-weight: 700; cursor: pointer; transition: all 0.15s ease; user-select: none; }
    .btn-snap { background: var(--emerald); color: #022c22; box-shadow: 0 4px 14px 0 rgba(16,185,129,0.39); }
    .btn-snap:hover { background: #34d399; transform: translateY(-1px); }
    .btn-snap:active { transform: translateY(1px); }

    .btn-burst { background: #334155; color: #fff; margin-top: 8px; font-size: 13px; padding: 10px; }
    .btn-burst:hover { background: #475569; }

    .stats-box { background: #131c2e; border: 1px solid var(--border); border-radius: 10px; padding: 12px; display: flex; justify-content: space-around; text-align: center; }
    .stat-item h3 { font-size: 20px; font-weight: 700; color: var(--emerald); }
    .stat-item p { font-size: 11px; color: var(--muted); text-transform: uppercase; margin-top: 2px; }

    .gallery-section { width: 100%; max-width: 1080px; margin-top: 20px; }
    .gallery-title { font-size: 14px; font-weight: 600; color: var(--muted); margin-bottom: 10px; }
    .gallery-strip { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 8px; }
    .gallery-thumb { width: 130px; height: 98px; background: #000; border-radius: 8px; border: 1px solid var(--border); overflow: hidden; position: relative; flex-shrink: 0; }
    .gallery-thumb img { width: 100%; height: 100%; object-fit: cover; }
    .gallery-thumb .info { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.7); font-size: 9px; padding: 2px 4px; text-align: center; color: #fff; }

    .flash-overlay { position: fixed; inset: 0; background: rgba(255,255,255,0.7); pointer-events: none; opacity: 0; transition: opacity 0.1s ease-out; z-index: 999; }
    .toast { position: fixed; bottom: 20px; right: 20px; background: #1e293b; border: 1px solid var(--emerald); color: #fff; padding: 12px 18px; border-radius: 8px; box-shadow: 0 10px 20px rgba(0,0,0,0.5); transform: translateY(100px); transition: transform 0.2s ease; z-index: 1000; }
    .toast.show { transform: translateY(0); }
  </style>
</head>
<body>

  <div id="flash" class="flash-overlay"></div>
  <div id="toast" class="toast">Photo captured!</div>

  <header>
    <h1>🌱 AgroNex-Pi Live Camera Dataset Studio</h1>
    <p>Hold leaf 10-20 cm from camera &bull; Adjust lens focus ring until sharp &bull; Press <b>[SPACEBAR]</b> to click photo</p>
  </header>

  <div class="main-container">
    <!-- Camera Viewport Card -->
    <div class="video-card">
      <div class="video-viewport">
        <img id="liveFeed" src="/video_feed" alt="Live Camera Feed">
      </div>
      <div class="hud-bar">
        <div id="sharpnessBadge" class="badge badge-good">🔍 Checking Sharpness...</div>
        <div id="lightingBadge" class="badge badge-good">💡 Checking Lighting...</div>
      </div>
    </div>

    <!-- Controls Card -->
    <div class="control-card">
      <div>
        <label for="classSelect">Target Disease / Plant Class</label>
        <select id="classSelect" onchange="onClassChange()">
          {% for c in classes %}
            <option value="{{ c }}" {% if c == active_class %}selected{% endif %}>{{ c }}</option>
          {% endfor %}
          <option value="__NEW__">+ [Add New Custom Class]</option>
        </select>
        <input type="text" id="newClassInput" placeholder="Enter class name (e.g. Tulsi___Caterpillar)" style="display: none; margin-top: 8px;">
      </div>

      <div class="stats-box">
        <div class="stat-item">
          <h3 id="classCount">0</h3>
          <p>This Class</p>
        </div>
        <div class="stat-item">
          <h3 id="totalCount">0</h3>
          <p>Total Dataset</p>
        </div>
      </div>

      <div>
        <button id="snapBtn" class="btn btn-snap" onclick="triggerSnap()">
          📸 SNAP PHOTO [Spacebar]
        </button>
        <button id="burstBtn" class="btn btn-burst" onclick="toggleBurst()">
          ⚡ Auto-Burst Mode (Take 20 @ 1.5s)
        </button>
      </div>

      <div style="font-size: 11px; color: var(--muted); line-height: 1.4; border-top: 1px solid var(--border); padding-top: 12px;">
        <b>💡 Photography Pro-Tips:</b><br/>
        &bull; <b>Focus:</b> If badge says <i>[BLURRY]</i>, twist the small round lens ring on your OV5647 camera.<br/>
        &bull; <b>Angles:</b> Rotate and tilt the leaf between clicks.<br/>
        &bull; <b>Background:</b> Capture 25+ photos of pots/soil under <code>background_not_a_leaf</code> so the model doesn't hallucinate diseases on dirt!
      </div>
    </div>
  </div>

  <!-- Recent Gallery -->
  <div class="gallery-section">
    <div class="gallery-title">Recently Captured Photos (This Session)</div>
    <div class="gallery-strip" id="galleryStrip">
      <div style="color: var(--muted); font-size: 12px; padding: 20px;">No photos captured in this session yet. Press Spacebar to snap!</div>
    </div>
  </div>

  <script>
    let activeClass = document.getElementById('classSelect').value;
    let burstInterval = null;
    let burstRemaining = 0;

    function onClassChange() {
      const select = document.getElementById('classSelect');
      const input = document.getElementById('newClassInput');
      if (select.value === '__NEW__') {
        input.style.display = 'block';
        input.focus();
      } else {
        input.style.display = 'none';
        activeClass = select.value;
        fetchCounts();
      }
    }

    document.getElementById('newClassInput').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const val = e.target.value.trim().replace(/ /g, '_');
        if (val) {
          const opt = document.createElement('option');
          opt.value = val;
          opt.textContent = val;
          document.getElementById('classSelect').prepend(opt);
          document.getElementById('classSelect').value = val;
          activeClass = val;
          e.target.style.display = 'none';
          fetchCounts();
        }
      }
    });

    async function fetchCounts() {
      try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        document.getElementById('classCount').textContent = data.classes[activeClass] || 0;
        document.getElementById('totalCount').textContent = data.total;
        
        // Update HUD
        const metrics = data.metrics || {};
        const sharpBadge = document.getElementById('sharpnessBadge');
        if (metrics.sharpness >= 15.0) {
          sharpBadge.className = 'badge badge-good';
          sharpBadge.textContent = `🔍 Sharpness: ${metrics.sharpness} [CRISP & CLEAR]`;
        } else {
          sharpBadge.className = 'badge badge-bad';
          sharpBadge.textContent = `⚠️ Sharpness: ${metrics.sharpness} [BLURRY - TURN LENS]`;
        }

        const lightBadge = document.getElementById('lightingBadge');
        if (metrics.brightness >= 30 && metrics.brightness <= 225) {
          lightBadge.className = 'badge badge-good';
          lightBadge.textContent = `💡 Lighting: ${metrics.brightness} [GOOD LIGHT]`;
        } else {
          lightBadge.className = 'badge badge-warn';
          lightBadge.textContent = `⚠️ Lighting: ${metrics.brightness} [${metrics.brightness < 30 ? 'TOO DARK' : 'TOO BRIGHT'}]`;
        }
      } catch (e) {}
    }

    async function triggerSnap() {
      const btn = document.getElementById('snapBtn');
      btn.style.transform = 'scale(0.96)';
      setTimeout(() => btn.style.transform = '', 100);

      // Screen flash effect
      const flash = document.getElementById('flash');
      flash.style.opacity = '1';
      setTimeout(() => flash.style.opacity = '0', 80);

      try {
        const res = await fetch('/api/capture', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ class_name: activeClass })
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Saved #${data.count} to ${activeClass}`);
          document.getElementById('classCount').textContent = data.count;
          addThumb(data.thumb_url, data.filename, data.metrics.sharpness);
          fetchCounts();
        }
      } catch (e) {
        showToast('Capture error: ' + e);
      }
    }

    function addThumb(url, filename, sharpness) {
      const strip = document.getElementById('galleryStrip');
      if (strip.innerText.includes('No photos')) {
        strip.innerHTML = '';
      }
      const thumb = document.createElement('div');
      thumb.className = 'gallery-thumb';
      thumb.innerHTML = `
        <img src="${url}" alt="${filename}">
        <div class="info">S:${sharpness} &bull; Saved</div>
      `;
      strip.prepend(thumb);
    }

    function toggleBurst() {
      if (burstInterval) {
        clearInterval(burstInterval);
        burstInterval = null;
        document.getElementById('burstBtn').textContent = '⚡ Auto-Burst Mode (Take 20 @ 1.5s)';
        return;
      }

      burstRemaining = 20;
      document.getElementById('burstBtn').textContent = `⏹ STOP BURST (${burstRemaining} left)`;
      burstInterval = setInterval(() => {
        if (burstRemaining <= 0) {
          toggleBurst();
          return;
        }
        triggerSnap();
        burstRemaining--;
        document.getElementById('burstBtn').textContent = `⏹ STOP BURST (${burstRemaining} left)`;
      }, 1500);
    }

    function showToast(msg) {
      const toast = document.getElementById('toast');
      toast.textContent = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 1800);
    }

    // Spacebar capture listener
    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space' && e.target.tagName !== 'INPUT') {
        e.preventDefault();
        triggerSnap();
      }
    });

    setInterval(fetchCounts, 1200);
    fetchCounts();
  </script>
</body>
</html>
"""


@app.route('/')
def index():
    # Gather class list including already existing directories
    classes = list(DEFAULT_CLASSES)
    if os.path.isdir(OUTPUT_BASE):
        for folder in sorted(os.listdir(OUTPUT_BASE)):
            full = os.path.join(OUTPUT_BASE, folder)
            if os.path.isdir(full) and folder not in classes:
                classes.append(folder)
    return render_template_string(HTML_TEMPLATE, classes=classes, active_class=classes[0])


@app.route('/video_feed')
def video_feed():
    def gen():
        while True:
            jpeg = camera.get_latest_jpeg()
            if jpeg is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')
            time.sleep(0.035)

    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/capture', methods=['POST'])
def api_capture():
    data = request.get_json() or {}
    class_name = data.get('class_name', 'Tulsi___Healthy').strip().replace(' ', '_')
    if not class_name:
        class_name = 'Tulsi___Healthy'

    try:
        res = camera.snap_photo(class_name)
        thumb_url = f"/api/thumb/{class_name}/{res['filename']}"
        return jsonify({
            "success": True,
            "filename": res['filename'],
            "count": res['count'],
            "metrics": res['metrics'],
            "thumb_url": thumb_url
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/thumb/<class_name>/<filename>')
def api_thumb(class_name, filename):
    filepath = os.path.join(OUTPUT_BASE, class_name, filename)
    if os.path.isfile(filepath):
        with open(filepath, 'rb') as f:
            return Response(f.read(), mimetype='image/jpeg')
    return "Not Found", 404


@app.route('/api/stats')
def api_stats():
    classes_counts = {}
    total = 0
    if os.path.isdir(OUTPUT_BASE):
        for cls in sorted(os.listdir(OUTPUT_BASE)):
            d = os.path.join(OUTPUT_BASE, cls)
            if os.path.isdir(d):
                n = len([f for f in os.listdir(d) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                classes_counts[cls] = n
                total += n
    return jsonify({
        "classes": classes_counts,
        "total": total,
        "metrics": camera.metrics if camera else {}
    })


def run_gui_window(cam: CameraStreamer):
    """Optional OpenCV GUI window for desktop/HDMI monitors."""
    logger.info("Opening OpenCV GUI Window... (Press SPACE to snap, N for next class, Q to quit)")
    classes = list(DEFAULT_CLASSES)
    current_idx = 0

    while cam.running:
        with cam.lock:
            frame = cam.display_frame.copy() if cam.display_frame is not None else None

        if frame is not None:
            active_class = classes[current_idx]
            count = len([f for f in os.listdir(os.path.join(OUTPUT_BASE, active_class))
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))]) if os.path.isdir(os.path.join(OUTPUT_BASE, active_class)) else 0

            # Bottom banner
            cv2.rectangle(frame, (0, 440), (640, 480), (20, 20, 20), -1)
            cv2.putText(frame, f"CLASS: {active_class} ({count} saved) | [SPACE]=Snap [N]=Next [Q]=Quit",
                        (10, 465), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 200), 1)

            cv2.imshow("AgroNex Dataset Studio (GUI)", frame)
            key = cv2.waitKey(20) & 0xFF
            if key == ord(' '):
                cam.snap_photo(active_class)
            elif key == ord('n') or key == ord('N'):
                current_idx = (current_idx + 1) % len(classes)
                logger.info(f"Switched class to: {classes[current_idx]}")
            elif key == ord('q') or key == ord('Q') or key == 27:
                break
        else:
            time.sleep(0.05)

    cv2.destroyAllWindows()


def main():
    global camera

    parser = argparse.ArgumentParser(description="AgroNex-Pi: Live Camera Dataset Studio")
    parser.add_argument("--port", type=int, default=8080, help="Web server port (default: 8080)")
    parser.add_argument("--gui", action="store_true", help="Launch OpenCV desktop window alongside web studio")
    args = parser.parse_args()

    local_ip = get_local_ip()

    print("=" * 68)
    print("      🌱  AGRONEX-PI: LIVE CAMERA DATASET STUDIO  🌱")
    print("=" * 68)
    print(f"  Starting camera streamer (Picamera2 / USB fallback)...")

    camera = CameraStreamer()
    camera.start()

    print("\n  [✓] Live Camera Studio is READY!")
    print(f"  👉 Open in your Laptop or Phone browser:")
    print(f"       \033[92mhttp://{local_ip}:{args.port}\033[0m")
    print(f"       (or http://localhost:{args.port} if on the Pi)\n")
    print("  Controls:")
    print("    - Live 30 FPS video feed with real-time blur/sharpness check")
    print("    - Press [SPACEBAR] or click 'Snap Photo' to capture")
    print("    - Auto-burst mode for rapid multi-angle collection")
    print("=" * 68 + "\n")

    if args.gui:
        gui_thread = threading.Thread(target=run_gui_window, args=(camera,), daemon=True)
        gui_thread.start()

    try:
        # Run Flask server quietly without debug reloader
        app.run(host="0.0.0.0", port=args.port, debug=False, threaded=True)
    finally:
        camera.close()


if __name__ == "__main__":
    main()
