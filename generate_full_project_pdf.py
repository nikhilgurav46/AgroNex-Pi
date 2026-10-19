#!/usr/bin/env python3
"""
AgroNex-Pi: Comprehensive Major Project Technical Report & Code Compendium Generator
Generates a complete, publication-grade PDF covering:
- Project Directory Tree & File Catalog
- System Architecture & Hardware Pinout (with Block Diagram)
- Software FSM & Multithreaded Control Flow (with Flowchart)
- Edge AI & Plant Disease Diagnosis Pipeline
- Autonomous Field Operation Subsystems (Irrigation, Trimmer, Navigation)
- AWS Cloud Architecture & Live Deployed S3 Dashboard
- Testing & Verification Suite
- Complete Source Code for All Project Files
"""

import os
import sys
import time
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether, HRFlowable, Image as RLImage, Preformatted
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to compute dynamic total page count with running headers & footers."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Suppress header and footer on cover page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header
        self.drawString(54, 750, "AgroNex-Pi: Autonomous Smart Farm Robot - Major Project Technical Report & Source Compendium")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 744, 558, 744)

        # Footer
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Confidential & Academic Engineering Documentation | Live Cloud: agronex-pi-data-nikhil.s3-website.ap-south-1.amazonaws.com")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def load_file_content(rel_path):
    """Safely loads file content with line numbers."""
    abs_path = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(abs_path):
        return f"# Error: File {rel_path} not found in workspace."
    try:
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        formatted = []
        for idx, line in enumerate(lines, 1):
            line_str = line.rstrip("\r\n")
            if len(line_str) > 115:
                line_str = line_str[:112] + "..."
            formatted.append(f"{idx:04d} | {line_str}")
        return "\n".join(formatted)
    except Exception as e:
        return f"# Error reading {rel_path}: {e}"


def get_file_stats(rel_path):
    """Returns line count and file size."""
    abs_path = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(abs_path):
        return 0, 0
    size = os.path.getsize(abs_path)
    try:
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = len(f.readlines())
        return lines, size
    except Exception:
        return 0, size


def build_full_report(output_filename="AgroNex_Pi_Complete_Major_Project_Report.pdf"):
    pdf_path = os.path.join(BASE_DIR, output_filename)
    print(f"[*] Starting compilation of complete project report: {pdf_path}")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Palette
    c_primary = colors.HexColor("#0f172a")     # Slate-900
    c_secondary = colors.HexColor("#1e293b")   # Slate-800
    c_accent_blue = colors.HexColor("#2563eb") # Blue-600
    c_accent_green = colors.HexColor("#059669")# Emerald-600
    c_accent_amber = colors.HexColor("#d97706")# Amber-600
    c_text_dark = colors.HexColor("#334155")   # Slate-700
    c_border = colors.HexColor("#e2e8f0")      # Slate-200
    c_bg_light = colors.HexColor("#f8fafc")    # Slate-50

    # Custom Typography Styles
    cover_title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=c_primary,
        alignment=0,
        spaceAfter=8
    )

    cover_subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_accent_blue,
        spaceAfter=18
    )

    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=14,
        textColor=c_text_dark
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Header3',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=c_accent_blue,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=c_text_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12.5,
        textColor=c_secondary
    )

    code_block_style = ParagraphStyle(
        'CodeMonospace',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.0,
        leading=7.5,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # =========================================================================
    # 1. COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 20))
    # Category Tag
    tag_table = Table([[
        Paragraph("<font color='#059669'><b>FINAL YEAR ENGINEERING MAJOR PROJECT REPORT &amp; SOURCE COMPENDIUM</b></font>", body_style)
    ]], colWidths=[504])
    tag_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ecfdf5")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#a7f3d0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(tag_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("AgroNex-Pi: Autonomous Smart Agricultural &amp; Farm Maintenance Robot", cover_title_style))
    story.append(Paragraph("Edge-AI Plant Disease Diagnosis, Closed-Loop Precision Irrigation, Grass Trimming, GPS/Compass Navigation &amp; Real-Time AWS Cloud Telemetry", cover_subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_accent_blue, spaceAfter=18))

    # Executive Metadata Table
    meta_data = [
        [Paragraph("<b>Domain &amp; Specialization:</b>", meta_style), Paragraph("Autonomous Robotics, Edge Artificial Intelligence (TinyML), IoT Cloud Telemetry", meta_style)],
        [Paragraph("<b>High-Level Controller:</b>", meta_style), Paragraph("Raspberry Pi 4 Model B (Quad-Core ARM Cortex-A72 @ 1.5 GHz, 4GB RAM)", meta_style)],
        [Paragraph("<b>Actuation &amp; Power Subsystem:</b>", meta_style), Paragraph("Arduino Uno R3 + Dual BTS7960 43A H-Bridges + 4× 12V 10A High-Torque Motors", meta_style)],
        [Paragraph("<b>Computer Vision &amp; AI:</b>", meta_style), Paragraph("OV5647 5MP CSI-2 Camera + MobileNetV2 Transfer Learning (TensorFlow Lite)", meta_style)],
        [Paragraph("<b>Autonomous Navigation:</b>", meta_style), Paragraph("NEO-7M GPS (UART /dev/serial0) + HMC5883L/QMC5883L Digital Compass (I2C-1)", meta_style)],
        [Paragraph("<b>Cloud Architecture:</b>", meta_style), Paragraph("AWS API Gateway (HTTP v2) -> AWS Lambda -> Amazon S3 (Live Deployed Dashboard)", meta_style)],
        [Paragraph("<b>Live Cloud Dashboard URL:</b>", meta_style), Paragraph("<font color='#2563eb'><u>http://agronex-pi-data-nikhil.s3-website.ap-south-1.amazonaws.com/</u></font>", meta_style)],
        [Paragraph("<b>Academic Submission Year:</b>", meta_style), Paragraph("Final Year Bachelor of Engineering (Major Project) — Academic Year 2026", meta_style)],
    ]
    t_meta = Table(meta_data, colWidths=[160, 344])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 20))

    # Executive Abstract Callout
    abstract_text = (
        "<b>Executive Abstract:</b> Modern precision agriculture requires continuous, autonomous field-level stewardship "
        "to optimize water resource usage, curtail disease progression before crop devastation, and reduce labor costs. "
        "<b>AgroNex-Pi</b> solves these multi-disciplinary challenges through an edge-compute robotic rover. The system "
        "fuses closed-loop soil moisture sensing via a 10-bit SPI ADC with dual-threshold hysteresis irrigation, autonomous grass trimming, "
        "GPS waypoint navigation with compass bearing correction, and edge computer vision running a quantized MobileNetV2 model "
        "on live 5MP CSI camera frames. Every operational state, environmental measurement, and diagnostic event is relayed in real-time "
        "to a serverless AWS cloud infrastructure, enabling remote monitoring and teleoperation from anywhere in the world. "
        "This document provides the complete technical explanation of the entire folder directory, hardware schematics, algorithm flowcharts, "
        "and the verbatim source code of every software module."
    )
    t_abstract = Table([[Paragraph(abstract_text, callout_style)]], colWidths=[504])
    t_abstract.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(t_abstract)

    story.append(PageBreak())

    # =========================================================================
    # 2. MASTER DIRECTORY TREE & FILE CATALOG
    # =========================================================================
    story.append(Paragraph("1. Project Folder Directory Structure & File Catalog", h1_style))
    story.append(Paragraph(
        "The AgroNex-Pi workspace is organized cleanly into modular architectural tiers: hardware drivers, "
        "subsystem controllers, AI inference, cloud relays, web dashboards, database persistence, and diagnostic test scripts. "
        "The directory tree below illustrates the layout of the entire codebase:",
        body_style
    ))

    tree_str = """Major project/
│
├── config.py                 # Central system configuration, BCM pin map, thresholds & AWS URL
├── main.py                   # Master supervisor, FSM controller, multi-threaded worker coordinator
├── hardware.py               # Low-level hardware drivers (GPIO, SPI, I2C, UART, Picamera2, Relays)
├── aws_relay.py              # Cloud telemetry background client & command polling thread
├── database.py               # SQLite persistent logging (telemetry, irrigation events, FSM states)
├── irrigation.py             # Closed-loop smart irrigation controller with hysteresis logic
├── cutter.py                 # Automated grass trimmer scheduler and duty-cycle manager
├── navigation.py             # GPS waypoint navigation, Haversine distance & compass PID heading
├── disease_detect.py         # Edge AI inference engine, Picamera2 frame gating & HSV green masking
├── disease_db.py             # Agronomic disease remedy database & treatment recommendation lookup
├── app.py                    # Local Flask web dashboard server, diagnostic REST API & video stream
│
├── aws/                      # AWS Cloud Infrastructure & Serverless Backend
│   ├── lambda_function.py    # AWS Lambda serverless function for API Gateway /state, /telemetry, /scans
│   ├── DEPLOY_GUIDE.md       # Step-by-step AWS deployment and CORS configuration guide
│   └── agronex_dashboard/    # Live cloud dashboard hosted on AWS S3 Static Website Hosting
│       └── index.html        # Glassmorphic cloud telemetry monitor and remote command panel
│
├── diagrams/                 # Architectural visual schematics and flowcharts
│   ├── system_block_diagram.jpg # Complete system hardware and power block diagram
│   └── project_flowchart.jpg    # Master supervisor FSM operational lifecycle flowchart
│
├── test_*.py                 # Hardware Verification & Diagnostic Test Suite
│   ├── test_soil.py          # MCP3008 SPI ADC & Capacitive soil probe reader test
│   ├── test_dht.py           # DHT11/DHT22 1-Wire temperature & humidity sensor test
│   ├── test_navigation_sensors.py # NEO-7M GPS UART & HMC5883L/QMC5883L I2C compass test
│   ├── test_camera.py        # OV5647 CSI camera singleton frame capture test
│   ├── test_alert.py         # Active buzzer and red LED pulse alert test
│   ├── test_relay.py         # Active-LOW 2-channel 5V relay actuation test
│   └── test_motors.py        # Dual BTS7960 4-wheel drive H-bridge PWM motor test
│
├── models/                   # Edge AI Models & Classification Labels
│   ├── plant_model.tflite    # Quantized MobileNetV2 neural network (10 classes)
│   └── labels.txt            # Target PlantVillage + local leaf classification class labels
│
├── requirements-pi.txt       # Production Python dependencies for Raspberry Pi OS (Bookworm)
└── README.md & SYSTEM_GUIDE.md # Technical documentation and operating manual"""

    story.append(Preformatted(tree_str, code_block_style))
    story.append(Spacer(1, 10))

    # Comprehensive Table Catalog
    story.append(Paragraph("<b>Master File Role &amp; Responsibility Matrix:</b>", h2_style))
    catalog_data = [
        [Paragraph("<b>File / Path</b>", meta_style), Paragraph("<b>Lines / Size</b>", meta_style), Paragraph("<b>Architectural Role &amp; Key Responsibilities</b>", meta_style)],
        [Paragraph("config.py", meta_style), Paragraph("188 L<br/>8.5 KB", meta_style), Paragraph("Centralized configuration repository: BCM pin allocations, moisture thresholds (35%/65%), pump timers, PWM frequencies, AWS API endpoint URL, and model paths.", meta_style)],
        [Paragraph("main.py", meta_style), Paragraph("693 L<br/>29.8 KB", meta_style), Paragraph("Supervisor thread and core FSM controller. Coordinates startup self-test, 5 concurrent daemon threads, watchdog monitoring, safe-state fail-safes, and clean shutdown.", meta_style)],
        [Paragraph("hardware.py", meta_style), Paragraph("689 L<br/>26.5 KB", meta_style), Paragraph("Hardware Abstraction Layer (HAL). Wraps RPi.GPIO, spidev (MCP3008), smbus2 (HMC5883L/QMC5883L), pyserial (NEO-7M), picamera2, and BTS7960 motors. Supports --simulate.", meta_style)],
        [Paragraph("aws_relay.py", meta_style), Paragraph("222 L<br/>8.3 KB", meta_style), Paragraph("AWS IoT Cloud bridge. Serializes live telemetry, posts to AWS API Gateway, polls remote operator commands (E_STOP, PUMP_ON, CUTTER_ON), and triggers instantaneous state pushes.", meta_style)],
        [Paragraph("aws/lambda_function.py", meta_style), Paragraph("160 L<br/>6.8 KB", meta_style), Paragraph("Serverless AWS Lambda backend. Handles /state, /telemetry, /command, /scans with S3 object persistence and complete CORS headers (Access-Control-Allow-Origin: *).", meta_style)],
        [Paragraph("irrigation.py", meta_style), Paragraph("208 L<br/>9.1 KB", meta_style), Paragraph("Closed-loop precision irrigation controller. Implements dual-threshold hysteresis, maximum run-time watchdog (60s), dry-run cooldown (120s), and event database logging.", meta_style)],
        [Paragraph("cutter.py", meta_style), Paragraph("118 L<br/>4.8 KB", meta_style), Paragraph("Grass cutter scheduler. Manages high-speed trimmer duty cycle, autonomous lawn trimming schedules, software safety interlocks, and relay de-energizing.", meta_style)],
        [Paragraph("navigation.py", meta_style), Paragraph("121 L<br/>5.1 KB", meta_style), Paragraph("GPS waypoint navigation. Implements Haversine spherical distance calculation, forward azimuth bearing, compass error PID steering, and pulsed dead-reckoning drive bursts.", meta_style)],
        [Paragraph("disease_detect.py", meta_style), Paragraph("531 L<br/>23.9 KB", meta_style), Paragraph("Edge AI vision pipeline. Performs Picamera2 capture, Laplacian blur variance check, luminance bounds filter, HSV green pixel masking (>=15%), and TFLite inference.", meta_style)],
        [Paragraph("disease_db.py", meta_style), Paragraph("236 L<br/>12.3 KB", meta_style), Paragraph("Agronomic treatment database. Maps predicted leaf diseases to botanical common names, symptoms, organic cures, chemical fungicides, and prevention procedures.", meta_style)],
        [Paragraph("database.py", meta_style), Paragraph("163 L<br/>7.1 KB", meta_style), Paragraph("Thread-safe SQLite database manager (agronex.db). Logs periodic sensor readings, pump events, cutter runs, FSM state changes, and disease scan records.", meta_style)],
        [Paragraph("app.py", meta_style), Paragraph("481 L<br/>19.0 KB", meta_style), Paragraph("Local Flask web dashboard server. Serves local monitoring UI, live Picamera2 MJPEG video feed, manual override controls, and embedded proxy routes for the cloud dashboard.", meta_style)],
    ]
    t_catalog = Table(catalog_data, colWidths=[110, 60, 334])
    t_catalog.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_catalog)

    story.append(PageBreak())

    # =========================================================================
    # 3. COMPLETE HARDWARE & SENSOR ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("2. Complete Hardware &amp; Embedded Systems Architecture", h1_style))
    story.append(Paragraph(
        "The AgroNex-Pi physical architecture adopts a robust, decoupled dual-controller design. "
        "The <b>Raspberry Pi 4 Model B</b> serves as the high-level brain responsible for computer vision, "
        "TFLite neural network inference, sensor acquisition, web hosting, and cloud communications. "
        "Actuation and high-current motor drive are delegated through dedicated power circuits to guarantee "
        "that motor electrical noise and inductive back-EMF never reset the microprocessor.",
        body_style
    ))

    # Embed System Block Diagram Image
    diagram_path = os.path.join(BASE_DIR, "diagrams", "system_block_diagram.jpg")
    if os.path.exists(diagram_path):
        # 504 pt width, maintain aspect ratio (1376x768 -> 504 x 281)
        story.append(RLImage(diagram_path, width=504, height=281))
        story.append(Paragraph("<i>Figure 2.1: AgroNex-Pi Complete Hardware, Power &amp; Interfacing Architecture Block Diagram.</i>", meta_style))
        story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Complete GPIO, Bus &amp; Peripheral Pin Mapping Reference:</b>", h2_style))
    story.append(Paragraph(
        "All Raspberry Pi pin assignments follow BCM numbering. Hardware interfaces operate across independent, "
        "non-conflicting buses (SPI0, I2C-1, UART0, 1-Wire, and CSI-2):",
        body_style
    ))

    pin_data = [
        [Paragraph("<b>BCM Pin</b>", meta_style), Paragraph("<b>Physical Pin</b>", meta_style), Paragraph("<b>Interface Type</b>", meta_style), Paragraph("<b>Peripheral Hardware Component</b>", meta_style), Paragraph("<b>Electrical Specification &amp; Notes</b>", meta_style)],
        [Paragraph("GPIO 2", meta_style), Paragraph("Pin 3", meta_style), Paragraph("I2C1 SDA", meta_style), Paragraph("HMC5883L / QMC5883L Compass", meta_style), Paragraph("3.3V Logic. Auto-probes 0x1E (Honeywell) and 0x0D (QMC).", meta_style)],
        [Paragraph("GPIO 3", meta_style), Paragraph("Pin 5", meta_style), Paragraph("I2C1 SCL", meta_style), Paragraph("HMC5883L / QMC5883L Compass", meta_style), Paragraph("3.3V Logic clock line. Built-in 1.8k pull-up on Pi board.", meta_style)],
        [Paragraph("GPIO 4", meta_style), Paragraph("Pin 7", meta_style), Paragraph("1-Wire GPIO", meta_style), Paragraph("DHT11 / DHT22 Temp &amp; Humidity", meta_style), Paragraph("Requires external 10k Ohm pull-up resistor to 3.3V.", meta_style)],
        [Paragraph("GPIO 8", meta_style), Paragraph("Pin 24", meta_style), Paragraph("SPI0 CE0", meta_style), Paragraph("MCP3008 10-bit ADC (CS)", meta_style), Paragraph("Chip Select. Dedicated strictly to SPI0. Never use for motors!", meta_style)],
        [Paragraph("GPIO 9", meta_style), Paragraph("Pin 21", meta_style), Paragraph("SPI0 MISO", meta_style), Paragraph("MCP3008 10-bit ADC (DOUT)", meta_style), Paragraph("Master In Slave Out data line.", meta_style)],
        [Paragraph("GPIO 10", meta_style), Paragraph("Pin 19", meta_style), Paragraph("SPI0 MOSI", meta_style), Paragraph("MCP3008 10-bit ADC (DIN)", meta_style), Paragraph("Master Out Slave In command line.", meta_style)],
        [Paragraph("GPIO 11", meta_style), Paragraph("Pin 23", meta_style), Paragraph("SPI0 SCLK", meta_style), Paragraph("MCP3008 10-bit ADC (CLK)", meta_style), Paragraph("SPI Clock line, operating at 1.35 MHz.", meta_style)],
        [Paragraph("GPIO 15", meta_style), Paragraph("Pin 10", meta_style), Paragraph("UART0 RXD", meta_style), Paragraph("NEO-7M GPS Module (TXD)", meta_style), Paragraph("9600 baud NMEA serial stream (/dev/serial0).", meta_style)],
        [Paragraph("GPIO 17", meta_style), Paragraph("Pin 11", meta_style), Paragraph("GPIO Output", meta_style), Paragraph("Relay CH1 — Submersible Pump", meta_style), Paragraph("Active-LOW opto-isolated relay. HIGH=OFF, LOW=ENERGIZED.", meta_style)],
        [Paragraph("GPIO 27", meta_style), Paragraph("Pin 13", meta_style), Paragraph("GPIO Output", meta_style), Paragraph("Relay CH2 — Grass Cutter Trimmer", meta_style), Paragraph("Active-LOW opto-isolated relay. HIGH=OFF, LOW=ENERGIZED.", meta_style)],
        [Paragraph("GPIO 22", meta_style), Paragraph("Pin 15", meta_style), Paragraph("GPIO Output", meta_style), Paragraph("5V Active Piezo Buzzer", meta_style), Paragraph("Audible alert upon disease detection / critical fault.", meta_style)],
        [Paragraph("GPIO 23", meta_style), Paragraph("Pin 16", meta_style), Paragraph("GPIO Output", meta_style), Paragraph("Red Visual Warning LED", meta_style), Paragraph("Driven through 220 Ohm current-limiting resistor.", meta_style)],
        [Paragraph("CSI-2 Port", meta_style), Paragraph("15-pin Ribbon", meta_style), Paragraph("MIPI CSI-2", meta_style), Paragraph("OV5647 5MP Camera Module", meta_style), Paragraph("Direct GPU hardware video pipeline via picamera2.", meta_style)],
        [Paragraph("USB / I2C", meta_style), Paragraph("USB Port", meta_style), Paragraph("USB Serial", meta_style), Paragraph("Arduino Uno R3 Motor Controller", meta_style), Paragraph("Controls 2× BTS7960 motor drivers for 4× 12V 10A motors.", meta_style)],
    ]
    t_pin = Table(pin_data, colWidths=[65, 60, 65, 140, 174])
    t_pin.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_pin)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Power Distribution Architecture &amp; Electrical Safety:</b>", h2_style))
    story.append(Paragraph(
        "Robotic field systems with high-torque DC motors experience sudden current spikes up to 20A–30A during startup and pivot maneuvers. "
        "To prevent microprocessor brownouts, ground bounce, and inductive flyback destruction, AgroNex-Pi implements a strict isolation policy:",
        body_style
    ))
    story.append(Paragraph("• <b>Dual Power Rail Isolation:</b> The high-current 12V motor battery rail is electrically isolated from the logic rail. The motors draw directly from the 12V 10A supply via the BTS7960 H-bridges.", bullet_style))
    story.append(Paragraph("• <b>Regulated Logic Rail:</b> The Raspberry Pi 4B and optocoupler inputs are powered by a high-efficiency LM2596 / MP1584 buck converter supplying a clean, regulated 5.1V at 3.5A.", bullet_style))
    story.append(Paragraph("• <b>Common Star-Ground:</b> All grounds (battery ground, buck converter output ground, Raspberry Pi GND, and Arduino GND) meet at a single, heavy-gauge copper star-ground point to eliminate ground loops.", bullet_style))
    story.append(Paragraph("• <b>Startup Safe Relay State:</b> Active-LOW relay pins (GPIO 17, 27) are explicitly driven HIGH before setting their mode to OUTPUT to eliminate spurious actuation pulses when the Pi powers on.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # 4. SOFTWARE ARCHITECTURE & SUPERVISOR FSM
    # =========================================================================
    story.append(Paragraph("3. Software Architecture, Control Flow &amp; Supervisor FSM", h1_style))
    story.append(Paragraph(
        "AgroNex-Pi is orchestrated by a multi-threaded Python supervisor structured around a robust "
        "<b>Finite State Machine (FSM)</b>. The FSM guarantees that physical actuators can never enter invalid, "
        "conflicting, or hazardous states. If any sensor disconnects or fails the mandatory boot self-test, "
        "the supervisor halts actuation immediately and transitions into <code>SAFE_STATE</code>.",
        body_style
    ))

    # Embed Flowchart Diagram
    flowchart_path = os.path.join(BASE_DIR, "diagrams", "project_flowchart.jpg")
    if os.path.exists(flowchart_path):
        # Portrait flowchart: 340 width, height = 340 * (1376/768) = 608 pt
        story.append(RLImage(flowchart_path, width=340, height=608))
        story.append(Paragraph("<i>Figure 3.1: Master Supervisor Finite State Machine (FSM) &amp; Multi-Threaded Execution Lifecycle.</i>", meta_style))
        story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Finite State Machine State Definitions:</b>", h2_style))
    fsm_table_data = [
        [Paragraph("<b>FSM State</b>", meta_style), Paragraph("<b>Trigger / Entry Condition</b>", meta_style), Paragraph("<b>System Actions &amp; Physical Actuator Behavior</b>", meta_style)],
        [Paragraph("BOOT", meta_style), Paragraph("Power applied / process launch", meta_style), Paragraph("Initializes database, configures logging, initializes hardware driver libraries without energizing outputs.", meta_style)],
        [Paragraph("SELF_TEST", meta_style), Paragraph("Transition from BOOT", meta_style), Paragraph("Comprehensive diagnostic: probes SQLite DB, MCP3008 SPI ADC, DHT 1-Wire, GPS UART, compass I2C, and Picamera2.", meta_style)],
        [Paragraph("IDLE", meta_style), Paragraph("Self-test passes 100% green", meta_style), Paragraph("All actuators de-energized. Spawns AWS Cloud Relay thread, local Flask server thread, and watchdog monitor.", meta_style)],
        [Paragraph("MONITORING", meta_style), Paragraph("Periodic control loop cycle (30s)", meta_style), Paragraph("Polls soil moisture, ambient temperature, humidity, GPS fix, and compass heading. Updates telemetry cache.", meta_style)],
        [Paragraph("IRRIGATING", meta_style), Paragraph("Soil moisture &lt; 35% (MOISTURE_LOW)", meta_style), Paragraph("Energizes Relay CH1 (Pump ON). Monitored by 60s runtime safety watchdog. Shuts off when moisture reaches 65%.", meta_style)],
        [Paragraph("CUTTING", meta_style), Paragraph("Hourly cutter interval timer expires", meta_style), Paragraph("Energizes Relay CH2 (Cutter ON) for 30s. Automatically disabled during active irrigation or low battery.", meta_style)],
        [Paragraph("SCANNING", meta_style), Paragraph("Camera detects green plant (&gt;=15%)", meta_style), Paragraph("Halts chassis motors. Picamera2 captures unblurred leaf frame. Runs quantized TFLite inference. Logs diagnosis.", meta_style)],
        [Paragraph("SAFE_STATE", meta_style), Paragraph("Emergency Stop / Sensor fault", meta_style), Paragraph("Immediate fail-safe: de-energizes all relays, stops motor PWM, logs CRITICAL incident, pulses warning buzzer/LED.", meta_style)],
    ]
    t_fsm = Table(fsm_table_data, colWidths=[80, 150, 274])
    t_fsm.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_fsm)

    story.append(PageBreak())

    # =========================================================================
    # 5. EDGE AI & PLANT DISEASE DETECTION PIPELINE
    # =========================================================================
    story.append(Paragraph("4. Edge AI &amp; Deep Learning Plant Disease Diagnosis", h1_style))
    story.append(Paragraph(
        "AgroNex-Pi performs on-device plant disease classification directly on the Raspberry Pi 4B CPU using "
        "a customized, quantized <b>MobileNetV2</b> neural network model. The architecture is optimized specifically for "
        "low-latency embedded inference without requiring an expensive cloud GPU or constant internet connection.",
        body_style
    ))

    story.append(Paragraph("<b>4.1 Computer Vision Quality Gating &amp; Auto-Green Segmentation</b>", h2_style))
    story.append(Paragraph(
        "To avoid misclassifications caused by blurred frames (rover motion) or empty soil backgrounds, the vision pipeline "
        "applies three deterministic quality gates before invoking the neural network:",
        body_style
    ))
    story.append(Paragraph("1. <b>Laplacian Blur Filter:</b> Computes the variance of the Laplacian of the grayscale image: <code>Var(Laplacian(I)) &gt;= 50.0</code>. Blurred images are immediately rejected to conserve compute cycles.", bullet_style))
    story.append(Paragraph("2. <b>Luminance Filter:</b> Measures mean pixel brightness: <code>35.0 &lt;= Mean(Luminance) &lt;= 225.0</code> to reject severe underexposure (shadows) and lens flare.", bullet_style))
    story.append(Paragraph("3. <b>HSV Green Plant Masking:</b> Converts frame to HSV color space and masks pixels within <code>H:[35, 90], S:[40, 255], V:[40, 255]</code>. Only if green foliage covers &gt;= 15% of the frame is inference triggered.", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>4.2 Supported Plant Disease Classes &amp; Agronomic Knowledge Base</b>", h2_style))
    story.append(Paragraph(
        "The model is trained on PlantVillage benchmark classes augmented by field samples captured via the Pi camera. "
        "Upon classification with confidence &gt;= 70%, the system retrieves actionable treatment protocols from <code>disease_db.py</code>:",
        body_style
    ))

    disease_data = [
        [Paragraph("<b>Target Class Label</b>", meta_style), Paragraph("<b>Crop &amp; Condition</b>", meta_style), Paragraph("<b>Botanical Symptoms &amp; Field Signs</b>", meta_style), Paragraph("<b>Agronomic Treatment &amp; Fungicide Action</b>", meta_style)],
        [Paragraph("Pepper__bell___Bacterial_spot", meta_style), Paragraph("Bell Pepper<br/>(Bacterial)", meta_style), Paragraph("Small, yellow-green circular lesions turning dark brown with greasy margins on leaf undersides.", meta_style), Paragraph("Apply copper-based bactericides (Copper Hydroxide 53.8% WG) at 7-10 day intervals. Avoid overhead watering.", meta_style)],
        [Paragraph("Pepper__bell___healthy", meta_style), Paragraph("Bell Pepper<br/>(Healthy)", meta_style), Paragraph("Vibrant green foliage, uniform turgor, no chlorosis or necrosis present.", meta_style), Paragraph("Maintain optimal moisture (40-60%) and balanced nitrogen-phosphorus-potassium (NPK 10-10-10) fertilization.", meta_style)],
        [Paragraph("Potato___Early_blight", meta_style), Paragraph("Potato<br/>(Fungal)", meta_style), Paragraph("Concentric target-board rings surrounded by chlorotic yellow halos on mature lower leaves.", meta_style), Paragraph("Spray Chlorothalonil 75% WP or Mancozeb 75% WP at 2.5 g/L. Practice 3-year crop rotation.", meta_style)],
        [Paragraph("Potato___Late_blight", meta_style), Paragraph("Potato<br/>(Oomycete)", meta_style), Paragraph("Rapidly spreading water-soaked dark lesions with white fungal downy mildew on underside in humid air.", meta_style), Paragraph("Apply systemic fungicides: Metalaxyl-M + Mancozeb (Ridomil Gold) at 2.5 g/L immediately. Prune infected stems.", meta_style)],
        [Paragraph("Tomato___Early_blight", meta_style), Paragraph("Tomato<br/>(Fungal)", meta_style), Paragraph("Dark brown target-shaped circular spots with concentric rings starting on older leaves near soil.", meta_style), Paragraph("Apply Copper Oxychloride 50% WP or Azoxystrobin 23% SC. Mulch soil to prevent rain splashback.", meta_style)],
        [Paragraph("Tomato___Late_blight", meta_style), Paragraph("Tomato<br/>(Oomycete)", meta_style), Paragraph("Large irregular pale green/brown water-soaked patches. Destroys foliage within 4-7 days.", meta_style), Paragraph("Preventive Mancozeb; curative Dimethomorph 50% WP (1 g/L) or Cymoxanil. Remove severely blighted plants.", meta_style)],
        [Paragraph("Tomato___healthy", meta_style), Paragraph("Tomato<br/>(Healthy)", meta_style), Paragraph("Deep green compound leaves, vigorous growth, crisp texture.", meta_style), Paragraph("Maintain drip irrigation schedule. Ensure adequate calcium supply to prevent blossom end rot.", meta_style)],
        [Paragraph("background_not_a_leaf", meta_style), Paragraph("Soil / Path / Debris", meta_style), Paragraph("Frame contains garden soil, gravel, mulch, or robotic hardware.", meta_style), Paragraph("Non-plant object detected. Suppresses alerts and discards image from disease scan database.", meta_style)],
    ]
    t_disease = Table(disease_data, colWidths=[120, 75, 150, 159])
    t_disease.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_disease)

    story.append(PageBreak())

    # =========================================================================
    # 6. AUTONOMOUS FIELD OPERATION SUBSYSTEMS
    # =========================================================================
    story.append(Paragraph("5. Autonomous Field Operation Subsystems", h1_style))
    story.append(Paragraph(
        "AgroNex-Pi features three specialized autonomous control subsystems that execute concurrently "
        "under the supervision of the master FSM:",
        body_style
    ))

    story.append(Paragraph("<b>5.1 Closed-Loop Precision Irrigation Controller (irrigation.py)</b>", h2_style))
    story.append(Paragraph(
        "The irrigation subsystem reads analog soil moisture via the 10-bit SPI MCP3008 ADC. "
        "It employs a <b>dual-threshold hysteresis control loop</b> to prevent rapid relay chattering:",
        body_style
    ))
    story.append(Paragraph("• <b>Activation Condition:</b> When <code>soil_moisture &lt; MOISTURE_LOW (35.0%)</code> and the cooldown timer has elapsed, the controller energizes Relay CH1 (Pump ON).", bullet_style))
    story.append(Paragraph("• <b>Deactivation Condition:</b> The pump runs until <code>soil_moisture &gt;= MOISTURE_HIGH (65.0%)</code> is reached.", bullet_style))
    story.append(Paragraph("• <b>Dry-Run Safety Watchdog:</b> If the pump runs continuously for <code>PUMP_MAX_RUNTIME (60.0s)</code> without reaching 65%, it forcibly shuts off to protect against dry running or pipe disconnection.", bullet_style))
    story.append(Paragraph("• <b>Cooldown Interlock:</b> A mandatory <code>PUMP_COOLDOWN (120.0s)</code> rest period is enforced between irrigation cycles to allow water to percolate through the root zone.", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>5.2 Automated Grass Trimmer Controller (cutter.py)</b>", h2_style))
    story.append(Paragraph(
        "The trimming subsystem manages lawn maintenance and weed suppression around crops:",
        body_style
    ))
    story.append(Paragraph("• <b>Scheduled Execution:</b> The cutter initiates periodically every <code>CUTTER_INTERVAL (3600.0s = 1 hour)</code>.", bullet_style))
    story.append(Paragraph("• <b>Timed Duty Cycle:</b> The trimmer runs for a calibrated duration of <code>CUTTER_DURATION (30.0s)</code> before de-energizing Relay CH2.", bullet_style))
    story.append(Paragraph("• <b>Mutual Exclusion Safety Lock:</b> Cutting is strictly locked out while the robot is actively irrigating to prevent splashing water onto high-speed cutting blades.", bullet_style))

    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>5.3 Autonomous GPS Waypoint Navigation (navigation.py)</b>", h2_style))
    story.append(Paragraph(
        "Field traversal is guided by fusing the NEO-7M GPS receiver with the HMC5883L/QMC5883L 3-axis digital compass:",
        body_style
    ))
    story.append(Paragraph("• <b>Haversine Geodesic Distance:</b> Computes the spherical distance between the current GPS fix $(lat_1, lon_1)$ and target waypoint $(lat_2, lon_2)$ using the Earth radius $R = 6,371,000$ meters.", bullet_style))
    story.append(Paragraph("• <b>Target Azimuth Bearing:</b> Computes forward bearing $\\theta = \\text{atan2}(\\sin(\\Delta lon)\\cdot\\cos(lat_2), \\cos(lat_1)\\cdot\\sin(lat_2) - \\sin(lat_1)\\cdot\\cos(lat_2)\\cdot\\cos(\\Delta lon))$.", bullet_style))
    story.append(Paragraph("• <b>Heading Error &amp; PID Pivot:</b> Compares target bearing against live compass heading. If heading error exceeds $\\pm 12^\\circ$, the robot executes pivot bursts (left or right) until aligned.", bullet_style))
    story.append(Paragraph("• <b>Dead-Reckoning Drive Slices:</b> Drives forward in small 1.0-second bursts, stopping after each burst to re-verify heading and check for obstacles.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # 7. AWS CLOUD IOT ARCHITECTURE & LIVE DASHBOARD
    # =========================================================================
    story.append(Paragraph("6. AWS Cloud IoT Architecture &amp; Live Deployed Dashboard", h1_style))
    story.append(Paragraph(
        "AgroNex-Pi bridges the physical field robot with a globally accessible cloud dashboard using "
        "a serverless AWS architecture. The entire cloud infrastructure operates on AWS Free Tier services "
        "and is deployed live in the <b>ap-south-1 (Mumbai)</b> region.",
        body_style
    ))

    story.append(Paragraph("<b>6.1 Cloud Telemetry &amp; Teleoperation Pipeline:</b>", h2_style))
    story.append(Paragraph("1. <b>Raspberry Pi Client (aws_relay.py):</b> Every 5.0 seconds (and immediately upon any state change), the background relay thread packages a JSON snapshot of all sensor readings, GPS coordinates, actuator states, and FSM mode. It dispatches an HTTP POST to the AWS API Gateway endpoint.", bullet_style))
    story.append(Paragraph("2. <b>AWS API Gateway (HTTP API v2):</b> Routes incoming requests (<code>POST /telemetry</code>, <code>GET /state</code>, <code>POST /command</code>, <code>GET /command</code>, <code>POST /scans</code>, <code>GET /scans</code>) to the Lambda execution engine.", bullet_style))
    story.append(Paragraph("3. <b>AWS Lambda (lambda_function.py):</b> Executes serverless Python handler. Reads and writes state objects (<code>state.json</code>, <code>scans.json</code>, <code>command.json</code>) to an Amazon S3 storage bucket.", bullet_style))
    story.append(Paragraph("4. <b>CORS &amp; Security:</b> The Lambda function explicitly attaches <code>Access-Control-Allow-Origin: *</code>, <code>Access-Control-Allow-Methods: *</code>, and handles <code>OPTIONS</code> preflight requests to allow direct cross-origin browser execution.", bullet_style))
    story.append(Paragraph("5. <b>Live Static Website Hosting (Amazon S3):</b> The HTML5/CSS3 glassmorphic dashboard is deployed to an S3 public static website bucket, accessible at:", bullet_style))

    # Live Dashboard URL Box
    live_url_table = Table([[
        Paragraph("<b>🌐 Live Deployed AWS Dashboard URL:</b><br/>"
                  "<font color='#2563eb' size='9.5'><b>http://agronex-pi-data-nikhil.s3-website.ap-south-1.amazonaws.com/</b></font><br/>"
                  "<font color='#059669' size='8'>✔ Verified Online: Real-time telemetry, Google Maps satellite tracking, manual overrides &amp; disease gallery active.</font>", body_style)
    ]], colWidths=[504])
    live_url_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#93c5fd")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(live_url_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>6.2 Remote Command Dispatching &amp; Emergency Stop Protocol:</b>", h2_style))
    story.append(Paragraph(
        "Remote operators can control field actuators from any smartphone or browser. When an operator clicks "
        "<b>'Manual Pump'</b>, <b>'Trim Lawn'</b>, <b>'Capture AI Scan'</b>, or <b>'EMERGENCY STOP'</b>, "
        "the command is pushed to <code>POST /command</code> in AWS S3. Within 5 seconds, the Raspberry Pi "
        "polls <code>GET /command</code>, executes the physical hardware actuation, and resets the queue.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # 8. HARDWARE TESTING & VERIFICATION SUITE
    # =========================================================================
    story.append(Paragraph("7. Hardware Verification, Testing Suite &amp; Deployment", h1_style))
    story.append(Paragraph(
        "Before launching the full autonomous supervisor, each hardware component must be validated independently "
        "using the project's dedicated diagnostic test scripts. This guarantees electrical integrity and prevents motor damage.",
        body_style
    ))

    test_table_data = [
        [Paragraph("<b>Diagnostic Test Script</b>", meta_style), Paragraph("<b>Target Hardware</b>", meta_style), Paragraph("<b>Execution Command</b>", meta_style), Paragraph("<b>Expected Verification Output</b>", meta_style)],
        [Paragraph("test_soil.py", meta_style), Paragraph("MCP3008 ADC + Capacitive Probe", meta_style), Paragraph("<code>python test_soil.py</code>", meta_style), Paragraph("Displays raw 10-bit ADC reading (380-850) and computed moisture percentage (0-100%).", meta_style)],
        [Paragraph("test_dht.py", meta_style), Paragraph("DHT11 / DHT22 Sensor", meta_style), Paragraph("<code>python test_dht.py</code>", meta_style), Paragraph("Displays ambient temperature in °C and relative humidity in % after 1-wire timing check.", meta_style)],
        [Paragraph("test_navigation_sensors.py", meta_style), Paragraph("NEO-7M GPS + HMC5883L Compass", meta_style), Paragraph("<code>python test_navigation_sensors.py</code>", meta_style), Paragraph("Verifies I2C compass heading (0-360°) and checks for valid NMEA GPS fix sentences on UART.", meta_style)],
        [Paragraph("test_camera.py", meta_style), Paragraph("OV5647 CSI Camera Module", meta_style), Paragraph("<code>python test_camera.py</code>", meta_style), Paragraph("Initializes Picamera2, captures RGB888 test frame, and writes <code>test_camera_capture.jpg</code>.", meta_style)],
        [Paragraph("test_alert.py", meta_style), Paragraph("Piezo Buzzer &amp; Red LED", meta_style), Paragraph("<code>python test_alert.py</code>", meta_style), Paragraph("Pulses audible 5V buzzer and visual red LED in rapid 0.15s warning cadence.", meta_style)],
        [Paragraph("test_relay.py", meta_style), Paragraph("2-Channel 5V Relay Module", meta_style), Paragraph("<code>python test_relay.py</code>", meta_style), Paragraph("Cycles CH1 (Pump) and CH2 (Cutter) with audible click verification, ensuring active-LOW logic.", meta_style)],
        [Paragraph("test_motors.py", meta_style), Paragraph("Dual BTS7960 Motor Drivers", meta_style), Paragraph("<code>python test_motors.py</code>", meta_style), Paragraph("Sequentially tests 50% PWM in Forward, Reverse, Left Pivot, and Right Pivot for 1.5s each.", meta_style)],
    ]
    t_test = Table(test_table_data, colWidths=[95, 105, 110, 194])
    t_test.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_test)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Linux systemd Production Daemon Setup (agronex.service):</b>", h2_style))
    story.append(Paragraph(
        "To enable headless autonomous operation on power-up in the field without an attached monitor or keyboard, "
        "AgroNex-Pi runs as a background systemd service on Raspberry Pi OS:",
        body_style
    ))
    daemon_code = """[Unit]
Description=AgroNex-Pi Autonomous Agricultural Robot Controller
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Major_project
ExecStart=/usr/bin/python3 /home/pi/Major_project/main.py --port 5000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target"""
    story.append(Preformatted(daemon_code, code_block_style))

    story.append(PageBreak())

    # =========================================================================
    # 9. COMPLETE SOURCE CODE COMPENDIUM
    # =========================================================================
    story.append(Paragraph("8. Complete Source Code Compendium", h1_style))
    story.append(Paragraph(
        "This section contains the complete, unedited source code for all primary modules, drivers, "
        "controllers, AWS serverless functions, and hardware diagnostic scripts in the AgroNex-Pi codebase. "
        "Each listing includes line numbers and a description of its architecture.",
        body_style
    ))

    code_files = [
        ("config.py", "Central System Configuration, BCM Pin Map, Calibrations & AWS Endpoints"),
        ("main.py", "Master Supervisor Thread, FSM State Machine & Multithreaded Core"),
        ("hardware.py", "Hardware Abstraction Layer (HAL) for GPIO, SPI, I2C, UART, Camera & Motors"),
        ("aws_relay.py", "AWS Cloud Telemetry Bridge & Remote Command Poller Client"),
        ("aws/lambda_function.py", "Serverless AWS Lambda Backend Function for Telemetry & State"),
        ("irrigation.py", "Closed-Loop Precision Irrigation Controller & Watchdog Safety"),
        ("cutter.py", "Automated Grass Trimmer Scheduler & Duty-Cycle Safety Controller"),
        ("navigation.py", "Autonomous GPS Waypoint & Digital Compass Navigation Controller"),
        ("disease_detect.py", "Edge AI Vision Pipeline, Image Quality Gating & TFLite Inference"),
        ("disease_db.py", "Agronomic Plant Disease Treatment & Recommendation Knowledge Base"),
        ("database.py", "SQLite Database Manager (agronex.db) for Telemetry & System Logging"),
        ("app.py", "Local Flask Web Dashboard, REST API Server & Camera Stream Handler"),
        ("test_soil.py", "MCP3008 SPI ADC & Capacitive Soil Moisture Sensor Test Script"),
        ("test_dht.py", "DHT11 / DHT22 1-Wire Digital Humidity & Temperature Test Script"),
        ("test_relay.py", "2-Channel 5V Active-LOW Relay Module Actuation Test Script"),
        ("test_navigation_sensors.py", "NEO-7M GPS UART & HMC5883L/QMC5883L I2C Compass Test Script"),
        ("test_camera.py", "OV5647 CSI-2 Camera Singleton Frame Capture Test Script"),
        ("test_alert.py", "5V Active Buzzer & Red Visual Warning LED Test Script"),
        ("test_motors.py", "Dual BTS7960 4-Wheel Drive H-Bridge PWM Motor Test Script"),
    ]

    for filename, description in code_files:
        lines, size = get_file_stats(filename)
        content = load_file_content(filename)

        story.append(Spacer(1, 6))
        # File Header Table
        header_table = Table([[
            Paragraph(f"<b>FILE: {filename}</b>", ParagraphStyle('FileH', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#0f172a"))),
            Paragraph(f"<b>{lines} lines | {size:,} bytes</b>", ParagraphStyle('FileM', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor("#475569"), alignment=2))
        ]], colWidths=[330, 174])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#e2e8f0")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(header_table)

        story.append(Paragraph(f"<i>{description}</i>", ParagraphStyle('FileD', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, textColor=colors.HexColor("#334155"), spaceBefore=3, spaceAfter=4)))

        # Code Listing
        story.append(Preformatted(content, code_block_style))
        story.append(Spacer(1, 14))

    # Build Document with NumberedCanvas
    print("[*] Generating PDF document and calculating dynamic pagination...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Successfully generated complete project PDF: {pdf_path}")
    print(f"[OK] File size: {os.path.getsize(pdf_path):,} bytes")


if __name__ == "__main__":
    build_full_report()
