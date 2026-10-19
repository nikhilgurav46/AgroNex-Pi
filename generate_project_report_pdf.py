import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image as RLImage
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render total page count."""
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
            # Skip header/footer on cover page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header
        self.drawString(54, 750, "AgroNex-Pi: Autonomous Smart Agricultural Garden Robot — Final Year Major Project")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 744, 558, 744)

        # Footer
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Confidential & Academic Engineering Documentation")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def build_pdf(filename="AgroNex_Pi_Complete_Major_Project_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0f172a") # Dark Slate
    accent_blue = colors.HexColor("#2563eb")   # Royal Blue
    accent_green = colors.HexColor("#059669")  # Emerald Green
    accent_amber = colors.HexColor("#d97706")  # Amber
    dark_gray = colors.HexColor("#334155")
    light_bg = colors.HexColor("#f8fafc")

    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=primary_color,
        alignment=0,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=accent_blue,
        spaceAfter=25
    )

    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=14,
        textColor=dark_gray
    )

    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=accent_green,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=accent_blue,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_gray,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=dark_gray,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderColor=colors.HexColor("#e2e8f0"),
        borderWidth=0.5,
        borderPadding=5,
        spaceAfter=6
    )

    callout_style = ParagraphStyle(
        'CalloutStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1e293b"),
        backColor=colors.HexColor("#ecfdf5"),
        borderColor=colors.HexColor("#10b981"),
        borderWidth=1,
        borderPadding=6,
        spaceAfter=8
    )

    warning_callout = ParagraphStyle(
        'WarningCallout',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#991b1b"),
        backColor=colors.HexColor("#fef2f2"),
        borderColor=colors.HexColor("#ef4444"),
        borderWidth=1,
        borderPadding=6,
        spaceAfter=8
    )

    story = []

    # ==========================================
    # COVER PAGE
    # ==========================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("FINAL YEAR MAJOR PROJECT REPORT", ParagraphStyle('SubHeader', fontName='Helvetica-Bold', fontSize=11, textColor=accent_green, leading=14, spaceAfter=8)))
    story.append(Paragraph("AgroNex-Pi: Autonomous Smart Agricultural Garden Robot", title_style))
    story.append(Paragraph("A Raspberry Pi Rover Integrating Edge AI, GPS-Compass Waypoint Navigation, Automated Irrigation and Grass Cutting", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=3, color=accent_blue, spaceBefore=5, spaceAfter=20))

    meta_text = """
    <b>Platform:</b> Raspberry Pi 4B (4GB RAM, Quad-Core Cortex-A72 @ 1.5GHz)<br/>
    <b>Drive System:</b> 4-Wheel Drive (4x 12V 10A DC Motors, 2x BTS7960 drivers)<br/>
    <b>Edge AI Subsystem:</b> TensorFlow Lite MobileNetV2 (PlantVillage Dataset Classification)<br/>
    <b>Software Stack:</b> Python 3, Flask REST API, SQLite WAL Mode, Vanilla Modern CSS UI<br/>
    <b>Field Deployments:</b> GPS waypoint patrol, soil-moisture hysteresis, grass trimming<br/>
    <b>Author / Engineering Team:</b> Final Year Major Project Group
    """
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 30))

    exec_summary = """
    <b>EXECUTIVE SUMMARY & ENGINEERING SCOPE:</b><br/>
    AgroNex-Pi addresses critical labor shortages and water inefficiency in modern precision horticulture. 
    The Raspberry Pi 4B supervises GPS-compass waypoint navigation, monitors capacitive soil moisture 
    to trigger on-demand pump irrigation, schedules mechanical grass trimming, conducts optical disease scans 
    via a quality-gated convolutional neural network. This report provides an exhaustive breakdown of the hardware matrix, 
    codebase architecture, failure mode mitigation strategies, and practical execution procedures.
    """
    story.append(Paragraph(exec_summary, callout_style))
    story.append(PageBreak())

    # ==========================================
    # SECTION 1: ARCHITECTURAL DECOMPOSITION
    # ==========================================
    story.append(Paragraph("1. System Architecture: Raspberry Pi Hardware Supervisor", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    
    arch_intro = """
    The Raspberry Pi 4B supervises sensing, safety, edge inference, GPS-compass navigation and motor commands. 
    The system is organized as software layers with explicit safety interlocks and hardware sensor checks:
    """
    story.append(Paragraph(arch_intro, body_style))

    story.append(Paragraph("<b>Tier 1: Brain 1 — Raspberry Pi 4B (High-Level Intelligence & Perception)</b>", h2_style))
    story.append(Paragraph("• <b>Role:</b> Decides <i>WHERE</i> the robot should go and <i>WHAT</i> it observes.", bullet_style))
    story.append(Paragraph("• <b>Key Tasks:</b> OV5647 CSI vision acquisition, MobileNetV2 disease inference, GPS waypoint dispatch, HMC5883L heading correction, SQLite event persistence, and Flask HTTP/REST telemetry.", bullet_style))

    story.append(Paragraph("<b>Tier 2: Navigation and Drive Layer</b>", h2_style))
    story.append(Paragraph("• <b>Role:</b> Uses NEO-7M GPS position and HMC5883L heading to guide short, stop-and-recheck drive bursts.", bullet_style))
    story.append(Paragraph("• <b>Key Tasks:</b> PWM control of two BTS7960 H-bridges, emergency stop, and safe refusal to move without a recent fix and configured waypoint.", bullet_style))

    story.append(Paragraph("<b>Tier 3: Brain 3 — Distributed Sensor & Actuator Matrix</b>", h2_style))
    story.append(Paragraph("• <b>Sensors:</b> Capacitive Soil Moisture Sensor v1.2 (via MCP3008 SPI ADC), DHT11/22, OV5647 CSI camera, NEO-7M GPS and HMC5883L compass.", bullet_style))
    story.append(Paragraph("• <b>Actuators:</b> 4x 12V 300 RPM high-torque DC motors, 12V diaphragm water pump (via Relay CH1), 12V high-speed grass trimmer motor (via Relay CH2), active piezo buzzer, high-luminance LED status indicator.", bullet_style))

    # Architecture Table
    arch_data = [
        ["Subsystem", "Processor / Chip", "Communication", "Primary Function"],
        ["Perception & Vision", "Raspberry Pi 4B (4GB)", "CSI-2 / MIPI Bus", "OV5647 capture and TFLite inference"],
        ["Mission Supervisor", "Raspberry Pi 4B", "Internal Threads / IPC", "FSM Supervisor, Watchdog, SQLite WAL logging"],
        ["Telemetry Dashboard", "Flask WSGI Server", "HTTP / WebSockets", "Offline-first UI, REST API, manual overrides"],
        ["Navigation & Drive", "Pi GPIO + NEO-7M + HMC5883L", "UART / I2C / PWM", "GPS waypoint and compass-heading control"],
        ["Analog Acquisition", "MCP3008 10-bit ADC", "SPI (Bus 0, CE0)", "Translates capacitive analog soil probe to % moisture"],
        ["Power Switching", "2-Channel Relay Module", "Active-LOW GPIO", "Galvanic isolation for 12V water pump and grass cutter"]
    ]
    t_arch = Table(arch_data, colWidths=[110, 115, 105, 174])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('BACKGROUND', (0,1), (-1,-1), light_bg),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [light_bg, colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 7.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(Spacer(1, 4))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    # Embed Process & Hardware Block Diagram
    story.append(PageBreak())
    story.append(Paragraph("System Process & Hardware Interconnect Schematic", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    diagram_path = os.path.join(os.path.dirname(__file__), "diagrams", "system_block_diagram.jpg")
    if os.path.exists(diagram_path):
        story.append(RLImage(diagram_path, width=500, height=280))
        story.append(Spacer(1, 4))
        caption_style = ParagraphStyle('FigCaption', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=11, textColor=colors.HexColor("#64748b"), alignment=1)
        story.append(Paragraph("<b>Figure 1:</b> AgroNex-Pi End-to-End Hardware Interconnection & Process Flow Block Diagram.<br/>Illustrates 12V motor rails, regulated logic rail, GPS/compass sensor buses, and dual BTS7960 4WD control.", caption_style))
        story.append(Spacer(1, 14))

    # Embed Formal Operational Flowchart (Figure 2)
    story.append(PageBreak())
    story.append(Paragraph("Formal Operational System Flowchart", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    flowchart_path = os.path.join(os.path.dirname(__file__), "diagrams", "project_flowchart.jpg")
    if os.path.exists(flowchart_path):
        story.append(RLImage(flowchart_path, width=280, height=490))
        story.append(Spacer(1, 4))
        caption_style = ParagraphStyle('FigCaption2', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, leading=11, textColor=colors.HexColor("#64748b"), alignment=1)
        story.append(Paragraph("<b>Figure 2:</b> AgroNex-Pi Formal System Operational Flowchart.<br/>Utilizes standard ISO shapes: Terminator (Ovals), Process (Rectangles), Decisions (Diamonds with conditional Yes/No branches), I/O (Parallelograms), and Initialization (Hexagons).", caption_style))
        story.append(Spacer(1, 14))

    # ==========================================
    # SECTION 2: HARDWARE & ELECTRICAL DESIGN
    # ==========================================
    story.append(Paragraph("2. Hardware Wiring, GPS Navigation & Power Distribution", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))

    hw_text = """
    Reliable field operation demands rigorous electrical isolation. Inductive kickback from 12V DC motors, 
    relays, and water pumps generates extreme EMI and voltage dips capable of causing Raspberry Pi brownouts 
    (triggering the dreaded under-voltage throttling warning and SD card corruption).
    """
    story.append(Paragraph(hw_text, body_style))

    story.append(Paragraph("<b>A. Dual-Rail Isolated Power Distribution Architecture</b>", h2_style))
    story.append(Paragraph("• <b>High-Current Motor Rail (12V Battery / Li-Ion Pack):</b> Feeds both BTS7960 motor drivers and the 12V trimmer motor through correctly sized fuses. Design for motor stall current and provide driver cooling.", bullet_style))
    story.append(Paragraph("• <b>Logic Rail (Clean 5.1V / 3A via High-Efficiency Buck Converter):</b> Powers the Raspberry Pi 4B through USB-C or GPIO Header Pins 2 & 4. GPS/compass power and logic levels must match their module specifications.", bullet_style))
    story.append(Paragraph("• <b>Star Grounding:</b> High-power motor ground and sensitive digital logic grounds join at a single central star point to eliminate ground loops and return-current noise.", bullet_style))

    story.append(Paragraph("<b>B. GPS and Compass Navigation</b>", h2_style))
    story.append(Paragraph("The NEO-7M supplies global location by UART and the HMC5883L supplies a magnetic heading by I²C. The rover compares its bearing to each configured waypoint, pivots in a short burst when outside the heading tolerance, then advances for a short burst and re-checks. GPS/compass navigation does not provide obstacle detection or centimetre-level positioning; a safety observer remains mandatory.", body_style))

    story.append(Paragraph("<b>C. Complete BCM GPIO Pinout Matrix (Standardized in config.py)</b>", h2_style))
    pin_data = [
        ["Pin (BCM)", "Physical Pin", "Target Device", "Signal Type", "Safety Constraint"],
        ["GPIO 4", "Pin 7", "DHT11/22 Sensor", "1-Wire Bidirectional", "Requires 10k pull-up resistor to 3.3V"],
        ["GPIO 17", "Pin 11", "Relay CH1 (Water Pump)", "Digital Output (Active LOW)", "Initialized HIGH at boot to prevent pump turn-on glitch"],
        ["GPIO 27", "Pin 13", "Relay CH2 (Grass Cutter)", "Digital Output (Active LOW)", "Initialized HIGH; interlocked with drive motors"],
        ["GPIO 22", "Pin 15", "Active 5V Buzzer", "Digital Output", "Driven via NPN transistor / driver circuit"],
        ["GPIO 23", "Pin 16", "Red Alert LED", "Digital Output", "Requires 220 Ohm series current-limiting resistor"],
        ["GPIO 10", "Pin 19", "MCP3008 ADC DIN", "SPI0 MOSI", "Transfers command/channel select bits to ADC"],
        ["GPIO 9", "Pin 21", "MCP3008 ADC DOUT", "SPI0 MISO", "Receives 10-bit digitized sensor reading"],
        ["GPIO 11", "Pin 23", "MCP3008 ADC CLK", "SPI0 SCLK", "SPI synchronous clock line (up to 3.6MHz at 5V)"],
        ["GPIO 8", "Pin 24", "MCP3008 ADC CS", "SPI0 CE0", "Protected exclusively for SPI; NEVER assign to motors"],
        ["GPIO 5 / 6", "Pin 29 / 31", "Left BTS7960", "RPWM / LPWM", "Controls front-left and rear-left motors"],
        ["GPIO 13 / 19", "Pin 33 / 35", "Right BTS7960", "RPWM / LPWM", "Controls front-right and rear-right motors"],
        ["GPIO 14 / 15", "Pin 8 / 10", "NEO-7M", "UART", "GPS TX connects to Pi RX"],
        ["GPIO 2 / 3", "Pin 3 / 5", "HMC5883L", "I²C", "Compass must be calibrated away from motors"]
    ]
    t_pin = Table(pin_data, colWidths=[70, 75, 120, 115, 124])
    t_pin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 7.5),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('BACKGROUND', (0,1), (-1,-1), light_bg),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [light_bg, colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_pin)
    story.append(PageBreak())

    # ==========================================
    # SECTION 3: CODEBASE WALKTHROUGH
    # ==========================================
    story.append(Paragraph("3. Deep Codebase Walkthrough & Module Breakdown", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))

    story.append(Paragraph("<b>3.1 Configuration & Hardware Abstraction (config.py & hardware.py)</b>", h2_style))
    story.append(Paragraph("• <b>Thread-Safe SPI Locking:</b> Capacitive soil moisture reading requires polling the MCP3008 ADC over SPI. Because web requests (Flask) and autonomous control loops execute concurrently, <code>hardware.py</code> wraps all SPI transactions with a Python <code>threading.Lock()</code>, completely eliminating SPI bus collisions.", bullet_style))
    story.append(Paragraph("• <b>Active-LOW Relay Safety Glitch Prevention:</b> Many 5V relay boards trigger active-LOW. In naive code, setting pin direction defaults to LOW, briefly energizing the water pump or cutter on Pi reboot. <code>hardware.py</code> explicitly writes <code>GPIO.output(pin, GPIO.HIGH)</code> BEFORE switching direction to <code>GPIO.OUT</code>, eliminating dangerous power-on pulses.", bullet_style))
    story.append(Paragraph("• <b>Picamera2 Singleton Instance:</b> On Raspberry Pi 4B running Bullseye/Bookworm, camera sensors must not be re-opened repeatedly. The <code>Camera</code> class implements a thread-safe singleton that starts the sensor once at boot, captures frames into NumPy buffers, and releases cleanly on shutdown.", bullet_style))

    story.append(Paragraph("<b>3.2 Autonomous Subsystem Controllers (irrigation.py, cutter.py, navigation.py)</b>", h2_style))
    story.append(Paragraph("• <b>Hysteresis Irrigation Logic:</b> <code>irrigation.py</code> prevents pump chattering. Irrigation begins when moisture drops below <b>35.0%</b> and continues until it reaches <b>65.0%</b>. It enforces a strict <b>60-second maximum pump runtime</b> (preventing motor burnout if the reservoir runs dry) followed by a mandatory <b>120-second cooldown</b>.", bullet_style))
    story.append(Paragraph("• <b>Probe Drag Mitigation:</b> Running irrigation while driving drags soil probes through earth, causing mechanical damage. <code>irrigation.py</code> halts all 4WD drive motors during moisture sampling and water delivery.", bullet_style))
    story.append(Paragraph("• <b>Mutual Exclusion Trimming:</b> <code>cutter.py</code> operates the high-speed blade motor for 30 seconds at scheduled intervals. To avoid massive simultaneous current surges that drop battery voltage, drive motors are halted during the grass trim sequence.", bullet_style))
    story.append(Paragraph("• <b>Dead-Reckoning & Obstacle Evasion:</b> <code>navigation.py</code> executes skid-steering patrol paths. When distance rangers detect obstacles within the safety envelope, the routine pauses, initiates pivot turns toward clear headings, and re-engages forward waypoints.", bullet_style))

    story.append(Paragraph("<b>3.3 Edge AI Vision Pipeline (disease_detect.py & disease_db.py)</b>", h2_style))
    story.append(Paragraph("• <b>Model Architecture:</b> Uses a MobileNetV2 architecture fine-tuned on the PlantVillage dataset (detecting Healthy, Early Blight, Late Blight across Tomato and Potato crops). Quantized to 8-bit dynamic range for ultra-low latency (~40-70ms inference on Pi 4B).", bullet_style))
    story.append(Paragraph("• <b>Image Quality Gating:</b> Outdoor robotics face motion blur and harsh sun. Before running inference, frames pass two mathematical filters: <i>Laplacian Variance Gating</i> (rejects blurred frames with variance < 50.0) and <i>Luminance Gating</i> (rejects extreme under/over-exposure outside 35-225 mean brightness).", bullet_style))
    story.append(Paragraph("• <b>Softmax Confidence Thresholding:</b> Classifications are accepted only if confidence >= <b>0.70</b>. Predictions below 70% are logged as uncertain to prevent erroneous pesticide recommendations.", bullet_style))
    story.append(Paragraph("• <b>Agronomic Knowledge Base:</b> <code>disease_db.py</code> correlates class IDs with agricultural descriptions, pathogen names, and specific chemical (Mancozeb, Chlorothalonil) or organic (copper fungicide, neem extract) remedies.", bullet_style))

    story.append(Paragraph("<b>3.4 Web Server & Finite State Machine Supervisor (app.py, dashboard.html, main.py)</b>", h2_style))
    story.append(Paragraph("• <b>Decoupled Telemetry Cache:</b> <code>app.py</code> never queries physical sensors inside Flask request threads. Instead, the supervisor loop writes sensor readings into a thread-safe global cache <code>_telemetry_cache</code>. The web UI polls this cache, guaranteeing <b>sub-millisecond API response times</b> without hardware bus contention.", bullet_style))
    story.append(Paragraph("• <b>Zero-CDN Dark Mode Dashboard:</b> <code>dashboard.html</code> runs completely offline on the Pi in rural fields without internet access. Built with pure Vanilla CSS/JS, featuring live SVG moisture history charts, color-coded health badges, and an instant Emergency Stop button.", bullet_style))
    story.append(Paragraph("• <b>Watchdog Thread & Signal Traps:</b> <code>main.py</code> runs a dedicated watchdog monitoring the control loop heartbeat. If the loop hangs for > 3x poll intervals, the watchdog trips, de-energizing all actuators immediately. POSIX <code>SIGINT</code> and <code>SIGTERM</code> signals are trapped to guarantee safe hardware de-allocation on system shutdown.", bullet_style))
    story.append(PageBreak())

    # ==========================================
    # SECTION 4: FAILURE MODES & PREVENTION MATRIX
    # ==========================================
    story.append(Paragraph("4. Comprehensive Failure Mode & Effects Analysis (FMEA)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))

    fmea_intro = """
    A major project fails not because the primary code doesn't work, but because real-world physics, 
    electrical noise, and environmental factors are overlooked. Below is the comprehensive mitigation matrix 
    implemented in AgroNex-Pi:
    """
    story.append(Paragraph(fmea_intro, body_style))

    fmea_data = [
        ["Failure Mode", "Root Cause", "Hazard to System", "Engineered Code / Hardware Solution"],
        ["Pi Brownout / Crash", "Simultaneous motor & pump start dips 12V battery", "Raspberry Pi restarts, corrupts SD card filesystem", "Dual-rail power isolation with MP1584 buck converter; software mutual exclusion ensures drive motors halt before pump/cutter relays engage."],
        ["Motor Driver Overheat", "High current from two 12V motors per BTS7960 side", "Driver overheats or rover stalls", "Fuse for stall current, provide cooling, use correctly sized wiring, and keep PWM duty conservative."],
        ["GPS / Compass Error", "GPS multipath, weak sky view, motor magnetic interference", "Waypoint error or incorrect heading", "Require recent GPS fix, mount compass away from motors, calibrate heading, and use a safety observer."],
        ["Pump Burnout (Dry Run)", "Water tank empties while soil is still dry", "Diaphragm pump overheats and melts impeller", "Strict 60-second pump safety timeout in irrigation.py; capacitive tank level float switch triggers auto-return to water station."],
        ["False Disease Scans", "Rover vibration creates camera blur; harsh direct sunlight", "Incorrect disease diagnosis, improper spraying alert", "Two-stage image gate in disease_detect.py: Laplacian variance (>50.0) filters blur; mean luminance (35-225) filters harsh glare; 70% softmax gate."],
        ["SPI Bus Contention", "Web dashboard and control loop access ADC at same time", "Corrupted SPI frames, kernel driver crash, system freeze", "Thread synchronization: hardware.py encapsulates all ADC SPI transactions within a global threading.Lock()."],
        ["Relay Power-On Pulse", "Active-LOW relays trigger when Pi GPIO boot pins float", "Water pump sprays unintentionally when rover boots up", "hardware.py forces GPIO output to HIGH BEFORE setting pin direction to OUT, maintaining de-energized relay state during boot."],
        ["Software Loop Freeze", "Blocking network call or sensor read hangs control loop", "Robot continues driving blindly into walls/crops", "Dedicated hardware Watchdog thread checks supervisor heartbeat every second; trips fail-safe shutdown if heartbeat stops for >90s."]
    ]

    t_fmea = Table(fmea_data, colWidths=[90, 100, 110, 204])
    t_fmea.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 7.5),
        ('BOTTOMPADDING', (0,0), (-1,0), 4),
        ('BACKGROUND', (0,1), (-1,-1), light_bg),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [light_bg, colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 6.8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_fmea)
    story.append(Spacer(1, 10))

    # ==========================================
    # SECTION 5: STEP-BY-STEP EXECUTION GUIDE
    # ==========================================
    story.append(Paragraph("5. Step-by-Step Copy-Paste Execution & Testing Guide", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))

    exec_intro = """
    Follow this exact chronological sequence to set up, test, train, and execute the AgroNex-Pi software suite 
    either in simulation mode on a PC or live on the physical Raspberry Pi 4B:
    """
    story.append(Paragraph(exec_intro, body_style))

    story.append(Paragraph("<b>Step 1: Environment Setup & Python Dependencies</b>", h2_style))
    cmd_env = """# Create and activate Python virtual environment
python -m venv venv
# On Windows:
.\\venv\\Scripts\\activate
# On Raspberry Pi (Linux):
source venv/bin/activate

# Install essential dependencies
pip install flask numpy pillow opencv-python pypdf reportlab
# On Raspberry Pi (install hardware packages):
pip install spidev RPi.GPIO picamera2"""
    story.append(Paragraph(cmd_env.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))

    story.append(Paragraph("<b>Step 2: Kaggle PlantVillage Dataset Extraction & Model Training</b>", h2_style))
    cmd_data = """# Unzip pre-downloaded dataset archive (~689 MB)
python -c "import zipfile, os; os.makedirs('plantvillage_dataset', exist_ok=True); zipfile.ZipFile('plantdisease.zip').extractall('plantvillage_dataset'); print('Extracted successfully!')"

# Run transfer learning on MobileNetV2 (generates plant_model.tflite & labels.txt in ./models/)
python train_plant_disease_model.py --epochs 10 --batch_size 32"""
    story.append(Paragraph(cmd_data.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))

    story.append(Paragraph("<b>Step 3: Component-by-Component Hardware Test Suite (§10)</b>", h2_style))
    cmd_tests = """# 1. Test MCP3008 SPI ADC & Capacitive Soil Probe:
python test_soil.py                 # (Add --simulate on PC)

# 2. Test DHT11/22 1-Wire Temperature & Humidity Sensor:
python test_dht.py                  # (Add --simulate on PC)

# 3. Test Active-LOW 5V Relays (Water Pump & Cutter):
python test_relay.py                # (Pulses CH1 and CH2 for 1.5s)

# 4. Test Piezo Buzzer and Visual Red Alert LED:
python test_alert.py                # (Pulses warning sequence)

# 5. Test Picamera2 Singleton Capture:
python test_camera.py               # (Saves test_camera_capture.jpg)

# 6. Test dual BTS7960 4WD chassis motors (Forward, Reverse, Left, Right Pivot):
python test_motors.py               # (Runs 50% PWM test on all 4 directions)"""
    story.append(Paragraph(cmd_tests.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))

    story.append(Paragraph("<b>Step 4: Launch Main Supervisor & Web Dashboard</b>", h2_style))
    cmd_run = """# RUN IN SIMULATION MODE (On Laptop / PC without physical GPIO):
python main.py --simulate --port 5000

# RUN ON PHYSICAL RASPBERRY PI 4B:
sudo python main.py --port 5000

# Access Dashboard in any browser on the local Wi-Fi network:
# URL: http://localhost:5000  OR  http://<RASPBERRY_PI_IP>:5000"""
    story.append(Paragraph(cmd_run.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))

    story.append(Paragraph("<b>Step 5: Production Deployment via Linux systemd Service</b>", h2_style))
    cmd_service = """# Install background daemon so AgroNex boots automatically on power-up
sudo nano /etc/systemd/system/agronex.service

# Paste the following unit file:
[Unit]
Description=AgroNex-Pi Autonomous Rover Controller
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Major_project
ExecStart=/usr/bin/python3 /home/pi/Major_project/main.py --port 5000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

# Enable and start daemon:
sudo systemctl daemon-reload
sudo systemctl enable agronex.service
sudo systemctl start agronex.service"""
    story.append(Paragraph(cmd_service.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built: {filename}")

if __name__ == "__main__":
    build_pdf()
