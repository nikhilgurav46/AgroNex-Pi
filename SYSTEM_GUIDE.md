# AgroNex-Pi: Complete Code Explanation, Dataset Setup & Execution Guide

This document provides a complete, step-by-step guide to the **AgroNex-Pi** codebase. It explains what every single file does, where the dataset is located, how to extract and train it, and how to verify and run the entire software stack in sequence.

---

## 1. Dataset Location & Extraction Instructions

### Dataset File Location
The pre-downloaded Kaggle PlantVillage dataset archive is located directly in your project root folder at:
```
plantdisease.zip (Size: ~689.5 MB)
Path: c:\Users\Nikhil\OneDrive\Desktop\Major project\plantdisease.zip
```

### Unzipping & Installation Command
To extract the dataset into the `./plantvillage_dataset` folder, run this Python command in your terminal:

```bash
python -c "import zipfile, os; os.makedirs('plantvillage_dataset', exist_ok=True); zipfile.ZipFile('plantdisease.zip').extractall('plantvillage_dataset'); print('Dataset extracted successfully!')"
```

Once extracted, the images will be organized in `./plantvillage_dataset/PlantVillage/` categorized by crop and disease folders (e.g. `Tomato___healthy`, `Potato___Early_blight`).

---

## 2. File-by-File Code Explanation (What Each Code File Does)

Below is a detailed breakdown of every code file in the AgroNex-Pi software stack:

### 2.1 Core Configuration & System Layer
- **`config.py`**: **Global System Configuration & Pin Map.** Stores all physical BCM pin numbers (Relays GPIO17/27, Sensors GPIO4, SPI GPIO8/9/10/11, dual BTS7960 PWM GPIO5/6/13/19, NEO-7M UART and HMC5883L I²C), thresholds, timings, confidence gate, and file paths.
- **`hardware.py`**: **Low-Level Hardware Drivers.** Wraps physical hardware communication:
  - `SoilSensor`: Reads MCP3008 ADC CH0 via `spidev` protected by a `threading.Lock()` to prevent bus contention.
  - `DHTSensor`: Reads DHT11/22 temperature and humidity with automatic 1-wire retry logic.
  - `Relay`: Controls active-LOW 5V relays for the water pump and cutter. Initializes output pins to `GPIO.HIGH` before setting mode to prevent boot-up pulses.
  - `Motors`: Controls 4WD chassis motor speeds and directions through two BTS7960 high-current H-bridges with PWM (1 kHz).
  - `GPSSensor` / `CompassSensor`: Reads NEO-7M NMEA fixes and HMC5883L heading for waypoint navigation.
  - `Camera`: Manages the OV5647 CSI camera through `picamera2` as a singleton (initialized ONCE at boot).
  - `Alerts`: Pulses piezo buzzer and alert LED during disease detections.
  - `emergency_stop()`: Immediately de-energizes all relays and grounds motor pins on failure.
- **`database.py`**: **SQLite Storage Manager.** Enables Write-Ahead Logging (WAL) mode for high concurrency. Uses autoincrement primary keys across `sensor_log`, `irrigation_events`, `disease_log`, and `system_events`.

### 2.2 Functional Subsystem Controllers
- **`irrigation.py`**: **Soil Sensing & Automated Irrigation.** Implements hysteresis control (`35%` turn ON, `65%` turn OFF). Incorporates probe drag mitigation (halts chassis motion while irrigating), 60-second pump safety shutoff on dry tank/leak, 120-second cooldown period, and implausible ADC rejection.
- **`cutter.py`**: **Grass Trimming Scheduler.** Automatically schedules periodic 30-second grass trimming runs. Halts chassis drive motors before starting the cutting motor to prevent high-current battery voltage sags.
- **`navigation.py`**: **Chassis Navigation Routine.** Uses NEO-7M GPS and HMC5883L compass heading to approach configured waypoints in short, stop-and-recheck bursts. No obstacle sensors are fitted.

### 2.3 AI Inference & Knowledge Base
- **`disease_db.py`**: **Plant Disease Knowledge Base.** Maps PlantVillage class labels to common names, biological causes, visual symptoms, and recommended agronomic treatments.
- **`disease_detect.py`**: **TFLite Edge AI Inference Pipeline.** Loads the quantized TFLite model once at startup, dynamically inspects tensor input shape/dtype, applies blur (Laplacian variance) and luminance quality gates, enforces softmax confidence thresholding (`0.70`), exact string label matching, and performance benchmarking (`benchmark(n=50)`).

### 2.4 Web Server & Supervisor Entry Point
- **`app.py`**: **Flask Dashboard & REST API Server.** Serves offline-first responsive web UI and REST endpoints (`/api/sensor`, `/api/history`, `/api/irrigation_events`, `/api/disease_log`, `/api/control`, `/api/estop`, `/api/health`). Thread-safe: reads cached telemetry to prevent SPI bus race conditions.
- **`templates/dashboard.html`**: **Web Dashboard User Interface.** Modern dark mode layout built with pure Vanilla CSS/JS (zero CDN dependencies). Features live gauge color-coding (red/amber/green), real-time SVG soil chart, interactive controls, and disease log tables.
- **`main.py`**: **System Entry Point & Supervisor.** Executes the Finite State Machine (`BOOT` -> `SELF_TEST` -> `IDLE` -> `MONITORING` -> `SAFE_STATE`), mandatory startup hardware diagnostics, watchdog thread, fail-safe `SIGTERM`/`SIGINT` signal handlers, and opt-in `--simulate` mode.

### 2.5 Standalone Hardware Test Suite (§10)
- **`test_soil.py`**: Tests MCP3008 SPI ADC communication and soil moisture percentage calculation.
- **`test_dht.py`**: Tests DHT11/22 1-wire temperature and humidity sensor reading.
- **`test_relay.py`**: Pulses water pump relay (CH1) and grass cutter relay (CH2) for 1.5s to verify active-LOW switching.
- **`test_alert.py`**: Pulses piezo buzzer and red alert LED.
- **`test_camera.py`**: Tests OV5647 CSI `picamera2` singleton capture and saves `test_camera_capture.jpg`.
- **`test_motors.py`**: Tests dual BTS7960 chassis motor directions (Forward, Backward, Left Turn, Right Turn) and PWM speed control.

### 2.6 PC / Colab Training & Field Capture (§9)
- **`train_plant_disease_model.py`**: Trains MobileNetV2 on PlantVillage dataset using two-stage transfer learning (frozen head at LR 1e-3, fine-tune top layers at LR 1e-5). Applies class weighting, exports dynamic-range quantized `plant_model.tflite` & `labels.txt`, and evaluates accuracy gap on physical field photos.
- **`capture_field_dataset.py`**: Runs ON THE PI using `picamera2` to capture real field photos at rover height and tilt for fine-tuning and testing (no mock fallback allowed).

---

## 3. Step-by-Step Execution & Verification Sequence

Follow this exact sequence to setup, train, test, and run the software:

```
[Step 1: Install Dependencies] ---> [Step 2: Unzip Dataset & Train Model]
                                          |
                                          v
[Step 5: Deploy on Pi / systemd] <-- [Step 4: Run Simulation] <-- [Step 3: Run Test Suite]
```

### Step 1: Install Dependencies

> [!NOTE]
> **Windows PC vs. Raspberry Pi Installation:**
> - **On Windows (for PC simulation & model training):** Do **NOT** install `spidev` or `RPi.GPIO` (they are Linux/Pi kernel drivers). On Windows, install only pure Python/PC libraries.
> - **On Raspberry Pi 4:** Install hardware drivers via `apt-get` (pre-compiled binaries).

#### A. On Windows PC (for testing `--simulate` mode & model training):
```cmd
pip install flask numpy pillow opencv-python matplotlib scikit-learn tensorflow
```

#### B. On Raspberry Pi 4 (Raspberry Pi OS):
```bash
# System pre-compiled hardware packages
sudo apt-get update
sudo apt-get install -y python3-spidev python3-rpi.gpio python3-picamera2 python3-opencv
pip install pyserial smbus2

# Python environment packages
pip install flask numpy pillow adafruit-circuitpython-dht tflite-runtime
```

### Step 2: Unzip Dataset & Train AI Model
1. **Unzip the Dataset:**
   ```bash
   python -c "import zipfile, os; os.makedirs('plantvillage_dataset', exist_ok=True); zipfile.ZipFile('plantdisease.zip').extractall('plantvillage_dataset'); print('Unzipped!')"
   ```
2. **Train MobileNetV2 & Export Quantized TFLite Model:**
   ```bash
   python train_plant_disease_model.py
   ```
   *Outputs generated:* `models/plant_model.tflite` and `models/labels.txt`.

### Step 3: Verify Hardware with Standalone Test Suite
Run individual test scripts (use `--simulate` if testing on a PC without physical Pi hardware):

```bash
# 1. Soil Sensor Test
python test_soil.py --simulate

# 2. DHT Temperature & Humidity Test
python test_dht.py --simulate

# 3. Relay Module Test (Pump & Cutter)
python test_relay.py --simulate

# 4. Buzzer & LED Alert Test
python test_alert.py --simulate

# 5. Picamera2 Capture Test
python test_camera.py --simulate

# 6. BTS7960 Chassis Motors Test
python test_motors.py --simulate
```
*Expected Output:* Every test prints `[PASS] RESULT: PASS`.

### Step 4: Run System in PC Simulation Mode
To test the complete thread supervisor, FSM state transitions, SQLite logging, and web dashboard locally on your laptop:

```bash
python main.py --simulate
```

1. Open your browser and navigate to: `http://localhost:5000`
2. You will see the **AgroNex-Pi Dark Mode Dashboard**.
3. Verify live soil gauge, CPU temperature, telemetry updates, manual pump/cutter override buttons, and disease scan trigger.
4. Press `Ctrl+C` in the terminal to verify clean shutdown and emergency relay de-energization.

### Step 5: Physical Deployment on Raspberry Pi 4
When deploying on the physical Raspberry Pi 4 Model B:

1. **Start the Supervisor directly:**
   ```bash
   python main.py
   ```
2. **Or run as a systemd service (auto-start on boot):**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable agronex.service
   sudo systemctl start agronex.service
   ```
3. Access dashboard from any phone or laptop connected to the same Wi-Fi network:
   `http://<RASPBERRY_PI_IP>:5000`
