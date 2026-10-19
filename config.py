#!/usr/bin/env python3
"""
AgroNex-Pi: Global System Configuration & Constants

Centralized configuration file for AgroNex-Pi autonomous smart gardening
and farm maintenance robot.

All pin assignments use BCM numbering.
DO NOT modify pin assignments without verifying physical wiring.
"""

import os

# BASE DIRECTORY
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------------------------------------------------------
# 1. GPIO PIN MAP (BCM NUMBERING) - §2 Specification
# -----------------------------------------------------------------------------
# Power & Ground Reference (Documentary only):
# Physical Pin 1:  3.3V (DHT VCC, MCP3008 VDD/VREF)
# Physical Pin 2:  5.0V (Relay Module VCC)
# Physical Pin 4:  5.0V (Buck converter output)
# Physical Pin 6:  GND  (DHT GND)
# Physical Pin 25: GND  (MCP3008 AGND pin 14 + DGND pin 9)
# Physical Pin 39: GND  (BTS7960 power/logic ground)

# Sensors & Signal Pins
PIN_DHT_DATA = 4       # Physical Pin 7: DHT11/22 DATA (10k pull-up to 3.3V)
PIN_RELAY_PUMP = 17    # Physical Pin 11: Relay CH1 - Water Pump (Active LOW)
PIN_RELAY_CUTTER = 27  # Physical Pin 13: Relay CH2 - Grass Cutter (Active LOW)
PIN_BUZZER = 22        # Physical Pin 15: 5V Active Buzzer +
PIN_LED = 23           # Physical Pin 16: Red LED Anode (via 220 Ohm resistor)

# -----------------------------------------------------------------------------
# ADS1115 16-Bit 4-Channel I2C ADC (Primary Analog to Digital Converter)
# Connects to Raspberry Pi I2C Bus 1 (Physical Pin 3: SDA, Physical Pin 5: SCL)
# -----------------------------------------------------------------------------
USE_ADS1115 = True
ADS1115_I2C_BUS = 1
ADS1115_I2C_ADDRESS = 0x48  # Default address with ADDR connected to GND
ADS1115_CH_SOIL = 0         # Channel A0: Capacitive Soil Moisture Sensor v1.2
ADS1115_CH_WATER = 1        # Channel A1: HW-038 Water Level Sensor (3-pin)
ADS1115_CH_SPARE1 = 2       # Channel A2: Spare / Optional Battery Voltage Divider
ADS1115_CH_SPARE2 = 3       # Channel A3: Spare analog channel

# Calibration for ADS1115 (16-bit signed, range 0-32767 for 0-4.096V)
ADS_SOIL_DRY = 26300.0      # Measured raw reading in dry air (~3.28V on 3.3V rail -> 0% moisture)
ADS_SOIL_WET = 9500.0       # Raw reading submerged in water (~1.2V -> 100% moisture)
ADS_SOIL_MIN_VALID = 500    # Below this indicates short-circuit
ADS_SOIL_MAX_VALID = 32000  # Above this indicates open-circuit / disconnected

# HW-038 Water Level Sensor (3-pin: VCC, GND, Analog OUT to ADS1115 A1)
HW038_RAW_EMPTY = 1200.0    # Raw ADC reading when reservoir is completely dry
HW038_RAW_FULL = 18500.0    # Raw ADC reading when probe is submerged to ~4cm mark
WATER_CRITICAL_LOW = 20.0   # Percentage below which pump must NOT dry-run

# SPI Bus Pins (MCP3008 ADC fallback / backward compatibility)
PIN_SPI_MOSI = 10      # Physical Pin 19: MCP3008 DIN
PIN_SPI_MISO = 9       # Physical Pin 21: MCP3008 DOUT
PIN_SPI_SCLK = 11      # Physical Pin 23: MCP3008 CLK
PIN_SPI_CE0 = 8        # Physical Pin 24: MCP3008 CS/SHDN
MCP3008_CH_SOIL = 0    # Channel 0: Capacitive Soil Moisture Sensor v1.2
MCP3008_CH_BATT = 1    # Channel 1: Reserved for optional battery voltage divider

# Dual BTS7960 motor-driver pins
# BTS #1 drives the front-left and rear-left motors in parallel.
# BTS #2 drives the front-right and rear-right motors in parallel.
# Connect each board's R_EN and L_EN to 5 V (enabled). All Pi, BTS7960 and
# battery grounds must meet at one common star-ground point.
PIN_LEFT_RPWM = 5       # Physical Pin 29: BTS #1 RPWM, left side forward
PIN_LEFT_LPWM = 6       # Physical Pin 31: BTS #1 LPWM, left side reverse
PIN_RIGHT_RPWM = 13     # Physical Pin 33: BTS #2 RPWM, right side forward
PIN_RIGHT_LPWM = 19     # Physical Pin 35: BTS #2 LPWM, right side reverse
PWM_FREQ_MOTORS = 1000  # BTS7960 software PWM frequency

# -----------------------------------------------------------------------------
# Dual BTS7960 Motor Controller & Servo Actuators via Arduino Uno Slave
# Arduino Uno is connected to Raspberry Pi via standard USB data cable (/dev/ttyACM0 or /dev/ttyUSB0).
# Arduino controls: 2 BTS7960 Drivers (4 motors), Front & Back Servos, Front & Back Ultrasonics, Actuator Servo.
# -----------------------------------------------------------------------------
ARDUINO_ENABLED = True
ARDUINO_SERIAL_PORT = "/dev/ttyACM0"
ARDUINO_BAUDRATE = 115200

# Arduino UNO Hardware Pin Mapping (Documentary Reference):
# BTS #1 (Left Motors):   RPWM=D5, LPWM=D6, EN=D4
# BTS #2 (Right Motors):  RPWM=D3, LPWM=D11, EN=D7
# Actuator Servo:         D9
# Front Pan Servo:        D10
# Rear Pan Servo:         D12
# Front Ultrasonic HC-SR04: Trig=D2, Echo=D8
# Rear Ultrasonic HC-SR04:  Trig=A0, Echo=A1


# Navigation sensors
# NEO-7M TX -> Pi GPIO15/RXD (pin 10). Its RX is optional for configuration.
GPS_SERIAL_PORT = "/dev/serial0"
GPS_BAUDRATE = 9600
GPS_FIX_MAX_AGE = 5.0
# Simulated GPS coordinates (used only in --simulate mode; set to your test location)
GPS_SIM_LAT = 19.0760    # Default: Mumbai, India — change to your actual farm coordinates
GPS_SIM_LON = 72.8777
# HMC5883L: SDA -> GPIO2/pin 3, SCL -> GPIO3/pin 5, powered at 3.3 V.
HMC5883L_I2C_BUS = 1
HMC5883L_I2C_ADDRESS = 0x1E
COMPASS_DECLINATION_DEG = 0.0  # Set after local calibration.

# -----------------------------------------------------------------------------
# 2. IRRIGATION & SUBSYSTEM TIMINGS (§5.2)
# -----------------------------------------------------------------------------
MOISTURE_LOW = 35.0         # Below this soil moisture percentage, pump starts ON
MOISTURE_HIGH = 65.0        # Above this soil moisture percentage, pump turns OFF
POLL_INTERVAL = 1.0         # Control loop polling interval in seconds (rapid telemetry refresh)
ACTUATOR_AUTO_INTERVAL = 3600.0  # Automatic soil moisture probe cycle: 1 hour (3600s)
DHT_TEMP_INTERVAL = 600.0        # Automatic temperature & humidity scan: 10 minutes (600s)
WATER_MONITOR_CONTINUOUS = True  # Real-time water level continuous polling without delay
PUMP_MAX_RUNTIME = 60.0     # Max continuous pump runtime (seconds) to prevent dry running
PUMP_COOLDOWN = 120.0       # Minimum off-time (seconds) between irrigation cycles

# ADC Calibration parameters for Capacitive Soil Moisture Sensor v1.2 (3.3V VREF)
# Typical raw ADC values: Dry Air ~ 850, Submerged Water ~ 380
ADC_DRY = 850.0             # Raw ADC reading corresponding to 0% moisture
ADC_WET = 380.0             # Raw ADC reading corresponding to 100% moisture

# Implausible ADC threshold range (detects disconnected or shorted probe)
ADC_MIN_VALID = 50          # ADC < 50 suggests short-circuit / faulty sensor
ADC_MAX_VALID = 1000        # ADC > 1000 suggests open circuit / disconnected sensor

# -----------------------------------------------------------------------------
# 3. CUTTER SCHEDULING & SAFETY (§5.3)
# -----------------------------------------------------------------------------
CUTTER_ENABLED = True       # Master software enable flag for cutter relay
CUTTER_INTERVAL = 3600.0    # Time between automated grass trim runs (seconds)
CUTTER_DURATION = 30.0      # Duration of each grass trim run (seconds)

# -----------------------------------------------------------------------------
# 4. NAVIGATION PARAMETERS (§5.4)
# -----------------------------------------------------------------------------
MOTOR_SPEED_DEFAULT = 60.0  # Duty cycle percentage (0-100%) for forward drive
MOTOR_SPEED_TURN = 50.0     # Duty cycle percentage for turns
NAV_DRIVE_SLICE = 1.0       # Maximum forward burst before GPS/heading re-check
NAV_TURN_SLICE = 0.20       # Maximum pivot burst before heading re-check
NAV_HEADING_TOLERANCE_DEG = 12.0
NAV_WAYPOINT_REACHED_M = 2.5
# Populate before autonomous motion, e.g. [(12.9716, 77.5946)]. Empty = stop.
NAV_WAYPOINTS = []

# -----------------------------------------------------------------------------
# 5. DISEASE DETECTION & INFERENCE (§5.5)
# -----------------------------------------------------------------------------
DISEASE_SCAN_INTERVAL = 300.0   # Periodic auto-scan interval (seconds)
DISEASE_AUTO_GREEN_TRIGGER = True  # Auto-scan when green plant fills frame
GREEN_PIXEL_THRESHOLD = 0.08   # 8% of frame green is sufficient to trigger (was 0.15)
GREEN_H_LOW, GREEN_H_HIGH = 25, 95   # HSV hue range widened for indoor warm lighting (was 35, 90)
GREEN_S_LOW, GREEN_S_HIGH = 30, 255  # Lower saturation minimum for indoor ambient light (was 40)
GREEN_V_LOW, GREEN_V_HIGH = 40, 255  # HSV value range
AUTO_SCAN_COOLDOWN = 10.0      # Cooldown between scans reduced to 10s for responsive feedback
CONFIDENCE_THRESHOLD = 0.70     # Softmax confidence gate for disease classification

# Image Quality Gates (Tuned for real-world Raspberry Pi camera in diverse lighting)
LAPLACIAN_VAR_MIN = 12.0        # Variance of Laplacian blur threshold (was 50.0)
BRIGHTNESS_MIN = 15.0           # Minimum acceptable mean luminance (0-255)
BRIGHTNESS_MAX = 250.0          # Maximum acceptable mean luminance (0-255)

# Target PlantVillage Classes (must match models/labels.txt after training)
TARGET_CLASSES = [
    "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___healthy",
    "background_not_a_leaf",
]

# -----------------------------------------------------------------------------
# 6. SYSTEM PATHS & DIRECTORIES (§4) - DUAL-MODEL ARCHITECTURE (Strategy A)
# -----------------------------------------------------------------------------
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Dual-Model Switch:
# Set to 'custom' to use the Local Plants model (Tulsi & Money Plant)
# Set to 'plantvillage' to use the broad agricultural model (Tomato, Potato, Pepper)
ACTIVE_MODEL_PROFILE = os.environ.get("AGRONEX_MODEL_PROFILE", "custom").lower()

CUSTOM_MODEL_PATH = os.path.join(MODELS_DIR, "custom_plant_model.tflite")
CUSTOM_LABELS_PATH = os.path.join(MODELS_DIR, "custom_labels.txt")
BASE_MODEL_PATH = os.path.join(MODELS_DIR, "plant_model.tflite")
BASE_LABELS_PATH = os.path.join(MODELS_DIR, "labels.txt")

# Select active model based on profile and file availability
if ACTIVE_MODEL_PROFILE == "custom" and os.path.exists(CUSTOM_MODEL_PATH) and os.path.exists(CUSTOM_LABELS_PATH):
    MODEL_PATH = CUSTOM_MODEL_PATH
    LABELS_PATH = CUSTOM_LABELS_PATH
else:
    MODEL_PATH = BASE_MODEL_PATH
    LABELS_PATH = BASE_LABELS_PATH


STATIC_DIR = os.path.join(BASE_DIR, "static")
SCANS_DIR = os.path.join(STATIC_DIR, "scans")

LOGS_DIR = os.path.join(BASE_DIR, "logs")
DB_PATH = os.path.join(LOGS_DIR, "agronex.db")
LOG_PATH = os.path.join(LOGS_DIR, "agronex.log")
RUNTIME_CONFIG_PATH = os.path.join(BASE_DIR, "runtime_config.json")

# Field dataset captured by students using the Pi camera
FIELD_DATASET_DIR = os.path.join(BASE_DIR, "field_dataset")

# Ensure required runtime folders exist
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(SCANS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(FIELD_DATASET_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# 7. AWS CLOUD RELAY (API Gateway + Lambda)
# Replace the placeholder with your actual API Gateway Invoke URL after deploy.
# -----------------------------------------------------------------------------
AWS_API_URL = os.environ.get(
    "AGRONEX_AWS_URL",
    "https://fyxosg11ad.execute-api.ap-south-1.amazonaws.com"
)
AWS_API_KEY            = os.environ.get("AGRONEX_AWS_KEY", "")   # optional API Key
AWS_RELAY_INTERVAL     = 5.0   # seconds between telemetry pushes to cloud
CAMERA_SNAPSHOT_INTERVAL = 60  # seconds between camera JPEG uploads to AWS /snapshot (1 min)
AWS_ENABLED = ("REPLACE_ME" not in AWS_API_URL)          # auto-disable until configured


def load_runtime_config():
    """Apply moisture thresholds saved from the dashboard across reboots."""
    global MOISTURE_LOW, MOISTURE_HIGH
    if not os.path.isfile(RUNTIME_CONFIG_PATH):
        return
    try:
        import json
        with open(RUNTIME_CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "moisture_low" in data:
            MOISTURE_LOW = float(data["moisture_low"])
        if "moisture_high" in data:
            MOISTURE_HIGH = float(data["moisture_high"])
    except Exception:
        pass


load_runtime_config()

# -----------------------------------------------------------------------------
# 8. MISTRAL AI CHATBOT (Kisan Mitra / Multilingual Farm Assistant)
# Paste your Mistral API Key here or set MISTRAL_API_KEY environment variable.
# -----------------------------------------------------------------------------
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "mstrl_MTvPBRlJLRVQnpnk61HDpurJoT7L9Deb_0Jt5kr")
MISTRAL_MODEL   = os.environ.get("MISTRAL_MODEL", "open-mistral-7b")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# -----------------------------------------------------------------------------
# 9. USER AUTHENTICATION & ACCESS CONTROL (§5.8)
# Secret verification key required for new farmer account registration
# -----------------------------------------------------------------------------
FARMER_VERIFICATION_KEY = os.environ.get("AGRONEX_VERIFY_KEY", "AGRONEX_FARM_2026")
AUTH_SECRET_KEY         = os.environ.get("AGRONEX_AUTH_SECRET", "agronex_secret_session_key_2026")
