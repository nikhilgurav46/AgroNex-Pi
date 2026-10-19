#!/usr/bin/env python3
"""
AgroNex-Pi: Documentation Generator
Generates:
  1. AgroNex_Pi_Full_Project_Report.pdf  — Complete technical manual
  2. AgroNex_Pi_IEEE_Research_Paper.pdf  — IEEE-format research paper
"""

import os
import sys

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm, mm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, HRFlowable, KeepTogether, ListFlowable, ListItem
    )
    from reportlab.platypus.flowables import Flowable
    from reportlab.pdfgen import canvas as pdfcanvas
except ImportError:
    print("ERROR: reportlab not installed. Run: pip install reportlab")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Color Palette
GREEN_DARK   = colors.HexColor("#1B5E20")
GREEN_MID    = colors.HexColor("#388E3C")
GREEN_LIGHT  = colors.HexColor("#A5D6A7")
GREEN_BG     = colors.HexColor("#E8F5E9")
ACCENT_BLUE  = colors.HexColor("#1565C0")
ACCENT_AMBER = colors.HexColor("#F57F17")
GREY_DARK    = colors.HexColor("#212121")
GREY_MID     = colors.HexColor("#616161")
GREY_LIGHT   = colors.HexColor("#F5F5F5")
WHITE        = colors.white
BLACK        = colors.black

def report_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(GREEN_MID)
    canvas.setLineWidth(2)
    canvas.rect(1.5*cm, 1.5*cm, w - 3*cm, h - 3*cm)
    canvas.setFillColor(GREEN_DARK)
    canvas.rect(1.5*cm, h - 2.8*cm, w - 3*cm, 1.2*cm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(2*cm, h - 2.4*cm, "AgroNex-Pi  |  Autonomous Smart Agricultural Robot")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - 2*cm, h - 2.4*cm, f"Page {doc.page}")
    canvas.setFillColor(GREY_MID)
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(w/2, 1.7*cm, "AgroNex-Pi Project Report  |  Confidential — For Academic Use Only")
    canvas.restoreState()

def ieee_page(canvas, doc):
    canvas.saveState()
    w, h = letter
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY_MID)
    if doc.page > 1:
        canvas.drawCentredString(w/2, 0.6*inch, f"{doc.page}")
    canvas.restoreState()

def make_report_styles():
    s = {}
    s['cover_title'] = ParagraphStyle('cover_title',fontName='Helvetica-Bold',fontSize=32,textColor=WHITE,alignment=TA_CENTER,spaceAfter=6,leading=38)
    s['cover_sub'] = ParagraphStyle('cover_sub',fontName='Helvetica',fontSize=14,textColor=GREEN_LIGHT,alignment=TA_CENTER,spaceAfter=4)
    s['cover_info'] = ParagraphStyle('cover_info',fontName='Helvetica',fontSize=11,textColor=WHITE,alignment=TA_CENTER,spaceAfter=3)
    s['h1'] = ParagraphStyle('h1',fontName='Helvetica-Bold',fontSize=18,textColor=WHITE,backColor=GREEN_DARK,alignment=TA_LEFT,spaceBefore=18,spaceAfter=8,leftIndent=-12,rightIndent=-12,borderPad=8,leading=22)
    s['h2'] = ParagraphStyle('h2',fontName='Helvetica-Bold',fontSize=13,textColor=GREEN_DARK,spaceBefore=12,spaceAfter=4,leading=16)
    s['h3'] = ParagraphStyle('h3',fontName='Helvetica-Bold',fontSize=11,textColor=ACCENT_BLUE,spaceBefore=8,spaceAfter=3,leading=14)
    s['body'] = ParagraphStyle('body',fontName='Helvetica',fontSize=10,textColor=GREY_DARK,alignment=TA_JUSTIFY,spaceBefore=3,spaceAfter=4,leading=14)
    s['code'] = ParagraphStyle('code',fontName='Courier',fontSize=8.5,textColor=GREY_DARK,backColor=GREY_LIGHT,spaceBefore=4,spaceAfter=4,leftIndent=12,rightIndent=12,leading=13,borderWidth=1,borderColor=colors.HexColor("#BDBDBD"),borderPad=6)
    s['bullet'] = ParagraphStyle('bullet',fontName='Helvetica',fontSize=10,textColor=GREY_DARK,leftIndent=16,spaceAfter=2,leading=14)
    s['caption'] = ParagraphStyle('caption',fontName='Helvetica-Oblique',fontSize=9,textColor=GREY_MID,alignment=TA_CENTER,spaceAfter=6)
    s['note'] = ParagraphStyle('note',fontName='Helvetica-Oblique',fontSize=9,textColor=GREY_MID,backColor=colors.HexColor("#FFF9C4"),leftIndent=8,rightIndent=8,spaceBefore=4,spaceAfter=4,borderWidth=1,borderColor=ACCENT_AMBER,borderPad=5,leading=13)
    s['warning'] = ParagraphStyle('warning',fontName='Helvetica-Bold',fontSize=9,textColor=colors.HexColor("#B71C1C"),backColor=colors.HexColor("#FFEBEE"),leftIndent=8,rightIndent=8,spaceBefore=4,spaceAfter=4,borderWidth=1,borderColor=colors.HexColor("#C62828"),borderPad=5,leading=13)
    return s

def make_ieee_styles():
    s = {}
    s['title'] = ParagraphStyle('ieee_title',fontName='Times-Bold',fontSize=22,textColor=BLACK,alignment=TA_CENTER,spaceAfter=8,leading=26)
    s['authors'] = ParagraphStyle('ieee_authors',fontName='Times-Italic',fontSize=11,textColor=BLACK,alignment=TA_CENTER,spaceAfter=3,leading=14)
    s['affil'] = ParagraphStyle('ieee_affil',fontName='Times-Roman',fontSize=10,textColor=GREY_MID,alignment=TA_CENTER,spaceAfter=12,leading=13)
    s['abstract_head'] = ParagraphStyle('ieee_abstract_head',fontName='Times-Bold',fontSize=10,textColor=BLACK,alignment=TA_CENTER,spaceAfter=2)
    s['abstract'] = ParagraphStyle('ieee_abstract',fontName='Times-Roman',fontSize=9,textColor=BLACK,alignment=TA_JUSTIFY,spaceBefore=0,spaceAfter=8,leftIndent=36,rightIndent=36,leading=13)
    s['keywords'] = ParagraphStyle('ieee_keywords',fontName='Times-Italic',fontSize=9,textColor=BLACK,alignment=TA_JUSTIFY,leftIndent=36,rightIndent=36,spaceAfter=10,leading=12)
    s['h1'] = ParagraphStyle('ieee_h1',fontName='Times-Bold',fontSize=10,textColor=BLACK,alignment=TA_CENTER,spaceBefore=10,spaceAfter=4,leading=13)
    s['h2'] = ParagraphStyle('ieee_h2',fontName='Times-BoldItalic',fontSize=10,textColor=BLACK,alignment=TA_LEFT,spaceBefore=6,spaceAfter=2,leading=13)
    s['body'] = ParagraphStyle('ieee_body',fontName='Times-Roman',fontSize=10,textColor=BLACK,alignment=TA_JUSTIFY,spaceBefore=0,spaceAfter=4,leading=13,firstLineIndent=18)
    s['body_noindent'] = ParagraphStyle('ieee_body_noindent',fontName='Times-Roman',fontSize=10,textColor=BLACK,alignment=TA_JUSTIFY,spaceBefore=0,spaceAfter=4,leading=13)
    s['caption'] = ParagraphStyle('ieee_caption',fontName='Times-Italic',fontSize=9,textColor=BLACK,alignment=TA_CENTER,spaceAfter=6,leading=12)
    s['ref'] = ParagraphStyle('ieee_ref',fontName='Times-Roman',fontSize=9,textColor=BLACK,alignment=TA_JUSTIFY,leftIndent=18,firstLineIndent=-18,spaceAfter=3,leading=12)
    s['placeholder'] = ParagraphStyle('ieee_placeholder',fontName='Times-Italic',fontSize=10,textColor=GREY_MID,alignment=TA_CENTER,spaceAfter=4,backColor=colors.HexColor("#F0F0F0"),borderWidth=1,borderColor=GREY_MID,borderPad=8,leading=14)
    return s

def styled_table(data, col_widths, header_rows=1):
    style = [
        ('BACKGROUND',(0,0),(-1,header_rows-1),GREEN_DARK),
        ('TEXTCOLOR',(0,0),(-1,header_rows-1),WHITE),
        ('FONTNAME',(0,0),(-1,header_rows-1),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,header_rows-1),9),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('FONTNAME',(0,header_rows),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,header_rows),(-1,-1),9),
        ('ROWBACKGROUNDS',(0,header_rows),(-1,-1),[WHITE,GREEN_BG]),
        ('GRID',(0,0),(-1,-1),0.5,GREY_MID),
        ('TOPPADDING',(0,0),(-1,-1),4),
        ('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),6),
        ('RIGHTPADDING',(0,0),(-1,-1),6),
    ]
    return Table(data,colWidths=col_widths,style=style,repeatRows=header_rows)

def ieee_table(data,col_widths):
    style = [
        ('FONTNAME',(0,0),(-1,0),'Times-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),9),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LINEBELOW',(0,0),(-1,0),1,BLACK),
        ('LINEBELOW',(0,-1),(-1,-1),1,BLACK),
        ('LINEABOVE',(0,0),(-1,0),1,BLACK),
        ('TOPPADDING',(0,0),(-1,-1),3),
        ('BOTTOMPADDING',(0,0),(-1,-1),3),
    ]
    return Table(data,colWidths=col_widths,style=style)

def placeholder_box(s, label, height_cm=5):
    t = Table([[Paragraph(f"[ {label} ]<br/><br/>(Insert figure / photograph here)", s['placeholder'])]],colWidths=[14*cm])
    t.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),1.5,GREY_MID),
        ('BACKGROUND',(0,0),(-1,-1),colors.HexColor("#F8F8F8")),
        ('MINROWHEIGHTS',(0,0),(-1,-1),height_cm*cm),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ]))
    return t

# ─── FULL PROJECT REPORT ─────────────────────────────────────────────────────
def build_project_report():
    out = os.path.join(BASE_DIR, "AgroNex_Pi_Full_Project_Report.pdf")
    doc = SimpleDocTemplate(out,pagesize=A4,rightMargin=2.2*cm,leftMargin=2.2*cm,topMargin=3.4*cm,bottomMargin=2.2*cm,title="AgroNex-Pi Full Project Report",author="AgroNex-Pi Team")
    s = make_report_styles()
    story = []
    W = A4[0] - 4.4*cm

    # Cover
    cover_bg = Table([
        [Paragraph("AgroNex-Pi", s['cover_title'])],
        [Paragraph("Autonomous Smart Agricultural Robot", s['cover_sub'])],
        [Spacer(1,0.3*cm)],
        [Paragraph("Full Project Technical Report &amp; Developer Manual", s['cover_sub'])],
        [Spacer(1,0.8*cm)],
        [Paragraph("Raspberry Pi 4  |  TensorFlow Lite  |  AWS Cloud  |  GPS Navigation", s['cover_info'])],
        [Spacer(1,0.3*cm)],
        [Paragraph("Soil Moisture Sensing  |  Plant Disease AI  |  Grass Cutting  |  Irrigation", s['cover_info'])],
        [Spacer(1,1.2*cm)],
        [Paragraph("Prepared by: <b>Nikhil &amp; Team</b>", s['cover_info'])],
        [Paragraph("Academic Year: 2025-2026", s['cover_info'])],
        [Spacer(1,0.3*cm)],
        [Paragraph("Major Project — Final Year B.E./B.Tech (Electronics / Computer Engineering)", s['cover_info'])],
    ],colWidths=[W])
    cover_bg.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),GREEN_DARK),('BOX',(0,0),(-1,-1),3,GREEN_MID),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),('LEFTPADDING',(0,0),(-1,-1),20),('RIGHTPADDING',(0,0),(-1,-1),20)]))
    story.append(Spacer(1,1.5*cm))
    story.append(cover_bg)
    story.append(PageBreak())

    # TOC
    story.append(Paragraph("Table of Contents", s['h1']))
    story.append(Spacer(1,0.3*cm))
    toc_items=[("1.","Project Overview & Objectives","3"),("2.","System Architecture","4"),("3.","Hardware Components & Bill of Materials","5"),("4.","Pin Configuration & Wiring Guide","7"),("5.","Software Modules — Design & Code Explanation","10"),("  5.1","config.py — Global Configuration","10"),("  5.2","hardware.py — Hardware Driver Layer","11"),("  5.3","irrigation.py — Irrigation Controller","13"),("  5.4","cutter.py — Grass Trimmer Controller","14"),("  5.5","navigation.py — GPS Waypoint Navigation","15"),("  5.6","disease_detect.py — AI Disease Detection Pipeline","16"),("  5.7","disease_db.py — Disease Knowledge Base","18"),("  5.8","main.py — System Supervisor & FSM","19"),("  5.9","app.py — Flask REST API Server","21"),("  5.10","aws_relay.py — AWS Cloud Integration","22"),("  5.11","database.py — SQLite Persistence Layer","23"),("6.","AI Model Training Pipeline","24"),("7.","AWS Cloud Architecture","26"),("8.","Web Dashboard (index.html)","27"),("9.","System Working — End-to-End Flow","28"),("10.","Safety Mechanisms & Interlocks","30"),("11.","Testing Scripts","31"),("12.","Known Issues & Future Work","32")]
    toc_data=[["§","Section","Pg."]]
    for num,title,pg in toc_items:
        toc_data.append([num,title,pg])
    toc_t=Table(toc_data,colWidths=[1.2*cm,W-3*cm,1.5*cm])
    toc_t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),GREEN_DARK),('TEXTCOLOR',(0,0),(-1,0),WHITE),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,GREEN_BG]),('GRID',(0,0),(-1,-1),0.3,GREY_MID),('ALIGN',(2,0),(2,-1),'CENTER'),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),('LEFTPADDING',(0,0),(-1,-1),5)]))
    story.append(toc_t)
    story.append(PageBreak())

    # Section 1 — Overview
    story.append(Paragraph("1. Project Overview &amp; Objectives", s['h1']))
    story.append(Paragraph("AgroNex-Pi is a fully autonomous Raspberry Pi-based smart agricultural robot integrating five subsystems on a single rover chassis: real-time soil moisture sensing &amp; automated irrigation, scheduled grass trimming, GPS-guided waypoint navigation, AI-powered plant disease detection, and live cloud telemetry via AWS. All subsystems are coordinated by a multi-threaded Python supervisor running a Finite State Machine (FSM).", s['body']))
    story.append(Paragraph("1.1 Key Objectives", s['h2']))
    for obj in ["Automate repetitive agricultural tasks (watering, mowing) without continuous human intervention.","Detect plant diseases early using edge AI (TensorFlow Lite on Raspberry Pi 4) to minimize crop loss.","Provide real-time sensor telemetry accessible from anywhere via an AWS-hosted web dashboard.","Operate autonomously within a defined GPS-bounded area using compass-guided navigation.","Implement fail-safe hardware interlocks to prevent equipment damage during simultaneous actuator operation.","Support over-the-air monitoring and remote control via Flask REST API and AWS API Gateway.","Log all events (irrigation cycles, disease scans, system errors) to a local SQLite database for analysis."]:
        story.append(Paragraph(f"• {obj}", s['bullet']))
    story.append(Paragraph("1.2 Project Scope", s['h2']))
    story.append(Paragraph("The project targets Tulsi (Holy Basil) and general leafy plants as primary disease detection subjects, with a dual-model architecture supporting both the custom Tulsi model (5 classes: Healthy, Infected, Infested, Wilting, Background) and the PlantVillage broad-crop model (Tomato, Potato, Pepper — 8 classes). The rover is intended for outdoor garden/farm deployment with a human safety observer present.", s['body']))
    story.append(PageBreak())

    # Section 2 — Architecture
    story.append(Paragraph("2. System Architecture", s['h1']))
    story.append(Paragraph("AgroNex-Pi uses a layered, modular software architecture. No module other than hardware.py accesses GPIO or SPI pins directly. All inter-module communication is via Python object references or the shared telemetry cache maintained by app.py.", s['body']))
    story.append(Paragraph("2.1 Software Layer Diagram", s['h2']))
    arch_data=[["Layer","Modules","Responsibility"],["Hardware Abstraction (HAL)","hardware.py","GPIO, SPI, I2C, Camera, PWM — all physical I/O"],["Sensor/Actuator Controllers","irrigation.py\ncutter.py\nnavigation.py\ndisease_detect.py","Business logic for each subsystem (hysteresis, scheduling, AI inference)"],["Persistence","database.py","SQLite: events, scans, irrigation logs"],["Application Layer","app.py (Flask)","REST API, telemetry cache"],["System Supervisor","main.py","FSM, thread lifecycle, signal handlers"],["Cloud Integration","aws_relay.py","HTTP push to AWS API Gateway / S3"],["Knowledge Base","disease_db.py","Plant disease encyclopedia (cause, treatment)"],["Configuration","config.py","Centralised constants and pin map"]]
    story.append(styled_table(arch_data,[3.5*cm,4*cm,W-7.5*cm]))
    story.append(Paragraph("2.2 Thread Model", s['h2']))
    story.append(Paragraph("The supervisor launches four concurrent threads managed by Python's threading library:", s['body']))
    for name,desc in [("Control Loop Thread","3-second poll cycle: reads all sensors, evaluates irrigation, cutter, navigation, triggers auto-scan. Heartbeat timestamp updated each iteration."),("Disease Scanner Thread","Runs DiseaseDetector when triggered by green-pixel detection or manual API request. Saves result + JPEG scan to disk."),("Flask API Server Thread","Serves the REST API on port 5000 (daemon thread). Provides /api/telemetry, /api/scan, /api/manual/* endpoints."),("Watchdog Thread","Monitors control loop heartbeat. If no update within 30 seconds, logs an alert and optionally triggers safe-state.")]:
        story.append(Paragraph(f"<b>{name}:</b> {desc}", s['bullet']))
    story.append(PageBreak())

    # Section 3 — BOM
    story.append(Paragraph("3. Hardware Components &amp; Bill of Materials", s['h1']))
    bom_data=[["#","Component","Model / Spec","Qty","Purpose"],["1","Microcontroller","Raspberry Pi 4 Model B (4GB RAM)","1","Central processing unit; runs all Python modules"],["2","Soil Moisture Sensor","Capacitive v1.2 (3.3V)","1","Reads soil moisture (analog output)"],["3","ADC (I2C)","ADS1115 16-bit 4-ch I2C","1","Converts analog sensor signals to digital (primary)"],["4","ADC (SPI Fallback)","MCP3008 10-bit 8-ch SPI","1 (opt)","Backup ADC via SPI bus"],["5","Water Level Sensor","HW-038 3-pin Analog","1","Monitors water reservoir level"],["6","Temp/Humidity Sensor","DHT11 or DHT22","1","Ambient temperature and humidity"],["7","GPS Module","NEO-7M UART @ 9600 baud","1","Global positioning for waypoint navigation"],["8","Compass/Magnetometer","HMC5883L I2C 3-axis","1","Heading feedback for navigation"],["9","Camera","Raspberry Pi Camera v2 / USB webcam","1","Captures leaf images for disease AI"],["10","Motor Driver","BTS7960 43A H-Bridge","2","Drives DC drive motors (left side + right side)"],["11","Drive Motors","12V DC Geared Motor","4","Chassis locomotion"],["12","Relay Module","2-Channel 5V Active LOW","1","Switches water pump (CH1) and cutter (CH2)"],["13","Water Pump","Mini Submersible 5V-12V DC","1","Irrigation water delivery"],["14","Grass Cutter Motor","12V DC Brushed (blade attached)","1","Grass trimming actuator"],["15","Buzzer","5V Active Buzzer","1","Audio alerts"],["16","LED Indicator","Red LED + 220Ohm resistor","1","Visual status indicator"],["17","Buck Converter","LM2596 / XL4016 DC-DC Step-down","1","Steps 12V battery to 5V for Pi"],["18","Battery","12V 7Ah SLA or 3S Li-ion Pack","1","Main power supply"],["19","MicroSD Card","32GB+ Class 10 / A1","1","OS + project files storage"]]
    story.append(styled_table(bom_data,[0.6*cm,3.5*cm,4.5*cm,0.7*cm,W-9.3*cm]))
    story.append(PageBreak())

    # Section 4 — Pin Config
    story.append(Paragraph("4. Pin Configuration &amp; Wiring Guide", s['h1']))
    story.append(Paragraph("All GPIO assignments use BCM numbering (GPIO.setmode(GPIO.BCM)). Physical pin numbers refer to the standard Raspberry Pi 40-pin header.", s['body']))
    story.append(Paragraph("4.1 Power &amp; Ground Rail", s['h2']))
    power_data=[["Physical Pin","Signal","Connected To"],["Pin 1 (3.3V)","3.3V Power","DHT VCC, ADS1115 VDD, MCP3008 VDD/VREF, HMC5883L VCC, Capacitive Sensor VCC"],["Pin 2 (5V)","5V Power","Relay Module VCC, Buzzer (+)"],["Pin 4 (5V)","5V Power","Buck Converter Output to Pi GPIO 5V rail"],["Pin 6 (GND)","Signal GND","DHT GND"],["Pin 25 (GND)","Analog GND","ADS1115 GND, MCP3008 AGND (pin 14) + DGND (pin 9)"],["Pin 39 (GND)","Power GND","BTS7960 logic ground (star-grounded with battery negative)"]]
    story.append(styled_table(power_data,[2.5*cm,3*cm,W-5.5*cm]))
    story.append(Spacer(1,0.3*cm))
    story.append(Paragraph("4.2 GPIO Signal Pins (BCM Numbering)", s['h2']))
    gpio_data=[["BCM GPIO","Physical Pin","Direction","Signal / Function","Connected Hardware"],["GPIO 4","Pin 7","INPUT","DHT Data (10k pull-up to 3.3V)","DHT11/22 Temperature & Humidity Sensor"],["GPIO 17","Pin 11","OUTPUT","Relay CH1 Pump (Active LOW)","Relay Module IN1 to Water Pump"],["GPIO 27","Pin 13","OUTPUT","Relay CH2 Cutter (Active LOW)","Relay Module IN2 to Grass Cutter Motor"],["GPIO 22","Pin 15","OUTPUT","Buzzer (+)","5V Active Buzzer positive terminal"],["GPIO 23","Pin 16","OUTPUT","LED Anode (via 220 Ohm)","Red Status LED"],["GPIO 5","Pin 29","PWM OUT","Left Side RPWM (Forward)","BTS7960 #1 RPWM"],["GPIO 6","Pin 31","PWM OUT","Left Side LPWM (Reverse)","BTS7960 #1 LPWM"],["GPIO 13","Pin 33","PWM OUT","Right Side RPWM (Forward)","BTS7960 #2 RPWM"],["GPIO 19","Pin 35","PWM OUT","Right Side LPWM (Reverse)","BTS7960 #2 LPWM"],["GPIO 14","Pin 8","UART TX","GPS UART TX (optional config)","NEO-7M RX (optional)"],["GPIO 15","Pin 10","UART RX","GPS UART RX /dev/serial0","NEO-7M TX to Pi RXD"]]
    story.append(styled_table(gpio_data,[1.5*cm,1.8*cm,1.8*cm,4.5*cm,W-9.6*cm]))
    story.append(Spacer(1,0.3*cm))
    story.append(Paragraph("4.3 I2C Bus (GPIO2=SDA, GPIO3=SCL — Physical Pins 3, 5)", s['h2']))
    i2c_data=[["I2C Address","Device","Function","Notes"],["0x48","ADS1115 16-bit ADC","Reads: Soil Moisture (A0), Water Level (A1), Spare (A2/A3)","Internal pull-ups; external 4.7k optional"],["0x1E","HMC5883L Magnetometer","3-axis compass heading for GPS navigation","External 4.7k pull-ups to 3.3V required on SDA/SCL"]]
    story.append(styled_table(i2c_data,[1.8*cm,3.5*cm,6*cm,W-11.3*cm]))
    story.append(Spacer(1,0.3*cm))
    story.append(Paragraph("4.4 SPI Bus (MCP3008 Fallback ADC)", s['h2']))
    spi_data=[["BCM GPIO","Physical Pin","SPI Signal","MCP3008 Pin"],["GPIO 10","Pin 19","MOSI (DIN)","Pin 11"],["GPIO 9","Pin 21","MISO (DOUT)","Pin 12"],["GPIO 11","Pin 23","SCLK (CLK)","Pin 13"],["GPIO 8","Pin 24","CE0 (CS/SHDN)","Pin 10"],["3.3V","Pin 1","VDD & VREF","Pins 16 & 15"],["GND","Pin 25","AGND & DGND","Pins 14 & 9"]]
    story.append(styled_table(spi_data,[1.8*cm,2.2*cm,3*cm,W-7*cm]))
    story.append(Spacer(1,0.3*cm))
    story.append(Paragraph("4.5 BTS7960 Motor Driver Wiring", s['h2']))
    story.append(Paragraph("Two BTS7960 H-Bridge boards are used. BTS #1 drives both left-side motors (front-left + rear-left in parallel). BTS #2 drives both right-side motors. Each board's R_EN and L_EN must be tied to 5V (always enabled). All grounds must share a common star-ground point.", s['body']))
    bts_data=[["BTS Board","Pi BCM","Pi Physical Pin","BTS Pin","Motor Direction"],["BTS #1 (Left)","GPIO 5","Pin 29","RPWM","Left Forward"],["BTS #1 (Left)","GPIO 6","Pin 31","LPWM","Left Reverse"],["BTS #2 (Right)","GPIO 13","Pin 33","RPWM","Right Forward"],["BTS #2 (Right)","GPIO 19","Pin 35","LPWM","Right Reverse"]]
    story.append(styled_table(bts_data,[3*cm,2*cm,3*cm,2.5*cm,W-10.5*cm]))
    story.append(Paragraph("WARNING: Always connect a common ground between the Pi, BTS7960 boards, and battery negative terminal. Floating grounds will cause erratic motor behavior or GPIO damage.", s['warning']))
    story.append(Spacer(1,0.2*cm))
    story.append(Paragraph("4.6 Camera Connection", s['h2']))
    story.append(Paragraph("The Raspberry Pi Camera v2 connects to the CSI ribbon cable port on the Pi 4. A USB webcam is automatically detected as fallback via cv2.VideoCapture() if the CSI camera is absent. The camera is managed as a singleton in hardware.py using the Camera.get_instance() pattern to prevent resource locks.", s['body']))
    story.append(PageBreak())

    # Section 5 — Software Modules
    story.append(Paragraph("5. Software Modules — Design &amp; Code Explanation", s['h1']))

    # 5.1
    story.append(Paragraph("5.1 config.py — Global Configuration &amp; Constants", s['h2']))
    story.append(Paragraph("Purpose: Single source of truth for all system constants. Every parameter — pin numbers, thresholds, file paths, timing intervals — is defined here. No other module stores configuration values locally.", s['body']))
    cfg_data=[["Constant / Group","Value / Range","Explanation"],["PIN_DHT_DATA","GPIO 4","Data pin for DHT11/22 sensor"],["PIN_RELAY_PUMP","GPIO 17","Active-LOW relay for water pump"],["PIN_RELAY_CUTTER","GPIO 27","Active-LOW relay for grass cutter"],["PIN_BUZZER / PIN_LED","GPIO 22, 23","Buzzer and LED indicator pins"],["PIN_LEFT_RPWM/LPWM","GPIO 5, 6","BTS7960 #1 PWM pins (left motors)"],["PIN_RIGHT_RPWM/LPWM","GPIO 13, 19","BTS7960 #2 PWM pins (right motors)"],["MOISTURE_LOW / HIGH","35% / 65%","Hysteresis band for irrigation control"],["PUMP_MAX_RUNTIME","60 seconds","Safety cutoff for stuck pump / dry tank"],["PUMP_COOLDOWN","120 seconds","Minimum off-time between irrigation cycles"],["CUTTER_INTERVAL","3600 seconds","1 hour between automatic grass trim runs"],["CUTTER_DURATION","30 seconds","Duration of each trim cycle"],["CONFIDENCE_THRESHOLD","0.70 (70%)","Minimum AI confidence to report disease detection"],["LAPLACIAN_VAR_MIN","12.0","Blur detection threshold (Laplacian variance)"],["BRIGHTNESS_MIN/MAX","15 / 250","Luminance range for valid leaf images"],["GREEN_PIXEL_THRESHOLD","0.15 (15%)","Min green pixels in frame to trigger auto-scan"],["ACTIVE_MODEL_PROFILE","'custom' or 'plantvillage'","Selects which TFLite model to load at startup"],["AWS_API_URL","API Gateway URL","AWS endpoint for telemetry push"],["AWS_RELAY_INTERVAL","5 seconds","Interval between cloud telemetry pushes"]]
    story.append(styled_table(cfg_data,[4*cm,4*cm,W-8*cm]))
    story.append(Paragraph("The load_runtime_config() function reads runtime_config.json at startup, allowing moisture thresholds saved from the dashboard to persist across reboots.", s['note']))
    story.append(Spacer(1,0.3*cm))

    # 5.2
    story.append(Paragraph("5.2 hardware.py — Hardware Driver Layer (HAL)", s['h2']))
    story.append(Paragraph("Purpose: The Hardware Abstraction Layer. This is the ONLY module that touches GPIO, SPI, I2C, or physical device registers. All other modules receive hardware objects via dependency injection.", s['body']))
    story.append(Paragraph("Key Classes &amp; Functions:", s['h3']))
    hw_classes=[("initialize_hardware_libs(simulate)","Imports all hardware libraries (RPi.GPIO, picamera2, adafruit_dht, smbus2, cv2). If simulate=False and RPi.GPIO is absent, raises RuntimeError — no silent fallbacks."),("ADS1115ADC","16-bit I2C ADC driver using raw smbus2 register writes. Reads 4 analog channels. Used for soil moisture (A0) and water level (A1)."),("MCP3008ADC","10-bit SPI ADC fallback driver using spidev. Activated if ADS1115 is not configured."),("SoilSensor","Wraps ADS1115 Channel 0. Calibrates raw 16-bit counts to 0-100% moisture. Rejects implausible readings."),("WaterLevelSensor","Wraps ADS1115 Channel 1. Converts raw counts to reservoir fill percentage (0-100%)."),("DHTSensor","Reads temperature and humidity from DHT11/22 via adafruit-circuitpython-dht. Returns last valid reading on CRC error."),("GPSSensor","Reads NMEA sentences from NEO-7M GPS via PySerial on /dev/serial0. Parses $GPRMC for lat/lon/speed. Returns fix age for staleness rejection."),("CompassSensor","Reads HMC5883L magnetometer via I2C. Computes heading in degrees (0-360) with optional declination correction."),("Relay","Controls 2-channel 5V relay module via GPIO (Active LOW). pump_on(), pump_off(), cutter_on(), cutter_off() with safety interlock preventing simultaneous operation."),("Motors","Controls 4 drive motors via 2x BTS7960 using software PWM at 1kHz. forward(), reverse(), turn_left(), turn_right(), stop()."),("Camera","Singleton camera manager. Supports CSI (picamera2) with USB webcam fallback. Exposes capture_frame() returning numpy BGR array."),("Alerts","Manages buzzer and LED. alert_disease() triggers beep + LED flash. alert_water_low() triggers sustained buzzer.")]
    for name,desc in hw_classes:
        story.append(Paragraph(f"<b>{name}:</b> {desc}", s['bullet']))
    story.append(Paragraph("Simulation Mode: When --simulate CLI flag is passed, all hardware classes return realistic mock data (random moisture %, simulated GPS coordinates). A persistent SIMULATION MODE warning banner appears in logs and dashboard.", s['note']))
    story.append(PageBreak())

    # 5.3
    story.append(Paragraph("5.3 irrigation.py — Irrigation Controller", s['h2']))
    story.append(Paragraph("Design Pattern: Hysteresis-based on/off control with safety interlocks. Called every 3 seconds from the Control Loop.", s['body']))
    for step,desc in [("Step 1 — Read Sensor","Calls SoilSensor.read_percentage(). If moisture_pct is None (implausible ADC reading), cycle is skipped and event logged."),("Step 2 — Active Irrigation Check","If pump is ON: checks if moisture >= 65% (normal stop) or runtime > 60s (safety timeout stop)."),("Step 3 — Activation Decision","If pump OFF and moisture < 35%: checks cooldown >= 120s since last off then starts pump. Before starting, calls motors.stop() to halt chassis."),("Step 4 — Normal State","If moisture 35%-65%: status = MOISTURE_OK, no action.")]:
        story.append(Paragraph(f"<b>{step}:</b> {desc}", s['bullet']))
    story.append(Paragraph("All irrigation cycle events (start time, end time, duration, initial moisture, final moisture, trigger type) are logged to the SQLite database for efficiency analysis.", s['note']))
    story.append(Spacer(1,0.3*cm))

    # 5.4
    story.append(Paragraph("5.4 cutter.py — Grass Trimmer Scheduler", s['h2']))
    story.append(Paragraph("Schedules automated grass trimming every CUTTER_INTERVAL (3600s = 1 hour) for CUTTER_DURATION (30s). Before energizing the cutter relay, chassis motors are hard-stopped to prevent voltage sag on the shared 12V bus.", s['body']))
    story.append(Paragraph("Safety Interlocks:", s['h3']))
    for safety in ["Refuses to start if CUTTER_ENABLED = False in config.py.","Refuses to start if water pump is currently active (prevents simultaneous high-current loads).","Re-enforces motors.stop() on every control loop tick while cutting is active.","Emergency stop method immediately de-energizes relay with no delay."]:
        story.append(Paragraph(f"• {safety}", s['bullet']))
    story.append(Spacer(1,0.3*cm))

    # 5.5
    story.append(Paragraph("5.5 navigation.py — GPS Waypoint Navigation", s['h2']))
    story.append(Paragraph("Implements GPS + compass guided autonomous navigation. The rover moves in short, safe bursts (NAV_DRIVE_SLICE = 1.0s, NAV_TURN_SLICE = 0.2s) and stops after each slice to re-check GPS and heading.", s['body']))
    story.append(Paragraph("Navigation Algorithm (execute_waypoint_step):", s['h3']))
    for i,step in enumerate(["Stop motors first (safety).","Request fresh GPS fix; reject if fix age > 5 seconds.","Compute great-circle distance and bearing to current waypoint using Haversine formula.","If distance <= 2.5m (NAV_WAYPOINT_REACHED_M) mark waypoint reached, advance index.","Compute heading error = bearing minus current_heading (wrapped to -180 to +180 degrees).","If heading error > 12 degrees (NAV_HEADING_TOLERANCE_DEG) pivot left/right for 0.2s then stop.","If heading error <= 12 degrees drive forward for 1.0s then stop.","Return status dict (action, distance, bearing, heading_error)."],1):
        story.append(Paragraph(f"{i}. {step}", s['bullet']))
    story.append(Spacer(1,0.3*cm))

    # 5.6
    story.append(Paragraph("5.6 disease_detect.py — AI Plant Disease Detection Pipeline", s['h2']))
    story.append(Paragraph("Runs TensorFlow Lite inference on captured leaf images. Supports three TFLite runtime backends: tflite_runtime (legacy), ai_edge_litert (new Raspberry Pi OS package), and tensorflow.lite (full TensorFlow fallback).", s['body']))
    story.append(Paragraph("Inference Pipeline Steps:", s['h3']))
    for step,desc in [("Image Quality Gate","Checks Laplacian variance (blur < 12.0) and mean luminance (outside 15-250 range). Rejects bad frames with RETAKE_NEEDED flag — NOT a disease alert."),("Green Pixel Verification","HSV-based green pixel count must exceed 15% of frame to confirm a leaf is present before running inference."),("Segmentation Consensus","Image divided into 3x3 grid (9 segments). Each classified independently. Disease alert only if diseased segments > 50% (majority voting) reducing false positives."),("TFLite Inference","Image resized to 224x224, normalized to float32 [0.0, 1.0]. Interpreter.invoke() runs on XNNPACK delegate."),("Confidence Gate","Only softmax confidence >= 70% accepted. Below this threshold: status = LOW_CONFIDENCE."),("Result Enrichment","Matched label looked up in disease_db.py for: common name, affected crop, cause, symptoms, treatment."),("Alert & Logging","If disease detected: buzzer alert triggered, result JPEG saved to /static/scans/, full result logged to SQLite DB.")]:
        story.append(Paragraph(f"<b>{step}:</b> {desc}", s['bullet']))
    story.append(Paragraph("TFLite import fallback chain in disease_detect.py lines 27-44:", s['h3']))
    story.append(Paragraph("try: import tflite_runtime.interpreter as tflite  # legacy Pi\nexcept: pass\nif tflite is None:\n    try: import ai_edge_litert.interpreter as tflite  # new Pi OS\n    except: pass\nif tflite is None:\n    try: import tensorflow.lite as tflite  # full TF\n    except: tflite = None", s['code']))
    story.append(PageBreak())

    # 5.7
    story.append(Paragraph("5.7 disease_db.py — Plant Disease Knowledge Base", s['h2']))
    story.append(Paragraph("A static Python dictionary containing disease metadata for all model classes: common name, affected crop, pathogen type, cause, symptoms, and recommended treatment.", s['body']))
    db_data=[["Model Class Label","Common Name","Pathogen Type","Treatment Summary"],["Tulsi___Healthy","Tulsi (Healthy)","—","No treatment needed"],["Tulsi___Infected","Tulsi Leaf Spot / Blight","Fungal (Colletotrichum / Alternaria)","Neem oil spray, remove infected leaves, improve drainage"],["Tulsi___Infested","Tulsi Pest Infestation","Insect / Mite","Neem oil, insecticidal soap, manual pest removal"],["Tulsi___Wilting","Tulsi Wilt / Root Rot","Fungal (Fusarium) / Overwatering","Reduce watering, improve drainage, fungicide drench"],["background_not_a_leaf","Non-plant background","—","Move camera closer to plant"],["Tomato___Early_blight","Early Blight","Fungal (Alternaria solani)","Copper-based fungicide, crop rotation"],["Tomato___Late_blight","Late Blight","Oomycete (Phytophthora infestans)","Systemic fungicide, destroy infected plants"],["Tomato___healthy","Healthy Tomato","—","—"],["Potato___Early_blight","Early Blight (Potato)","Fungal (Alternaria solani)","Fungicide spray, remove affected leaves"],["Potato___Late_blight","Late Blight (Potato)","Oomycete (Phytophthora infestans)","Metalaxyl fungicide, no overhead irrigation"],["Potato___healthy","Healthy Potato","—","—"],["Pepper__bell___Bacterial_spot","Bacterial Spot","Bacterial (Xanthomonas)","Copper bactericide, crop rotation"],["Pepper__bell___healthy","Healthy Bell Pepper","—","—"]]
    story.append(styled_table(db_data,[4.5*cm,3*cm,4*cm,W-11.5*cm]))
    story.append(Spacer(1,0.3*cm))

    # 5.8
    story.append(Paragraph("5.8 main.py — System Supervisor &amp; Finite State Machine", s['h2']))
    story.append(Paragraph("Purpose: Entry point and central coordinator. Launches all threads, runs the FSM control loop, handles OS signals for graceful shutdown.", s['body']))
    story.append(Paragraph("FSM States:", s['h3']))
    fsm_data=[["State","Description","Transitions To"],["BOOT","System startup — hardware library imports, logging setup","SELF_TEST"],["SELF_TEST","Verifies GPIO, ADC, camera, TFLite model, database. Refuses actuation if any test fails.","IDLE (pass) or SAFE_STATE (fail)"],["IDLE","All sensors active. Awaiting trigger: low moisture, cutter interval, green plant detection, manual API command.","IRRIGATING / CUTTING / NAVIGATING / SCANNING"],["IRRIGATING","Pump is ON. Chassis is halted. Monitors moisture to reach 65% or timeout.","IDLE"],["CUTTING","Cutter relay ON. Chassis halted. Times 30s trim cycle.","IDLE"],["NAVIGATING","GPS+compass guided motion toward next waypoint. One burst slice per control loop tick.","IDLE (waypoint reached or no GPS fix)"],["SCANNING","Disease scanner thread active. Captures frame, runs inference, logs result.","IDLE"],["SAFE_STATE","Emergency or critical failure. All actuators de-energized. Only monitoring active.","IDLE (manual recovery)"]]
    story.append(styled_table(fsm_data,[2.5*cm,6*cm,W-8.5*cm]))
    story.append(Paragraph("Signal Handling:", s['h3']))
    for sig in ["SIGTERM (systemd stop): Calls emergency_stop() de-energizes all relays/motors joins all threads exits cleanly.","SIGINT (Ctrl+C): Same as SIGTERM. No data corruption — SQLite writes are transactional.","Watchdog: Monitors control loop heartbeat timestamp. If stale > 30s logs WATCHDOG_TIMEOUT alert."]:
        story.append(Paragraph(f"• {sig}", s['bullet']))
    story.append(PageBreak())

    # 5.9
    story.append(Paragraph("5.9 app.py — Flask REST API Server", s['h2']))
    story.append(Paragraph("Hosts a Flask web server on port 5000. Provides REST endpoints for the dashboard frontend and external integrations. All state is read from/written to a shared telemetry_cache dict (thread-safe with RLock).", s['body']))
    api_data=[["Method","Endpoint","Description"],["GET","/api/telemetry","Returns current telemetry JSON: moisture, temperature, humidity, GPS, heading, FSM state, scan result, water level"],["POST","/api/scan","Triggers an immediate disease scan (background thread). Returns scan ID."],["GET","/api/scan/result","Returns latest disease scan result with confidence, label, treatment, image path."],["POST","/api/manual/pump/on","Manually starts water pump (with safety checks)"],["POST","/api/manual/pump/off","Manually stops water pump"],["POST","/api/manual/cutter/on","Manually starts grass cutter (with safety checks)"],["POST","/api/manual/cutter/off","Manually stops grass cutter"],["POST","/api/navigate/waypoint","Adds a GPS waypoint to the navigation mission"],["POST","/api/navigate/clear","Clears all waypoints and halts navigation"],["GET","/api/logs","Returns last 100 system log events from SQLite DB"],["POST","/api/config/thresholds","Updates moisture low/high thresholds at runtime (saved to runtime_config.json)"],["GET","/api/disease/library","Returns the full disease knowledge base from disease_db.py"],["GET","/","Serves the main dashboard index.html"]]
    story.append(styled_table(api_data,[1.5*cm,5.5*cm,W-7*cm]))
    story.append(Spacer(1,0.3*cm))

    # 5.10
    story.append(Paragraph("5.10 aws_relay.py — AWS Cloud Integration", s['h2']))
    story.append(Paragraph("Background thread that periodically (every 5 seconds) HTTP POSTs telemetry to AWS API Gateway. Also polls the /command endpoint to receive remote control commands from the cloud dashboard.", s['body']))
    aws_data=[["Pi to AWS Endpoint","Direction","Payload","AWS Service"],["POST /telemetry","Pi to Cloud","Full sensor JSON","API Gateway to Lambda to S3 (state.json)"],["GET /command","Pi from Cloud","Command string (e.g. pump_on)","API Gateway to Lambda to S3 (command.json)"],["POST /scan","Pi to Cloud","JPEG image (base64) + scan result JSON","API Gateway to Lambda to S3 (/scans/)"],["POST /snapshot","Pi to Cloud","JPEG camera snapshot (base64) every 60s","API Gateway to Lambda to S3 (/snapshots/)"]]
    story.append(styled_table(aws_data,[3.5*cm,2.5*cm,5*cm,W-11*cm]))
    story.append(Spacer(1,0.3*cm))

    # 5.11
    story.append(Paragraph("5.11 database.py — SQLite Persistence Layer", s['h2']))
    story.append(Paragraph("Manages a local SQLite database at logs/agronex.db. All writes are thread-safe (threading.Lock). Key tables:", s['body']))
    for tname,desc in [("system_events","Logs: timestamp, event_type (FSM_TRANSITION, IRRIGATION_START, CUTTER_START, PUMP_TIMEOUT etc.), severity (INFO/WARNING/ERROR), message, simulated flag."),("irrigation_events","Logs each complete pump cycle: start/end ISO timestamps, duration seconds, start moisture %, end moisture %, trigger type."),("disease_scans","Logs each disease inference: timestamp, label, common_name, confidence, is_healthy flag, image_path, treatment recommendation."),("telemetry_snapshots","Optional periodic snapshots of full sensor telemetry for historical analysis.")]:
        story.append(Paragraph(f"<b>{tname}:</b> {desc}", s['bullet']))
    story.append(PageBreak())

    # Section 6 — AI Training
    story.append(Paragraph("6. AI Model Training Pipeline", s['h1']))
    story.append(Paragraph("Two training scripts generate TFLite models for deployment on Raspberry Pi 4.", s['body']))
    story.append(Paragraph("6.1 train_custom_plant_model.py — Custom Tulsi Trainer", s['h2']))
    story.append(Paragraph("Trains a MobileNetV2-based transfer learning model on a local dataset collected using the Pi camera. Dataset is organized into class subdirectories under field_dataset/.", s['body']))
    for step,desc in [("Dataset Organization","Place images in field_dataset/class_name/ directories. Recommended classes: Tulsi___Healthy, Tulsi___Infected, Tulsi___Infested, Tulsi___Wilting, background_not_a_leaf."),("Data Augmentation","RandomFlip, RandomRotation, RandomZoom, RandomBrightness applied on-the-fly via tf.keras.Sequential augmentation pipeline."),("Base Model","MobileNetV2 pretrained on ImageNet (include_top=False). Input shape: 224x224x3. Base layers frozen for first 10-15 epochs."),("Classification Head","GlobalAveragePooling2D to Dropout(0.4) to Dense(128, ReLU) to Dropout(0.3) to Dense(num_classes, Softmax)."),("Fine-tuning","After initial training, last 50 layers of MobileNetV2 unfrozen, retrained with lr=1e-5."),("Quantization & Export","Model converted to float32 TFLite using TFLiteConverter. Saved as models/custom_plant_model.tflite. Labels saved as models/custom_labels.txt.")]:
        story.append(Paragraph(f"<b>{step}:</b> {desc}", s['bullet']))
    story.append(Paragraph("Training Command: python train_custom_plant_model.py", s['code']))
    story.append(Paragraph("6.2 train_plant_disease_model.py — PlantVillage Broad Crop Trainer", s['h2']))
    story.append(Paragraph("Trains on the PlantVillage dataset (plantdisease.zip) for 8 classes across Tomato, Potato, Bell Pepper. Same MobileNetV2 architecture.", s['body']))
    story.append(Paragraph("Training Command: python train_plant_disease_model.py", s['code']))
    story.append(Paragraph("Both scripts output to models/ directory. Active model is selected by setting AGRONEX_MODEL_PROFILE=custom (default) or AGRONEX_MODEL_PROFILE=plantvillage as an environment variable before launching main.py.", s['note']))
    story.append(Paragraph("6.3 Model Deployment on Raspberry Pi", s['h2']))
    for i,step in enumerate(["Train model on Windows/Linux PC (GPU recommended).","Copy models/ folder to Raspberry Pi: scp -r models/ nikhil@<pi-ip>:~/Major project/models/","Verify with: python3 test_disease_camera.py","Set model profile if needed: export AGRONEX_MODEL_PROFILE=custom","Launch full system: python3 main.py"],1):
        story.append(Paragraph(f"{i}. {step}", s['bullet']))
    story.append(PageBreak())

    # Section 7 — AWS
    story.append(Paragraph("7. AWS Cloud Architecture", s['h1']))
    story.append(Paragraph("AgroNex-Pi uses a serverless AWS architecture for cloud telemetry, remote control, and scan image storage.", s['body']))
    aws_arch=[["AWS Service","Configuration","Function"],["API Gateway","REST API, ap-south-1 region, CORS enabled","Entry point for all Pi HTTP POST/GET requests"],["AWS Lambda","Python 3.11 runtime, ~128MB memory","Processes telemetry payloads, reads/writes S3"],["Amazon S3","Private bucket: agronex-dashboard","Stores state.json, command.json, scan JPEGs, snapshot JPEGs, static dashboard"],["S3 Static Hosting","index.html + CSS/JS served from S3","Public-facing dashboard accessible from any browser"],["CloudWatch Logs","Automatic Lambda log retention","Debugging Lambda function errors"]]
    story.append(styled_table(aws_arch,[3*cm,4.5*cm,W-7.5*cm]))
    story.append(Paragraph("Data Flow:", s['h3']))
    for item in ["Pi to Cloud (Telemetry): Every 5 seconds, aws_relay.py POSTs JSON to /telemetry. Lambda stores it as state.json in S3.","Cloud to Pi (Command): Every 5 seconds, aws_relay.py GETs /command. Lambda reads command.json from S3. If command exists and unprocessed, Pi executes it.","Pi to Cloud (Scan Image): After each disease scan, aws_relay.py POSTs the JPEG (base64-encoded) and scan result JSON to /scan.","Pi to Cloud (Snapshot): Every 60 seconds, a JPEG snapshot from the camera is uploaded to S3 /snapshots/ for live monitoring.","Cloud Dashboard to S3: The public S3-hosted dashboard fetches state.json every 3 seconds to display live telemetry."]:
        story.append(Paragraph(f"• {item}", s['bullet']))
    story.append(PageBreak())

    # Section 8 — Dashboard
    story.append(Paragraph("8. Web Dashboard (index.html)", s['h1']))
    story.append(Paragraph("The AgroNex-Pi dashboard is a single-page HTML/CSS/JavaScript application hosted on Amazon S3. It provides real-time telemetry display, manual control buttons, disease scan history, farmer knowledge blog, and live map integration.", s['body']))
    for name,desc in [("Overview Cards","Live tiles for: Soil Moisture %, Water Level %, Temperature, Humidity, GPS coordinates, Heading (animated compass), FSM state, Pump status, Cutter status."),("Disease Detection Tab","Latest scan image, detected disease label, confidence bar, treatment recommendation. Retake/Low-Confidence badges on quality gate rejection."),("Scan Gallery","Grid of recent scan JPEG thumbnails from S3 /scans/ folder with timestamp and label overlay."),("Navigation Tab","Interactive map (Leaflet.js) with current GPS position, waypoint placement, and route visualization."),("Disease Library Tab","Full searchable encyclopedia of all supported plant diseases with cause, symptoms, treatment."),("Farmer Blogs Tab","Educational articles and farming tips related to crop disease management and autonomous farming."),("Logs Tab","Live system event log from /api/logs — FSM transitions, irrigation events, sensor errors."),("Manual Controls","Buttons for: Trigger Scan, Pump ON/OFF, Cutter ON/OFF, Set Waypoint, Clear Waypoints.")]:
        story.append(Paragraph(f"<b>{name}:</b> {desc}", s['bullet']))
    story.append(PageBreak())

    # Section 9 — Working Flow
    story.append(Paragraph("9. System Working — End-to-End Flow", s['h1']))
    story.append(Paragraph("9.1 Startup Sequence", s['h2']))
    for i,step in enumerate(["User runs: python3 main.py (or systemd starts it on boot)","initialize_hardware_libs() imports all drivers. Fails loudly if Pi hardware is missing without --simulate.","GPIO BCM mode set. All relay outputs initialized to OFF (HIGH = deactivated, Active LOW relay).","run_self_test() verifies: GPIO, ADC, DHT, GPS, Compass, Camera, TFLite model, SQLite DB.","Flask server thread starts on port 5000.","AWS Relay thread starts (if AGRONEX_AWS_URL is configured).","Watchdog thread starts.","Control Loop thread starts (3-second poll cycle).","FSM transitions: BOOT to SELF_TEST to IDLE."],1):
        story.append(Paragraph(f"{i}. {step}", s['bullet']))
    story.append(Paragraph("9.2 Normal Operation (IDLE / MONITORING Cycle)", s['h2']))
    story.append(Paragraph("Every 3 seconds, the Control Loop performs:", s['body']))
    for i,step in enumerate(["Read all sensors: soil moisture, water level, DHT temp/humidity, GPS fix, compass heading.","Update telemetry cache (for Flask API and AWS relay).","Evaluate Irrigation: If moisture < 35%, start pump cycle. If irrigation active, check completion.","Evaluate Cutter: If 3600s have elapsed since last trim, start 30s cutter cycle.","Evaluate Navigation: If waypoints are configured, execute one GPS/compass guided motion slice.","Evaluate Auto-Scan: If green_pixel_fraction > 15% and cooldown elapsed, trigger disease scanner thread.","Push telemetry to AWS (async, via AWSRelay background thread)."],1):
        story.append(Paragraph(f"{i}. {step}", s['bullet']))
    story.append(Paragraph("9.3 Disease Scan Flow (Auto or Manual)", s['h2']))
    for i,step in enumerate(["Trigger: auto (green pixel detection) or manual (dashboard button / API POST /api/scan).","Camera captures 224x224 frame (Picamera2 CSI or USB webcam fallback).","Quality Gate: Laplacian variance check (blur) and luminance check. If rejected: RETAKE_NEEDED (not a false disease alert).","Green pixel mask (HSV) applied: confirms leaf is in frame.","Image split into 3x3 grid (9 segments). Each segment classified by TFLite model.","Majority voting: if diseased_count > 4 (>50%) then DISEASE_DETECTED. Else HEALTHY.","Confidence gate: must be >= 70%.","Result: label, confidence, common_name, cause, treatment saved to DB + S3.","Alert: buzzer + LED if disease detected."],1):
        story.append(Paragraph(f"{i}. {step}", s['bullet']))
    story.append(PageBreak())

    # Section 10 — Safety
    story.append(Paragraph("10. Safety Mechanisms &amp; Interlocks", s['h1']))
    safety_data=[["Safety Interlock","Mechanism","Implemented In"],["Pump Dry-Run Prevention","Checks WATER_CRITICAL_LOW (20%). If reservoir < 20%, pump is NOT started even if soil is dry.","irrigation.py + WaterLevelSensor"],["Pump Max Runtime","Pump auto-shuts off after 60s (PUMP_MAX_RUNTIME) regardless of moisture.","irrigation.py"],["Pump Cooldown","120s minimum between pump cycles (PUMP_COOLDOWN). Protects relay contacts and pump motor.","irrigation.py"],["Cutter + Pump Interlock","Cutter refuses to start if pump is ON. Pump refuses manual start if cutter is ON.","cutter.py + irrigation.py"],["Chassis Stop During Actuation","motors.stop() called before starting pump or cutter. Chassis only moves after actuation completes.","irrigation.py + cutter.py"],["False-Positive Suppression","Disease alert only if >50% of image segments are diseased (majority voting).","disease_detect.py"],["Image Quality Gate","Blurry or overexposed frames rejected with RETAKE_NEEDED (not a false positive).","disease_detect.py"],["Confidence Gate","AI confidence must be >= 70% for any diagnosis to be reported.","disease_detect.py"],["SIGTERM/SIGINT Handler","Clean shutdown: emergency_stop() all GPIO LOW threads joined exit. No partial hardware states.","main.py"],["Watchdog Timer","If control loop heartbeat stale > 30s logs WATCHDOG_TIMEOUT.","main.py"],["Simulation Mode Banner","If --simulate used, persistent WARNING banner prevents accidental production use.","hardware.py + app.py"]]
    story.append(styled_table(safety_data,[4*cm,6*cm,W-10*cm]))
    story.append(PageBreak())

    # Section 11 — Testing
    story.append(Paragraph("11. Testing Scripts", s['h1']))
    tests=[("test_all_sensors.py","Reads all sensors simultaneously and prints formatted output. Use to verify hardware connections after wiring."),("test_disease_camera.py","Interactive camera tester + disease inference. Shows live camera feed, captures frame on ENTER, runs full disease detection pipeline."),("test_motors.py","Tests all 4 motor directions (forward, reverse, left, right) in sequence. Verify wheel direction before autonomous navigation."),("test_relay.py","Cycles pump and cutter relays ON/OFF. Verify relay click sounds and actuator response."),("test_dht.py","Reads DHT11/22 temperature and humidity 10 times with 2s intervals. Checks for CRC errors."),("test_soil.py","Reads soil moisture ADC value repeatedly and computes percentage. Shows raw ADC + calibrated %."),("test_water.py","Reads HW-038 water level sensor continuously. Shows raw ADC and reservoir fill %."),("test_camera.py","Simple camera connectivity test. Captures one frame and saves test_capture.jpg."),("test_compass_raw.py","Reads raw HMC5883L X/Y/Z values and computed heading at 1Hz. Use to calibrate compass declination."),("test_navigation_sensors.py","Reads GPS + compass together. Computes bearing and distance to a hardcoded test waypoint."),("test_alert.py","Triggers buzzer and LED alert patterns. Tests audio and visual alert hardware."),("verify_runtime_telemetry.py","Connects to Flask API on localhost:5000 and prints full telemetry JSON. Verifies main.py is running.")]
    test_data=[["Script","Purpose"]]+[[n,d] for n,d in tests]
    story.append(styled_table(test_data,[5.5*cm,W-5.5*cm]))
    story.append(PageBreak())

    # Section 12 — Issues
    story.append(Paragraph("12. Known Issues &amp; Future Work", s['h1']))
    story.append(Paragraph("12.1 Known Limitations", s['h2']))
    for issue in ["No obstacle detection — a human safety observer is mandatory at all times.","GPS accuracy is plus or minus 2-5m (consumer NEO-7M). Waypoint arrival radius of 2.5m compensates.","No wheel encoders — indoor navigation without GPS is not possible.","Disease model is limited to plants it was trained on. Novel diseases will produce incorrect results.","Simultaneous inference on multiple plants is not supported.","AWS cloud relay requires internet connectivity (all features remain functional offline via local Flask dashboard)."]:
        story.append(Paragraph(f"• {issue}", s['bullet']))
    story.append(Paragraph("12.2 Planned Future Enhancements", s['h2']))
    for f in ["Ultrasonic obstacle detection (HC-SR04) with automatic path re-planning.","YOLO-based real-time object detection for plant identification and disease localization.","Battery voltage monitoring via ADC spare channels (A2/A3) with low-battery shutdown.","Multi-plant scheduling: GPS-mapped plant beds with per-plant disease tracking history.","Bluetooth/Wi-Fi Direct mode for dashboard access without internet (Pi AP mode).","Rain sensor integration to inhibit irrigation during rainfall.","Edge TPU (Google Coral) support for 5x faster inference with INT8 quantized models.","OTA firmware updates via AWS S3 deployment pipeline."]:
        story.append(Paragraph(f"• {f}", s['bullet']))
    story.append(Spacer(1,0.5*cm))
    story.append(HRFlowable(width="100%",thickness=2,color=GREEN_MID))
    story.append(Spacer(1,0.2*cm))
    story.append(Paragraph("AgroNex-Pi — Full Project Technical Report | For Academic Use Only", s['caption']))

    doc.build(story,onFirstPage=report_page,onLaterPages=report_page)
    print(f"Full Project Report saved: {out}")
    return out


# ─── IEEE RESEARCH PAPER ─────────────────────────────────────────────────────
def build_ieee_paper():
    out = os.path.join(BASE_DIR, "AgroNex_Pi_IEEE_Research_Paper.pdf")
    doc = SimpleDocTemplate(out,pagesize=letter,rightMargin=0.75*inch,leftMargin=0.75*inch,topMargin=1*inch,bottomMargin=1*inch,title="AgroNex-Pi IEEE Research Paper",author="AgroNex-Pi Research Team")
    s = make_ieee_styles()
    story = []
    W_letter = letter[0] - 1.5*inch

    story.append(Paragraph("AgroNex-Pi: Design and Implementation of an Autonomous Smart Agricultural Robot with Edge AI Plant Disease Detection, GPS Navigation, and Cloud Telemetry", s['title']))
    story.append(Spacer(1,0.15*inch))
    story.append(Paragraph("Nikhil [Author Name], [Co-Author 1], [Co-Author 2], [Co-Author 3]", s['authors']))
    story.append(Paragraph("Department of [Electronics/Computer Engineering], [Institute Name], [City, State, Country]<br/>Email: [author@institute.edu]", s['affil']))
    story.append(HRFlowable(width="100%",thickness=1,color=BLACK))
    story.append(Spacer(1,0.1*inch))

    story.append(Paragraph("Abstract", s['abstract_head']))
    story.append(Paragraph("This paper presents AgroNex-Pi, a fully autonomous smart agricultural robot built on the Raspberry Pi 4 platform that integrates five functional subsystems: real-time soil moisture sensing with automated drip irrigation, scheduled grass trimming, GPS + compass guided waypoint navigation, edge AI plant disease detection using TensorFlow Lite MobileNetV2, and live cloud telemetry via Amazon Web Services (AWS). The plant disease detection subsystem employs a dual-model architecture capable of classifying five Tulsi (Ocimum tenuiflorum) disease states and eight PlantVillage crop classes (Tomato, Potato, Bell Pepper) with a minimum confidence threshold of 70% and a majority-voting image segmentation scheme to suppress false positives. All subsystems are coordinated by a multi-threaded Python supervisor implementing a Finite State Machine (FSM) with hardware interlocks to prevent simultaneous high-current actuator operation. A serverless AWS stack (API Gateway + Lambda + S3) provides remote monitoring and bidirectional control. Experimental results demonstrate [INSERT RESULTS: classification accuracy, irrigation response time, navigation precision]. The system achieves [INSERT PERFORMANCE METRICS] making it suitable for deployment in small-scale farms, home gardens, and nurseries.", s['abstract']))
    story.append(Paragraph("<b>Index Terms</b> — Autonomous Agricultural Robot, Edge AI, TensorFlow Lite, Plant Disease Detection, Raspberry Pi, IoT, GPS Navigation, Smart Irrigation, MobileNetV2, Transfer Learning.", s['keywords']))
    story.append(HRFlowable(width="100%",thickness=1,color=BLACK))
    story.append(Spacer(1,0.1*inch))

    story.append(Paragraph("I. INTRODUCTION", s['h1']))
    story.append(Paragraph("Agriculture remains the backbone of economies in developing nations, yet it faces mounting challenges including labor shortages, water scarcity, and the rapid spread of plant diseases. According to the Food and Agriculture Organization (FAO), plant pathogens cause annual crop losses estimated at 10-40% of global food production [1]. Early detection and intervention are critical but traditionally require expert agronomists visiting fields regularly — a resource constraint that small-scale farmers cannot sustain.", s['body']))
    story.append(Paragraph("The emergence of low-cost single-board computers (SBCs) such as the Raspberry Pi 4, combined with advances in lightweight neural network architectures like MobileNetV2 [2] and the TensorFlow Lite runtime, has made edge AI inference feasible on embedded systems with watt-level power budgets. Simultaneously, cloud platforms like AWS provide serverless infrastructure for remote monitoring without requiring dedicated server maintenance.", s['body']))
    story.append(Paragraph("This work presents AgroNex-Pi, which integrates soil sensing, automated irrigation, grass trimming, GPS-guided navigation, and AI-powered plant disease detection into a single autonomous rover. The system targets Tulsi (Holy Basil, Ocimum tenuiflorum) as the primary disease detection subject — a plant of significant cultural and medicinal importance in South Asia — while also supporting broad-crop PlantVillage classification.", s['body']))
    story.append(Paragraph("A. Contributions", s['h2']))
    story.append(Paragraph("The principal contributions of this work are:", s['body_noindent']))
    for c in ["1) A fully integrated autonomous agricultural rover combining five subsystems on the Raspberry Pi 4 platform.","2) A dual-model TFLite architecture with a switchable model profile supporting local plants (Tulsi) and broad agricultural crops.","3) A majority-voting image segmentation scheme requiring >50% of image segments to be diseased before alerting, reducing false positives.","4) A hardware interlock system preventing simultaneous high-current actuator operation (pump + cutter + motors).","5) A serverless AWS telemetry stack enabling remote monitoring and bidirectional control from any internet-connected device."]:
        story.append(Paragraph(c, s['body_noindent']))
    story.append(Spacer(1,0.1*inch))

    story.append(Paragraph("II. RELATED WORK", s['h1']))
    story.append(Paragraph("Automated agricultural robots have been explored extensively in precision agriculture research. Bac et al. [3] demonstrated robotic harvesting in greenhouse environments using visual servoing but required structured environments with known plant geometry. Mohanty et al. [4] showed that deep convolutional neural networks trained on the PlantVillage dataset could achieve greater than 99% accuracy in controlled laboratory conditions, though real-field performance remained lower due to background clutter and lighting variation.", s['body']))
    story.append(Paragraph("Smartphone-based disease diagnosis apps (e.g., Plantix, PlantSnap) deploy cloud inference models requiring internet connectivity for every prediction. In contrast, edge deployment on-device eliminates latency and operates offline. Howard et al. [2] introduced MobileNetV2, a depthwise separable convolution architecture optimized for mobile and embedded deployment, achieving ImageNet accuracy competitive with VGG-16 at a fraction of the computational cost.", s['body']))
    story.append(Paragraph("IoT-based irrigation systems [5] have demonstrated 30-40% water savings over timer-based systems, while GPS-guided agricultural robots [6] have shown promise for field navigation. However, prior work has not integrated all five subsystems into a single embedded platform at low cost. AgroNex-Pi addresses this gap.", s['body']))
    story.append(Spacer(1,0.1*inch))

    story.append(Paragraph("III. SYSTEM DESIGN AND ARCHITECTURE", s['h1']))
    story.append(Paragraph("AgroNex-Pi follows a layered software architecture with strict separation of concerns across nine Python modules. The hardware abstraction layer (HAL) in hardware.py encapsulates all GPIO, SPI, I2C, and camera access, ensuring that no other module accesses physical registers directly.", s['body']))
    story.append(Paragraph("A. Hardware Platform", s['h2']))
    story.append(Paragraph("The rover is built around the Raspberry Pi 4 Model B (4 GB RAM, 64-bit quad-core Cortex-A72 at 1.5 GHz). Analog sensor inputs are digitized by an ADS1115 16-bit I2C ADC, with an MCP3008 SPI ADC available as fallback. Motor drive is provided by dual BTS7960 43A H-bridge modules controlled via software PWM at 1 kHz. Table I lists the complete bill of materials.", s['body']))
    story.append(Spacer(1,0.05*inch))
    story.append(Paragraph("TABLE I - HARDWARE COMPONENTS", s['abstract_head']))
    bom_ieee=[["Component","Model / Specification","Purpose"],["SBC","Raspberry Pi 4B (4GB)","Central processor"],["ADC (I2C)","ADS1115 16-bit","Soil + Water sensors"],["Soil Moisture","Capacitive v1.2 (3.3V)","Moisture sensing"],["Water Level","HW-038 Analog 3-pin","Reservoir monitoring"],["Temp/Humidity","DHT11/22","Ambient conditions"],["GPS","NEO-7M UART","Positioning"],["Compass","HMC5883L I2C","Heading feedback"],["Camera","Pi Cam v2 / USB webcam","Leaf image capture"],["Motor Driver","BTS7960 43A (x2)","Drive motor control"],["Relay Module","2-ch 5V Active LOW","Pump + cutter switch"],["Battery","12V 7Ah SLA","Power supply"]]
    story.append(ieee_table(bom_ieee,[2.5*inch,2.5*inch,2*inch]))
    story.append(Spacer(1,0.05*inch))
    story.append(Paragraph("B. Software Architecture", s['h2']))
    story.append(Paragraph("The system supervisor (main.py) implements a Finite State Machine with states: BOOT, SELF_TEST, IDLE, IRRIGATING, CUTTING, NAVIGATING, SCANNING, and SAFE_STATE. Four concurrent threads are managed: the 3-second Control Loop, the Disease Scanner, the Flask REST API Server (port 5000), and the Watchdog Timer. Fig. 1 illustrates the software architecture.", s['body']))
    story.append(Spacer(1,0.05*inch))
    story.append(placeholder_box(s,"Fig. 1: AgroNex-Pi Software Architecture Block Diagram",height_cm=5.5))
    story.append(Paragraph("Fig. 1. AgroNex-Pi multi-threaded software architecture and FSM state diagram.", s['caption']))
    story.append(Spacer(1,0.05*inch))
    story.append(Paragraph("C. Hardware Wiring and GPIO Assignment", s['h2']))
    story.append(Paragraph("All GPIO pins use BCM numbering. Signal pins: DHT data (GPIO 4), Relay pump (GPIO 17, Active LOW), Relay cutter (GPIO 27, Active LOW), Buzzer (GPIO 22), LED (GPIO 23). Motor PWM: Left RPWM/LPWM (GPIO 5/6), Right RPWM/LPWM (GPIO 13/19). I2C bus (GPIO 2=SDA, GPIO 3=SCL) carries ADS1115 (0x48) and HMC5883L (0x1E). GPS NEO-7M connects to /dev/serial0 (UART RX = GPIO 15).", s['body']))
    story.append(Spacer(1,0.1*inch))

    story.append(Paragraph("IV. SUBSYSTEM IMPLEMENTATION", s['h1']))
    story.append(Paragraph("A. Soil Moisture Sensing and Automated Irrigation", s['h2']))
    story.append(Paragraph("A capacitive soil moisture sensor (v1.2) is connected to ADS1115 channel A0. Raw 16-bit ADC counts are linearized to moisture percentage using two-point calibration: ADS_SOIL_DRY = 21000 (0% in dry air) and ADS_SOIL_WET = 9500 (100% submerged). A hysteresis band governs pump activation: pump starts when moisture drops below 35% and stops when it reaches 65% or after a 60-second safety timeout. A mandatory 120-second cooldown protects relay contacts.", s['body']))
    story.append(Paragraph("B. GPS Waypoint Navigation", s['h2']))
    story.append(Paragraph("Navigation employs a NEO-7M GPS module (UART, 9600 baud) and an HMC5883L 3-axis magnetometer. The Haversine formula computes great-circle distance and bearing to the target waypoint. The rover executes motion in brief bursts (1.0s forward, 0.2s pivot) and re-samples sensors between each burst. A heading error tolerance of plus or minus 12 degrees determines whether to drive forward or pivot. Waypoint arrival is declared when distance is less than or equal to 2.5 m.", s['body']))
    story.append(Paragraph("C. Plant Disease Detection", s['h2']))
    story.append(Paragraph("The disease detection pipeline begins with a green-pixel pre-filter: the HSV-transformed camera frame must contain at least 15% green pixels (H: 35-90 degrees, S: 40-255, V: 40-255) before inference is triggered. An image quality gate rejects frames with Laplacian variance below 12.0 (blur) or luminance outside the range 15-250 (poor exposure).", s['body']))
    story.append(Paragraph("The accepted frame is resized to 224x224 and normalized to [0.0, 1.0] float32. To reduce false positives from background pixels, the image is divided into a 3x3 grid of nine segments. Each segment is classified independently by the TFLite MobileNetV2 model. A disease alert is issued only if more than 50% of segments (more than 4 of 9) are classified as diseased with confidence at least 70%. This majority-voting scheme is illustrated in Fig. 2.", s['body']))
    story.append(Spacer(1,0.05*inch))
    story.append(placeholder_box(s,"Fig. 2: 3x3 Image Segmentation Majority Voting Scheme",height_cm=4.5))
    story.append(Paragraph("Fig. 2. Majority-voting segmentation: disease declared only when more than 50% of segments are classified as diseased.", s['caption']))
    story.append(Spacer(1,0.05*inch))
    story.append(Paragraph("D. Dual-Model Architecture", s['h2']))
    story.append(Paragraph("A model profile switch (AGRONEX_MODEL_PROFILE environment variable) selects between two TFLite models at startup: (1) the Custom Tulsi Model trained on locally collected images (5 classes) and (2) the PlantVillage Model trained on the publicly available PlantVillage dataset (8 classes). The TFLite runtime is loaded via a three-level fallback chain supporting tflite_runtime, ai_edge_litert, and full TensorFlow.", s['body']))
    story.append(Spacer(1,0.1*inch))

    story.append(Paragraph("V. AI MODEL TRAINING METHODOLOGY", s['h1']))
    story.append(Paragraph("A. Dataset Collection", s['h2']))
    story.append(Paragraph("The custom Tulsi disease dataset was collected using the Raspberry Pi Camera v2 under natural outdoor lighting conditions. [INSERT NUMBER] images per class were captured across four disease states and one background class. The PlantVillage dataset [4] was used for broad-crop training, containing over 54,000 images across 38 plant-disease combinations, of which 8 target classes were selected.", s['body']))
    story.append(Paragraph("B. Model Architecture and Training", s['h2']))
    story.append(Paragraph("Transfer learning from MobileNetV2 (pretrained on ImageNet, input 224x224x3) was employed. The base model was frozen for initial training, followed by fine-tuning of the last 50 layers. A custom classification head was added: GlobalAveragePooling2D, Dropout(0.4), Dense(128, ReLU), Dropout(0.3), Dense(N_classes, Softmax). Training used the Adam optimizer with categorical cross-entropy loss. Data augmentation included random horizontal flip, rotation of plus or minus 15 degrees, zoom of plus or minus 20%, and brightness variation of plus or minus 30%.", s['body']))
    story.append(Spacer(1,0.05*inch))
    story.append(Paragraph("TABLE II - MODEL TRAINING PARAMETERS", s['abstract_head']))
    train_params=[["Parameter","Custom Tulsi Model","PlantVillage Model"],["Base Architecture","MobileNetV2","MobileNetV2"],["Input Resolution","224 x 224 x 3","224 x 224 x 3"],["Classes","5","8"],["Initial Learning Rate","1e-4","1e-4"],["Fine-tune Learning Rate","1e-5","1e-5"],["Initial Epochs","15","20"],["Fine-tune Epochs","10","10"],["Batch Size","32","32"],["Optimizer","Adam","Adam"],["Export Format","TFLite float32","TFLite float32"]]
    story.append(ieee_table(train_params,[2.5*inch,2*inch,2*inch]))
    story.append(Spacer(1,0.1*inch))

    story.append(Paragraph("VI. CLOUD ARCHITECTURE AND REMOTE MONITORING", s['h1']))
    story.append(Paragraph("A serverless AWS stack enables remote monitoring without dedicated server infrastructure. The Raspberry Pi periodically (every 5 seconds) HTTP POSTs sensor telemetry JSON to AWS API Gateway, which invokes a Python Lambda function that writes the payload to an Amazon S3 bucket as state.json. The S3-hosted dashboard frontend fetches this file at 3-second intervals to display live telemetry. Disease scan JPEG images are uploaded asynchronously after each inference. A bidirectional command channel allows the cloud dashboard to remotely trigger irrigation, scanning, and navigation commands. Fig. 3 illustrates the AWS data flow.", s['body']))
    story.append(Spacer(1,0.05*inch))
    story.append(placeholder_box(s,"Fig. 3: AWS Cloud Architecture Data Flow Diagram",height_cm=5))
    story.append(Paragraph("Fig. 3. AWS serverless architecture: Pi to API Gateway to Lambda to S3, with S3-hosted dashboard polling.", s['caption']))
    story.append(Spacer(1,0.1*inch))

    story.append(Paragraph("VII. EXPERIMENTAL RESULTS AND EVALUATION", s['h1']))
    story.append(Paragraph("This section presents experimental results for each subsystem. All experiments were conducted on the physical rover hardware under [INSERT CONDITIONS: indoor/outdoor, lighting conditions, test location].", s['body']))
    story.append(Paragraph("A. Disease Detection Performance", s['h2']))
    story.append(Spacer(1,0.05*inch))
    story.append(placeholder_box(s,"Fig. 4: Confusion Matrix — Tulsi Disease Classification Results",height_cm=5.5))
    story.append(Paragraph("Fig. 4. Confusion matrix for Tulsi disease classification on the test set.", s['caption']))
    story.append(Spacer(1,0.05*inch))
    story.append(Paragraph("TABLE III - DISEASE DETECTION CLASSIFICATION METRICS", s['abstract_head']))
    metrics=[["Class","Precision","Recall","F1-Score","Support"],["Tulsi___Healthy","[X.XX]","[X.XX]","[X.XX]","[N]"],["Tulsi___Infected","[X.XX]","[X.XX]","[X.XX]","[N]"],["Tulsi___Infested","[X.XX]","[X.XX]","[X.XX]","[N]"],["Tulsi___Wilting","[X.XX]","[X.XX]","[X.XX]","[N]"],["Background","[X.XX]","[X.XX]","[X.XX]","[N]"],["Weighted Average","[X.XX]","[X.XX]","[X.XX]","[N]"]]
    story.append(ieee_table(metrics,[2*inch,1.1*inch,1.1*inch,1.1*inch,1.1*inch]))
    story.append(Spacer(1,0.05*inch))
    story.append(Paragraph("B. Irrigation System Response", s['h2']))
    story.append(Spacer(1,0.05*inch))
    story.append(placeholder_box(s,"Fig. 5: Soil Moisture vs. Time — Irrigation Cycle Response Chart",height_cm=4.5))
    story.append(Paragraph("Fig. 5. Soil moisture percentage over time showing irrigation trigger at 35% and pump-off at 65%.", s['caption']))
    story.append(Spacer(1,0.05*inch))
    story.append(Paragraph("The hysteresis controller maintained soil moisture between 35%-65% across [N] irrigation cycles during testing. Average irrigation duration was [X] plus or minus [Y] seconds. No false pump timeouts (PUMP_SAFETY_TIMEOUT) were recorded during normal operation.", s['body']))
    story.append(Paragraph("C. Navigation Accuracy", s['h2']))
    story.append(Spacer(1,0.05*inch))
    story.append(placeholder_box(s,"Fig. 6: GPS Navigation Path — Planned vs. Actual Route",height_cm=5))
    story.append(Paragraph("Fig. 6. Planned navigation route (blue) vs. actual rover GPS track (red) for a [N]-waypoint mission.", s['caption']))
    story.append(Spacer(1,0.05*inch))
    story.append(Paragraph("TABLE IV - NAVIGATION PERFORMANCE METRICS", s['abstract_head']))
    nav_metrics=[["Metric","Value"],["Number of waypoints tested","[N]"],["Waypoint arrival accuracy (mean error)","[X.X] m"],["Heading alignment accuracy (mean error)","[X.X] degrees"],["Average time per waypoint","[X] seconds"],["GPS fix availability","[X]% uptime"]]
    story.append(ieee_table(nav_metrics,[3.5*inch,3*inch]))
    story.append(Spacer(1,0.05*inch))
    story.append(Paragraph("D. System Resource Utilization on Raspberry Pi 4", s['h2']))
    story.append(Paragraph("TABLE V - RASPBERRY PI 4 RESOURCE USAGE", s['abstract_head']))
    sys_metrics=[["Metric","Idle (No Inference)","During TFLite Inference"],["CPU Usage","[X]%","[X]%"],["RAM Usage","[X] MB","[X] MB"],["Inference Latency","—","[X] ms per frame"],["Power Consumption","[X] W","[X] W"],["CPU Temperature","[X] deg C","[X] deg C"]]
    story.append(ieee_table(sys_metrics,[2.5*inch,2*inch,2.5*inch]))
    story.append(Spacer(1,0.05*inch))
    story.append(Paragraph("E. System Photographs", s['h2']))
    story.append(Spacer(1,0.05*inch))
    story.append(placeholder_box(s,"Fig. 7: AgroNex-Pi Rover — Physical Hardware Assembly Photo",height_cm=6))
    story.append(Paragraph("Fig. 7. AgroNex-Pi physical rover showing chassis, sensors, motor drivers, and Raspberry Pi 4.", s['caption']))
    story.append(Spacer(1,0.05*inch))
    story.append(placeholder_box(s,"Fig. 8: AgroNex-Pi Web Dashboard — Live Telemetry Screenshot",height_cm=5))
    story.append(Paragraph("Fig. 8. AWS S3-hosted web dashboard displaying live sensor telemetry and disease scan results.", s['caption']))
    story.append(Spacer(1,0.1*inch))

    story.append(Paragraph("VIII. DISCUSSION", s['h1']))
    story.append(Paragraph("The experimental results confirm that MobileNetV2-based transfer learning on locally collected Tulsi disease images achieves [INSERT: accuracy X%] on the held-out test set, demonstrating that edge AI inference is practical on the Raspberry Pi 4 with an inference latency of [INSERT: X ms] per frame — well within the requirements of near-real-time plant monitoring.", s['body']))
    story.append(Paragraph("The majority-voting segmentation scheme reduced false positive disease alerts compared to whole-image classification, particularly for images with significant background or partially framed leaves. The image quality gate (Laplacian variance + luminance check) successfully rejected [INSERT: X% of frames] as unsuitable for inference in outdoor lighting conditions, preventing spurious disease alerts from motion-blurred captures.", s['body']))
    story.append(Paragraph("The hysteresis irrigation controller maintained target soil moisture with a mean steady-state error of [INSERT: plus or minus X%]. The GPS + compass navigation achieved waypoint arrival within [INSERT: X.X m] mean error, consistent with the plus or minus 2-5 m CEP specification of the NEO-7M module. A key limitation was GPS availability in dense canopy environments. Future work will integrate ultrasonic obstacle detection and wheel odometry.", s['body']))
    story.append(Spacer(1,0.1*inch))

    story.append(Paragraph("IX. CONCLUSION", s['h1']))
    story.append(Paragraph("This paper presented AgroNex-Pi, a low-cost autonomous agricultural robot integrating soil moisture sensing, automated irrigation, scheduled grass trimming, GPS-guided navigation, edge AI plant disease detection, and cloud telemetry on the Raspberry Pi 4. The system demonstrated [INSERT KEY RESULTS] in real-world testing, establishing it as a viable platform for small-scale precision agriculture applications. The dual-model TFLite architecture enables adaptation to different crop types by swapping the model file and labels without any code changes. Future directions include obstacle avoidance, INT8 quantization for Edge TPU deployment, multi-plant GPS tracking, and OTA model updates.", s['body']))
    story.append(Spacer(1,0.1*inch))

    story.append(Paragraph("ACKNOWLEDGMENT", s['h1']))
    story.append(Paragraph("The authors would like to thank [Guide/Mentor Name] for guidance and support throughout this project, [Institute Name] for providing laboratory facilities, and the open-source community behind TensorFlow, Raspberry Pi Foundation, and the PlantVillage dataset.", s['body']))
    story.append(Spacer(1,0.1*inch))

    story.append(HRFlowable(width="100%",thickness=1,color=BLACK))
    story.append(Paragraph("REFERENCES", s['h1']))
    refs=["[1] Food and Agriculture Organization (FAO), \"The State of Food and Agriculture 2021,\" FAO, Rome, 2021.","[2] M. Sandler, A. Howard, M. Zhu, A. Zhmoginov, and L.-C. Chen, \"MobileNetV2: Inverted Residuals and Linear Bottlenecks,\" in Proc. IEEE CVPR, 2018, pp. 4510-4520.","[3] C. W. Bac, E. J. van Henten, J. Hemming, and Y. Edan, \"Harvesting Robots for High-value Crops,\" J. Field Robot., vol. 31, no. 6, pp. 888-911, 2014.","[4] S. P. Mohanty, D. P. Hughes, and M. Salathe, \"Using Deep Learning for Image-Based Plant Disease Detection,\" Front. Plant Sci., vol. 7, p. 1419, 2016.","[5] A. Khanna and S. Kaur, \"Evolution of IoT and Its Significant Impact in the Field of Precision Agriculture,\" Comput. Electron. Agric., vol. 157, pp. 218-231, 2019.","[6] L. Emmi et al., \"New Trends in Robotics for Agriculture,\" ScientificWorldJournal, vol. 2014, Art. no. 404059, 2014.","[7] TensorFlow Lite, \"TensorFlow Lite Guide,\" Google, 2023. [Online]. Available: https://www.tensorflow.org/lite","[8] Raspberry Pi Foundation, \"Raspberry Pi 4 Model B Datasheet,\" 2019. [Online]. Available: https://www.raspberrypi.com","[9] Texas Instruments, \"ADS1115 Datasheet: Ultra-Small, Low-Power, 16-Bit ADC,\" SBAS444D, 2009.","[10] Honeywell, \"HMC5883L 3-Axis Digital Compass IC,\" Datasheet, 2013."]
    for ref in refs:
        story.append(Paragraph(ref, s['ref']))

    doc.build(story,onFirstPage=ieee_page,onLaterPages=ieee_page)
    print(f"IEEE Research Paper saved: {out}")
    return out


import shutil

if __name__ == "__main__":
    print("=" * 60)
    print("  AgroNex-Pi Documentation Generator")
    print("=" * 60)
    print()
    r1 = build_project_report()
    explanation_pdf = os.path.join(BASE_DIR, "Explanation file.pdf")
    try:
        shutil.copyfile(r1, explanation_pdf)
        print(f"Updated: {explanation_pdf}")
    except Exception as e:
        print(f"Could not overwrite Explanation file.pdf (might be open in viewer): {e}")
    print()
    r2 = build_ieee_paper()
    print()
    print("=" * 60)
    print("  All documents generated successfully!")
    print(f"  1. {os.path.basename(r1)}")
    print(f"  2. {os.path.basename(r2)}")
    print(f"  3. Explanation file.pdf")
    print("=" * 60)

