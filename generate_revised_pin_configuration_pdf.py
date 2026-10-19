#!/usr/bin/env python3
"""
AgroNex-Pi: Revised Physical Pin Configuration & Interconnect Guide Generator
Generates: AgroNex_Pi_Revised_Pin_Configuration.pdf
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to compute and render total page count and professional headers/footers."""
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
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0f766e"))

        # Header (Top)
        self.drawString(54, 752, "AGRONEX-PI AUTONOMOUS ROBOTICS")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawRightString(558, 752, "REVISED HARDWARE PIN SPECIFICATION • 2026")
        
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.75)
        self.line(54, 744, 558, 744)

        # Footer (Bottom)
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "Confidential • Final Year Major Engineering Project")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def build_pdf(filename="AgroNex_Pi_Revised_Pin_Configuration.pdf"):
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0d9488"),
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        "Heading1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0f766e"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        "Heading2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )
    th_style = ParagraphStyle(
        "TableHead",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )
    td_style = ParagraphStyle(
        "TableData",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1e293b")
    )
    td_bold = ParagraphStyle(
        "TableDataBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0f172a")
    )
    callout_style = ParagraphStyle(
        "Callout",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#065f46")
    )

    story = []

    # Title Banner
    story.append(Spacer(1, 10))
    story.append(Paragraph("AgroNex-Pi: Revised Physical Pin Configuration", title_style))
    story.append(Paragraph("Complete Interconnect Map • Raspberry Pi 4B • Arduino Uno Slave • ADS1115 ADC • Relays & Actuators", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0d9488"), spaceAfter=12))

    # Executive Overview
    story.append(Paragraph("1. Hardware Architecture Overview", h1_style))
    overview_text = (
        "The <b>AgroNex-Pi</b> robot employs a master-slave embedded computing architecture. The <b>Raspberry Pi 4 Model B</b> "
        "serves as the primary compute unit, running the Linux OS, OpenCV computer vision, TensorFlow Lite deep learning inference, "
        "SQLite telemetry storage, and AWS Cloud Gateway relay. Analog instrumentation (Capacitive Soil Probe v1.2 and HW-038 Water Reservoir Sensor) "
        "is digitized via a precision <b>ADS1115 16-Bit I2C ADC</b> (Address 0x48). Low-level motor PWM timing, ultrasonic obstacle distance radars, "
        "and the <b>3D-printed Soil Moisture Probe Linear Actuator</b> are managed by an <b>Arduino Uno R3</b> coprocessor connected over USB Serial. "
        "The opto-isolated 5V relay module controls the 12V submersible irrigation pump and grass trimmer cutter with <b>independent, simultaneous switching</b>."
    )
    story.append(Paragraph(overview_text, body_style))

    # Architecture Callout Box
    callout_data = [
        [Paragraph("<b>Key Operational Constraints & Chronology:</b><br/>"
                   "• <b>Startup Sequence:</b> Boot -> IDLE (3s) -> Actuator Probe Moves DOWN -> All Sensors Sampled -> Actuator Probe Retracts UP -> Chassis Drives FORWARD -> Autonomous Patrol.<br/>"
                   "• <b>Subsystem Periodic Timing:</b> Soil Moisture Actuator probes every <b>1 Hour</b> • Ambient Temperature scans every <b>10 Minutes</b> • HW-038 Water Level monitors <b>Continuously (Zero Delay)</b>.<br/>"
                   "• <b>Independent Relay Channels:</b> Water Pump (CH1) and Grass Cutter (CH2) are decoupled and can operate concurrently without mutual rejection.", callout_style)]
    ]
    t_callout = Table(callout_data, colWidths=[504])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0fdf4")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#86efac")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 10))

    # Section 2: Raspberry Pi 40-Pin Header Table
    story.append(Paragraph("2. Raspberry Pi 40-Pin GPIO Header Mapping (BCM Specification)", h1_style))
    
    rpi_table_data = [
        [
            Paragraph("Physical Pin", th_style),
            Paragraph("BCM GPIO", th_style),
            Paragraph("Signal Type", th_style),
            Paragraph("Connected Device / Subsystem", th_style),
            Paragraph("Wiring Details & Logic Level", th_style)
        ],
        [
            Paragraph("Pin 1", td_bold),
            Paragraph("3.3V Power", td_style),
            Paragraph("DC Power", td_style),
            Paragraph("ADS1115 VDD, DHT VCC, HMC5883L", td_style),
            Paragraph("Regulated 3.3V supply from Pi PMIC (<50mA load)", td_style)
        ],
        [
            Paragraph("Pin 2", td_bold),
            Paragraph("5.0V Power", td_style),
            Paragraph("DC Power", td_style),
            Paragraph("Relay Module VCC, Buzzer VCC", td_style),
            Paragraph("5V logic supply rail (backed by 3A LM2596 buck converter)", td_style)
        ],
        [
            Paragraph("Pin 3", td_bold),
            Paragraph("GPIO 2", td_style),
            Paragraph("I2C1 SDA", td_style),
            Paragraph("ADS1115 ADC & HMC5883L Compass", td_style),
            Paragraph("Hardware I2C Data line (internal 1.8k pull-up to 3.3V)", td_style)
        ],
        [
            Paragraph("Pin 5", td_bold),
            Paragraph("GPIO 3", td_style),
            Paragraph("I2C1 SCL", td_style),
            Paragraph("ADS1115 ADC & HMC5883L Compass", td_style),
            Paragraph("Hardware I2C Clock line (100 kHz bus clock)", td_style)
        ],
        [
            Paragraph("Pin 6, 9, 14", td_bold),
            Paragraph("GND", td_style),
            Paragraph("Ground", td_style),
            Paragraph("Common System Star Ground", td_style),
            Paragraph("Unified GND plane meeting Pi, battery, & sensors", td_style)
        ],
        [
            Paragraph("Pin 7", td_bold),
            Paragraph("GPIO 4", td_style),
            Paragraph("Digital 1-Wire", td_style),
            Paragraph("DHT11 / DHT22 Sensor DATA", td_style),
            Paragraph("Atmospheric temp & humidity; 10k pull-up to 3.3V", td_style)
        ],
        [
            Paragraph("Pin 10", td_bold),
            Paragraph("GPIO 15", td_style),
            Paragraph("UART RXD", td_style),
            Paragraph("NEO-7M GPS Module TXD", td_style),
            Paragraph("9600 Baud NMEA serial sentences stream", td_style)
        ],
        [
            Paragraph("Pin 11", td_bold),
            Paragraph("GPIO 17", td_style),
            Paragraph("Digital OUT", td_style),
            Paragraph("Relay CH1: Submersible Water Pump", td_style),
            Paragraph("Active-LOW (0V = Energized/Pumping, 3.3V = De-energized)", td_style)
        ],
        [
            Paragraph("Pin 13", td_bold),
            Paragraph("GPIO 27", td_style),
            Paragraph("Digital OUT", td_style),
            Paragraph("Relay CH2: Grass Cutter Motor", td_style),
            Paragraph("Active-LOW (0V = Energized/Trimming, 3.3V = De-energized)", td_style)
        ],
        [
            Paragraph("Pin 15", td_bold),
            Paragraph("GPIO 22", td_style),
            Paragraph("Digital OUT", td_style),
            Paragraph("Active 5V Alarm Buzzer", td_style),
            Paragraph("Driven via 2N2222 NPN transistor buffer for loud alerts", td_style)
        ],
        [
            Paragraph("Pin 16", td_bold),
            Paragraph("GPIO 23", td_style),
            Paragraph("Digital OUT", td_style),
            Paragraph("System Heartbeat / Fault LED", td_style),
            Paragraph("Red LED Anode via 220 Ohm current-limiting resistor", td_style)
        ],
        [
            Paragraph("Pin 29, 31", td_bold),
            Paragraph("GPIO 5, 6", td_style),
            Paragraph("PWM / GPIO", td_style),
            Paragraph("BTS7960 #1 RPWM / LPWM (Left 4WD)", td_style),
            Paragraph("Chassis Left Motor control (Pi direct fallback port)", td_style)
        ],
        [
            Paragraph("Pin 33, 35", td_bold),
            Paragraph("GPIO 13, 19", td_style),
            Paragraph("PWM / GPIO", td_style),
            Paragraph("BTS7960 #2 RPWM / LPWM (Right 4WD)", td_style),
            Paragraph("Chassis Right Motor control (Pi direct fallback port)", td_style)
        ],
        [
            Paragraph("USB 3.0 Port", td_bold),
            Paragraph("/dev/ttyACM0", td_style),
            Paragraph("USB CDC ACM", td_style),
            Paragraph("Arduino Uno Slave Controller", td_style),
            Paragraph("115200 Baud link for Actuator Probe & Motor commands", td_style)
        ],
        [
            Paragraph("CSI Ribbon", td_bold),
            Paragraph("CSI-2 Bus", td_style),
            Paragraph("2-Lane MIPI", td_style),
            Paragraph("Raspberry Pi CSI Camera Module", td_style),
            Paragraph("Captures real-time leaf foliage frames for CNN inference", td_style)
        ]
    ]

    t_rpi = Table(rpi_table_data, colWidths=[60, 60, 70, 154, 160])
    t_rpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f766e")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_rpi)
    story.append(Spacer(1, 12))

    # Page Break for clean multi-page document
    story.append(PageBreak())

    # Section 3: ADS1115 ADC & Analog Sensor Mapping
    story.append(Paragraph("3. ADS1115 16-Bit I2C ADC Channel Map", h1_style))
    story.append(Paragraph(
        "To avoid noise on the Pi's internal SPI bus and eliminate ground shifts, all analog field sensors "
        "connect to the dedicated <b>ADS1115 I2C Analog-to-Digital Converter</b> (Operating Address: 0x48).",
        body_style
    ))

    ads_table_data = [
        [
            Paragraph("Channel", th_style),
            Paragraph("Connected Sensor", th_style),
            Paragraph("Operating Principle", th_style),
            Paragraph("Raw ADC Range (16-Bit)", th_style),
            Paragraph("Calibrated Engineering Metric", th_style)
        ],
        [
            Paragraph("AIN0", td_bold),
            Paragraph("Capacitive Soil Moisture Probe v1.2", td_style),
            Paragraph("Dielectric capacitance frequency shift; corrosion-resistant", td_style),
            Paragraph("Dry: 21000<br/>Submerged: 9500", td_style),
            Paragraph("0.0% to 100.0% Volumetric Water Content (VWC)", td_style)
        ],
        [
            Paragraph("AIN1", td_bold),
            Paragraph("HW-038 Water Reservoir Level Sensor", td_style),
            Paragraph("Parallel conductor resistance immersion depth; 3-pin", td_style),
            Paragraph("Empty: 1200<br/>Full (4cm): 18500", td_style),
            Paragraph("0.0% to 100.0% Reservoir Capacity (Continuous)", td_style)
        ],
        [
            Paragraph("AIN2", td_bold),
            Paragraph("Battery Voltage Divider (12V Pack)", td_style),
            Paragraph("10k/2.2k precision divider (5.5:1 ratio into 3.3V range)", td_style),
            Paragraph("9.0V: 15400<br/>12.6V: 21560", td_style),
            Paragraph("9.0V to 12.6V Li-ion Battery Pack Voltage", td_style)
        ],
        [
            Paragraph("AIN3", td_bold),
            Paragraph("Spare Analog Channel", td_style),
            Paragraph("Reserved for optional solar panel monitoring or pH probe", td_style),
            Paragraph("0 to 32767", td_style),
            Paragraph("General Analog Input (0 - 4.096V range)", td_style)
        ]
    ]

    t_ads = Table(ads_table_data, colWidths=[45, 120, 135, 94, 110])
    t_ads.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0369a1")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#ffffff"), colors.HexColor("#f0f9ff")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_ads)
    story.append(Spacer(1, 12))

    # Section 4: Arduino Uno Slave Controller Pin Table
    story.append(Paragraph("4. Arduino Uno Slave Controller (Motors, Actuator & Radars)", h1_style))
    story.append(Paragraph(
        "The Arduino Uno receives serial string commands from the Pi over USB (/dev/ttyACM0 at 115200 baud). "
        "It generates stable hardware PWM for the BTS7960 motor drivers and servo pulses for the <b>3D-Printed Soil Probe Linear Actuator</b>.",
        body_style
    ))

    arduino_table_data = [
        [
            Paragraph("Arduino Pin", th_style),
            Paragraph("Subsystem Component", th_style),
            Paragraph("Signal Direction", th_style),
            Paragraph("Hardware Role & Command Protocol", th_style)
        ],
        [
            Paragraph("Pin D3 (PWM)", td_bold),
            Paragraph("Soil Moisture Actuator Servo", td_style),
            Paragraph("Digital OUT (50 Hz PWM)", td_style),
            Paragraph("<b>PROBE_DOWN:</b> Rotates arm into soil.<br/><b>PROBE_UP:</b> Lifts arm safely back to travel posture.", td_style)
        ],
        [
            Paragraph("Pin D4", td_bold),
            Paragraph("Left BTS7960 Enable (R_EN + L_EN)", td_style),
            Paragraph("Digital OUT (5V)", td_style),
            Paragraph("Bridges R_EN and L_EN of Left BTS7960 driver to enable H-bridge.", td_style)
        ],
        [
            Paragraph("Pin D5, D6", td_bold),
            Paragraph("Left BTS7960 (Left 4WD Motors)", td_style),
            Paragraph("PWM Output (Timer 0)", td_style),
            Paragraph("<b>D5:</b> Left Forward PWM (RPWM).<br/><b>D6:</b> Left Reverse PWM (LPWM). Driven via 'M,<left>,<right>'.", td_style)
        ],
        [
            Paragraph("Pin D7", td_bold),
            Paragraph("Right BTS7960 Enable (R_EN + L_EN)", td_style),
            Paragraph("Digital OUT (5V)", td_style),
            Paragraph("Bridges R_EN and L_EN of Right BTS7960 driver to enable H-bridge.", td_style)
        ],
        [
            Paragraph("Pin D9, D10", td_bold),
            Paragraph("Right BTS7960 (Right 4WD Motors)", td_style),
            Paragraph("PWM Output (Timer 1)", td_style),
            Paragraph("<b>D9:</b> Right Forward PWM (RPWM).<br/><b>D10:</b> Right Reverse PWM (LPWM).", td_style)
        ],
        [
            Paragraph("Pin D2, D8", td_bold),
            Paragraph("Front Ultrasonic Sensor (HC-SR04)", td_style),
            Paragraph("D2: TRIG (OUT)<br/>D8: ECHO (IN)", td_style),
            Paragraph("Measures forward obstacles. Commanded via 'SCAN_F,<angle>'. Reports 'DIST_F:<cm>'.", td_style)
        ],
        [
            Paragraph("Pin D11 (PWM)", td_bold),
            Paragraph("Front Ultrasonic Pan Servo", td_style),
            Paragraph("Digital OUT (50 Hz PWM)", td_style),
            Paragraph("Sweeps front radar bracket left/right during obstacle avoidance.", td_style)
        ],
        [
            Paragraph("Pin D12 (PWM)", td_bold),
            Paragraph("Rear Ultrasonic Pan Servo", td_style),
            Paragraph("Digital OUT (50 Hz PWM)", td_style),
            Paragraph("Sweeps rear radar bracket left/right during reverse patrol.", td_style)
        ],
        [
            Paragraph("Pin A0, A1", td_bold),
            Paragraph("Rear Ultrasonic Sensor (HC-SR04)", td_style),
            Paragraph("A0: TRIG (OUT)<br/>A1: ECHO (IN)", td_style),
            Paragraph("Measures rear obstacle clearance. Reports 'DIST_R:<cm>'.", td_style)
        ],
        [
            Paragraph("USB Type-B", td_bold),
            Paragraph("Raspberry Pi 4 USB 3.0 Port", td_style),
            Paragraph("Bidirectional Serial (115200)", td_style),
            Paragraph("Full-duplex command link. Auto-halts motors if communication watchdog drops >500ms.", td_style)
        ]
    ]

    t_ard = Table(arduino_table_data, colWidths=[75, 135, 105, 189])
    t_ard.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4338ca")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#ffffff"), colors.HexColor("#eef2ff")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_ard)
    story.append(Spacer(1, 12))

    # Section 5: Relay Module & Power Architecture
    story.append(Paragraph("5. Opto-Isolated Relay Subsystem & Electrical Decoupling", h1_style))
    relay_text = (
        "<b>Independent Simultaneous Switching:</b> CH1 (Irrigation Pump) and CH2 (Grass Cutter) operate on separate opto-isolated "
        "relay channels driven by GPIO 17 and GPIO 27. Each channel features an onboard PC817 optocoupler providing 2.5 kV isolation "
        "between the Raspberry Pi's digital 3.3V logic and the high-current 12V DC motor circuits. "
        "Flyback diodes (1N4007) are placed in reverse parallel across both the water pump and cutting motor terminals "
        "to suppress inductive kickback spikes (Back-EMF) that would otherwise cause voltage sags or brownouts on the Pi."
    )
    story.append(Paragraph(relay_text, body_style))

    # Chronology Summary Table
    story.append(Paragraph("6. Operational Startup Chronology & Autonomous Scheduling", h1_style))
    chronology_data = [
        [
            Paragraph("Phase / Event", th_style),
            Paragraph("Trigger Mechanism", th_style),
            Paragraph("Hardware Motion & Sensor Action", th_style),
            Paragraph("Dashboard Telemetry Result", th_style)
        ],
        [
            Paragraph("Step 1: IDLE", td_bold),
            Paragraph("System Boot / Reset", td_style),
            Paragraph("Robot remains stationary for 3.0 seconds to allow sensor warm-up & GPS fix.", td_style),
            Paragraph("Status: 'IDLE'; Connection dot glows green.", td_style)
        ],
        [
            Paragraph("Step 2: Probe Down", td_bold),
            Paragraph("Startup Chronology", td_style),
            Paragraph("Linear actuator extends probe DOWN into soil (PROBE_DOWN pulse).", td_style),
            Paragraph("Actuator pill: 'PROBING (DOWN)'.", td_style)
        ],
        [
            Paragraph("Step 3: Sample Sensors", td_bold),
            Paragraph("Startup Chronology", td_style),
            Paragraph("Reads Capacitive Soil Moisture, HW-038 Water Level, DHT Temp/Hum, GPS, Compass.", td_style),
            Paragraph("Live metrics update with persistent values.", td_style)
        ],
        [
            Paragraph("Step 4: Probe Up", td_bold),
            Paragraph("Startup Chronology", td_style),
            Paragraph("Linear actuator retracts probe safely UP into travel position (PROBE_UP).", td_style),
            Paragraph("Actuator pill: 'RETRACTED (UP)'.", td_style)
        ],
        [
            Paragraph("Step 5: Move Forward", td_bold),
            Paragraph("Startup Chronology", td_style),
            Paragraph("Chassis dual BTS7960 motors drive FORWARD for 2.0s at 60% duty cycle.", td_style),
            Paragraph("FSM: 'NAVIGATING' -> 'MONITORING'.", td_style)
        ],
        [
            Paragraph("Periodic 1-Hr Actuator", td_bold),
            Paragraph("Every 3600 seconds", td_style),
            Paragraph("Halts chassis, lowers probe, samples moisture, retracts probe, updates database.", td_style),
            Paragraph("Last moisture reading persistently displayed.", td_style)
        ],
        [
            Paragraph("Periodic 10-Min Temp", td_bold),
            Paragraph("Every 600 seconds", td_style),
            Paragraph("DHT sensor reads ambient temperature & humidity, checking crop heat stress.", td_style),
            Paragraph("Last temperature reading persistently displayed.", td_style)
        ],
        [
            Paragraph("Continuous Water Level", td_bold),
            Paragraph("Real-Time (Zero Delay)", td_style),
            Paragraph("HW-038 sensor analog read every 1s, preventing water tank dry-running.", td_style),
            Paragraph("Instant reservoir gauge update on dashboard.", td_style)
        ]
    ]

    t_chrono = Table(chronology_data, colWidths=[90, 85, 185, 144])
    t_chrono.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#065f46")),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#ffffff"), colors.HexColor("#ecfdf5")]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_chrono)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated revised pin configuration PDF: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    build_pdf()
