#!/usr/bin/env python3
"""Build AgroNex-Pi major-project PowerPoint (short slides + pictures)."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

BASE = r"C:\Users\Nikhil\OneDrive\Desktop\Major project"
AS = os.path.join(BASE, "ppt_assets")
OUT = os.path.join(BASE, "AgroNex_Pi_Presentation.pptx")

BG = RGBColor(0x0D, 0x23, 0x3A)
BG2 = RGBColor(0x10, 0x1A, 0x2E)
GREEN = RGBColor(0x00, 0xC8, 0x53)
CYAN = RGBColor(0x00, 0xB4, 0xD8)
GOLD = RGBColor(0xFF, 0xC3, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT = RGBColor(0xD0, 0xE8, 0xFF)
INK = RGBColor(0x0B, 0x1F, 0x17)

SW, SH = Inches(13.333), Inches(7.5)


def sl(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def set_bg(s, c=BG):
    fill = s.background.fill
    fill.solid()
    fill.fore_color.rgb = c


def shape(s, l, t, w, h, fill, line=None):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line:
        sh.line.color.rgb = line
        sh.line.width = Pt(1.25)
    else:
        sh.line.fill.background()
    return sh


def rect(s, l, t, w, h, fill):
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh


def tb(s, text, l, t, w, h, sz=16, bold=False, col=WHITE, al=PP_ALIGN.LEFT, font="Calibri"):
    box = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = al
    r = p.add_run()
    r.text = text
    r.font.size = Pt(sz)
    r.font.bold = bold
    r.font.color.rgb = col
    r.font.name = font
    return box


def footer(s, n=""):
    rect(s, 0, 7.18, 13.333, 0.32, GREEN)
    tb(s, "AgroNex-Pi  |  Autonomous Smart Agricultural Robot" + (f"  |  {n}" if n else ""),
       0.2, 7.2, 12.9, 0.28, sz=11, col=INK, al=PP_ALIGN.CENTER)


def header(s, title, sub=""):
    rect(s, 0, 0, 13.333, 0.95, GREEN)
    tb(s, title, 0.35, 0.12, 12.5, 0.48, sz=28, bold=True, col=INK)
    if sub:
        tb(s, sub, 0.35, 0.55, 12.5, 0.32, sz=13, col=RGBColor(0x06, 0x4E, 0x3B))


def bullets(s, items, l=0.45, t=1.2, w=12.4, sz=18, gap=0.42):
    y = t
    for item in items:
        if item.startswith("##"):
            tb(s, item[2:].strip(), l, y, w, 0.38, sz=sz, bold=True, col=CYAN)
        else:
            tb(s, "●  " + item, l, y, w, 0.4, sz=sz, col=LIGHT)
        y += gap


def pic(s, name, l, t, w, h):
    path = os.path.join(AS, name)
    if os.path.exists(path):
        s.shapes.add_picture(path, Inches(l), Inches(t), Inches(w), Inches(h))
    else:
        shape(s, l, t, w, h, RGBColor(0x1A, 0x2E, 0x40), GREEN)
        tb(s, name, l, t + h / 2, w, 0.4, sz=12, col=GOLD, al=PP_ALIGN.CENTER)


def grid_pics(s, files, captions, top=1.15, cols=4):
    n = len(files)
    rows = (n + cols - 1) // cols
    gapx, gapy = 0.22, 0.42
    cell_w = (13.0 - (cols - 1) * gapx) / cols
    cell_h = 2.35 if rows <= 2 else 1.85
    if rows == 1:
        cell_h = 4.6
    for i, (fn, cap) in enumerate(zip(files, captions)):
        r, c = divmod(i, cols)
        x = 0.18 + c * (cell_w + gapx)
        y = top + r * (cell_h + gapy)
        pic(s, fn, x, y, cell_w, cell_h - 0.32)
        tb(s, cap, x, y + cell_h - 0.30, cell_w, 0.3, sz=11, col=GOLD, al=PP_ALIGN.CENTER)


def table_slide(s, headers, rows, l=0.35, t=1.2, w=12.6, row_h=0.42):
    nr, nc = 1 + len(rows), len(headers)
    tbl = s.shapes.add_table(nr, nc, Inches(l), Inches(t), Inches(w), Inches(min(5.6, row_h * nr))).table
    widths = [Inches(w * 0.28)] + [Inches(w * 0.72 / (nc - 1))] * (nc - 1)
    for j, width in enumerate(widths):
        tbl.columns[j].width = width
    for j, h in enumerate(headers):
        cell = tbl.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = GREEN
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = h
        run.font.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = INK
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = tbl.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(0x12, 0x2C, 0x44) if i % 2 == 0 else RGBColor(0x16, 0x34, 0x50)
            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = str(val)
            run.font.size = Pt(12)
            run.font.color.rgb = LIGHT


def title_slide(prs):
    s = sl(prs)
    set_bg(s, BG2)
    rect(s, 0, 0, 13.333, 0.18, GREEN)
    rect(s, 0, 7.32, 13.333, 0.18, GREEN)
    tb(s, "MAJOR PROJECT PRESENTATION", 0.5, 1.15, 12.3, 0.4, sz=16, col=GOLD, al=PP_ALIGN.CENTER)
    tb(s, "AgroNex-Pi", 0.5, 1.7, 12.3, 0.9, sz=54, bold=True, col=GREEN, al=PP_ALIGN.CENTER)
    tb(s, "Autonomous Smart Agricultural Robot", 0.5, 2.6, 12.3, 0.5, sz=26, col=WHITE, al=PP_ALIGN.CENTER)
    tb(s, "Edge-AI disease detection  ·  GPS navigation  ·  Smart irrigation  ·  AWS cloud",
       0.5, 3.2, 12.3, 0.4, sz=16, col=CYAN, al=PP_ALIGN.CENTER)
    shape(s, 3.6, 3.8, 6.1, 0.06, GREEN)
    tb(s, "Department of Electronics / Computer Engineering", 0.5, 4.1, 12.3, 0.35, sz=16, col=LIGHT, al=PP_ALIGN.CENTER)
    tb(s, "Academic Year 2025–26", 0.5, 4.5, 12.3, 0.3, sz=14, col=GOLD, al=PP_ALIGN.CENTER)
    tb(s, "Team: Nikhil & members          Guide: [Guide Name]", 0.5, 5.15, 12.3, 0.35, sz=15, col=LIGHT, al=PP_ALIGN.CENTER)


def build():
    prs = Presentation()
    prs.slide_width = SW
    prs.slide_height = SH

    title_slide(prs)

    s = sl(prs); set_bg(s); header(s, "Contents"); footer(s, "02")
    left = ["1. Abstract", "2. Introduction", "3. SDGs", "4. Literature & gap",
            "5. Components", "6. Specifications", "7. Architecture", "8. Flowchart"]
    right = ["9. Hardware–software integration", "10. Dataset (our photos)",
             "11. Model building", "12. Testing & evaluation",
             "13. Dashboard", "14. Applications & future scope",
             "15. Conclusion", "16. References, thanks"]
    bullets(s, left, 0.7, 1.3, 5.8, 18, 0.55)
    bullets(s, right, 7.0, 1.3, 5.8, 18, 0.55)

    s = sl(prs); set_bg(s); header(s, "Abstract", "One-page summary"); footer(s, "03")
    bullets(s, [
        "Low-cost rover on Raspberry Pi 4 + Arduino Uno slave.",
        "Does 5 jobs: irrigate, mow, GPS navigate, detect leaf disease, send cloud data.",
        "AI runs on the Pi (TFLite MobileNetV2) — no internet needed for diagnosis.",
        "We trained on PlantVillage + our own local-plant photos.",
        "Safety: pump, cutter and drive motors never run together.",
    ], t=1.25, sz=20, gap=0.7)

    s = sl(prs); set_bg(s); header(s, "Introduction", "Why this project?"); footer(s, "04")
    bullets(s, [
        "FAO: plant disease wastes about 10-40% of world crop yield.",
        "Small farms cannot hire agronomists or irrigate by hand every day.",
        "Flood irrigation wastes water; cloud apps fail without internet.",
        "AgroNex-Pi: one cheap robot that waters, mows, drives and scans leaves.",
        "Farmer sees live data on phone / laptop (local Flask or AWS).",
    ], t=1.25, sz=20, gap=0.7)

    s = sl(prs); set_bg(s); header(s, "Objectives", "What we set out to build"); footer(s, "05")
    bullets(s, [
        "Build a low-cost rover that waters, mows, drives and scans plants.",
        "Detect leaf disease on the Pi (offline) using our own photos.",
        "Water only when soil is dry (save water vs timer irrigation).",
        "Show live sensors on a local dashboard and optional AWS cloud.",
        "Keep pump, cutter and motors from running at the same time (safety).",
    ], t=1.25, sz=20, gap=0.7)

    s = sl(prs); set_bg(s); header(s, "Sustainable Development Goals", "UN Agenda 2030"); footer(s, "05")
    cards = [
        ("SDG 2  Zero Hunger", "Early disease catch + smart watering protects yield."),
        ("SDG 6  Clean Water", "Pump ON only if soil < 35%. Saves water vs timers."),
        ("SDG 9  Innovation", "Edge AI + IoT robot that small farms can afford."),
        ("SDG 12  Responsible use", "Less chemical spray; treat only if AI confirms disease."),
    ]
    for i, (h, b) in enumerate(cards):
        x = 0.4 + (i % 2) * 6.45
        y = 1.25 + (i // 2) * 2.8
        shape(s, x, y, 6.15, 2.5, RGBColor(0x12, 0x2C, 0x44), GREEN)
        tb(s, h, x + 0.25, y + 0.3, 5.7, 0.55, sz=22, bold=True, col=GOLD)
        tb(s, b, x + 0.25, y + 1.05, 5.7, 1.1, sz=18, col=LIGHT)

    s = sl(prs); set_bg(s); header(s, "Literature review", "What others did"); footer(s, "06")
    table_slide(s, ["Work", "Idea", "Gap"], [
        ["Mohanty 2016", "CNN on PlantVillage (~99% lab)", "Lab photos, no robot, often cloud"],
        ["Bac 2014", "Greenhouse harvest robot", "Costly, needs structured farm"],
        ["Plantix / PlantSnap", "Phone app diagnosis", "Needs internet every time"],
        ["IoT irrigation papers", "Soil sensor + pump", "No AI, no navigation"],
        ["GPS agri robots", "Field waypoint driving", "No disease + irrigation combo"],
    ])

    s = sl(prs); set_bg(s); header(s, "Gap analysis  →  our work"); footer(s, "07")
    bullets(s, [
        "Gap: irrigation, mowing, GPS and AI are usually separate projects.",
        "Gap: lab datasets look unlike a Pi camera in a real garden.",
        "Gap: rural farms have weak internet — cloud-only AI fails.",
        "We combine all 5 jobs on one chassis.",
        "We photographed local plants with the same rover camera, then trained.",
        "Inference stays on-device; cloud is only for remote viewing.",
    ], t=1.25, sz=19, gap=0.7)

    s = sl(prs); set_bg(s); header(s, "Components — brain & sensors"); footer(s, "08")
    grid_pics(s, [
        "comp_rpi.jpg", "comp_arduino.jpg", "comp_camera.jpg", "comp_soil.jpg",
        "comp_ads.jpg", "comp_dht.jpg", "comp_water.jpg", "comp_compass.jpg",
    ], [
        "Raspberry Pi 4B", "Arduino Uno slave", "OV5647 camera", "Soil moisture",
        "ADS1115 ADC", "DHT11/22", "Water-level probe", "HMC5883L compass",
    ], cols=4)

    s = sl(prs); set_bg(s); header(s, "Components — drive, power, tools"); footer(s, "09")
    grid_pics(s, [
        "comp_chassis.jpg", "comp_bts.jpg", "comp_gps.jpg", "comp_relay.jpg",
        "comp_pump.jpg", "comp_cutter.jpg", "comp_buck.jpg", "comp_battery.jpg",
        "comp_ultra.jpg", "comp_alert.jpg",
    ], [
        "4WD chassis", "BTS7960 ×2", "NEO-7M GPS", "2-ch relay",
        "5 V pump", "12 V cutter", "LM2596 5 V", "12 V battery",
        "HC-SR04 ×2", "Buzzer + LED",
    ], cols=5, top=1.12)

    s = sl(prs); set_bg(s); header(s, "System specification"); footer(s, "10")
    table_slide(s, ["Item", "Value"], [
        ["Compute", "Pi 4B 4 GB + Arduino Uno R3 (USB 115200)"],
        ["Software", "Python 3.9, 9 modules, 4 threads, FSM"],
        ["AI", "MobileNetV2 → TFLite, 224×224, ~280 ms / frame"],
        ["Irrigation", "ON < 35%, OFF ≥ 65%, 60 s max, 120 s cooldown"],
        ["Disease gates", "Blur + green % + 70% confidence + 3×3 vote"],
        ["Navigation", "NEO-7M + compass, arrive within 2.5 m"],
        ["Cloud", "AWS API Gateway + Lambda + S3 every 5 s"],
        ["Power", "12 V battery, LM2596 5 V rail, common ground"],
    ], row_h=0.52)

    s = sl(prs); set_bg(s); header(s, "System architecture (block diagram)"); footer(s, "11")
    pic(s, "architecture.jpg", 0.35, 1.1, 12.6, 5.9)

    s = sl(prs); set_bg(s); header(s, "Software layers (short)"); footer(s, "12")
    bullets(s, [
        "hardware.py — only file that touches GPIO / I²C / UART / camera.",
        "Controllers: irrigation, cutter, navigation, disease_detect.",
        "main.py FSM: BOOT → SELF_TEST → IDLE → MONITORING → action states.",
        "Threads: 3 s control loop, scanner, Flask :5000, 30 s watchdog.",
        "aws_relay.py + S3 dashboard for remote view / commands.",
        "SAFE_STATE if self-test fails: all actuators off.",
    ], t=1.25, sz=20, gap=0.7)

    s = sl(prs); set_bg(s); header(s, "System flowchart"); footer(s, "13")
    pic(s, "flowchart.jpg", 0.25, 1.08, 12.8, 5.95)

    s = sl(prs); set_bg(s); header(s, "Formal operational flowchart"); footer(s, "13b")
    pic(s, "flowchart_html.jpg", 0.25, 1.08, 12.8, 5.95)

    s = sl(prs); set_bg(s); header(s, "Hardware & software integration"); footer(s, "14")
    pic(s, "integration.jpg", 0.25, 1.08, 12.8, 5.95)

    s = sl(prs); set_bg(s); header(s, "Integration — how parts talk"); footer(s, "15")
    bullets(s, [
        "Sensors: I²C (soil, water, compass), UART GPS, CSI camera, 1-wire DHT.",
        "Arduino: motors, probe servo, ultrasonics — Pi sends short serial commands.",
        "Relays active-LOW; pins set HIGH before OUTPUT so pump/cutter stay off at boot.",
        "Interlock: stop wheels before pump or cutter (protects 12 V rail).",
        "Cloud POST every 5 s; if Wi-Fi dies, local dashboard still works.",
    ], t=1.25, sz=19, gap=0.72)

    s = sl(prs); set_bg(s); header(s, "Building the dataset", "We photographed local plants ourselves"); footer(s, "16")
    pic(s, "dataset_process.jpg", 0.4, 1.15, 12.5, 3.55)
    bullets(s, [
        "Problem: Kaggle lab photos ≠ Pi camera (blur, noise, real background).",
        "Fix: capture with the same OV5647 on the rover (capture_field_dataset.py).",
        "Classes: healthy / unhealthy / yellow / dried / not-a-leaf.",
    ], t=4.85, sz=18, gap=0.48)

    s = sl(prs); set_bg(s); header(s, "Our local classes (field photos)"); footer(s, "17")
    grid_pics(s, [
        "leaf_healthy.jpg", "leaf_unhealthy.jpg", "leaf_yellow.jpg", "leaf_dried.jpg", "leaf_bg.jpg",
    ], [
        "Local_healthy", "Local_unhealthy", "Local_yellow", "Local_dried", "background_not_a_leaf",
    ], cols=5, top=1.3)

    s = sl(prs); set_bg(s); header(s, "Dataset details", "What we actually did"); footer(s, "18")
    bullets(s, [
        "Source A: PlantVillage (Kaggle) — tomato, potato, bell pepper, max 180 / class.",
        "Source B: our garden / campus plants with Pi camera at rover height.",
        "Angles: top, 15–30° tilt, 5–15 cm close-up. Sun + indoor light.",
        "Also shoot pots/soil/hands so the model learns “this is not a leaf”.",
        "Split: 80% train / 20% validation. Field images not capped.",
        "Folders merge into training_subset/ before training.",
    ], t=1.2, sz=19, gap=0.7)

    s = sl(prs); set_bg(s); header(s, "Building the model", "Transfer learning — short version"); footer(s, "19")
    bullets(s, [
        "Start from MobileNetV2 already trained on ImageNet (knows edges, colors).",
        "Remove old 1000-class head. Add GAP + Dropout 0.3 + Softmax(N classes).",
        "Stage 1: freeze backbone, train head (Adam, LR 1e-3).",
        "Stage 2: unfreeze top layers, tiny LR (1e-4 / 1e-5) — fine-tune.",
        "Export quantized TFLite (~small file) to models/plant_model.tflite.",
    ], t=1.2, sz=19, gap=0.72)

    s = sl(prs); set_bg(s); header(s, "ML techniques used"); footer(s, "20")
    table_slide(s, ["Technique", "Why we used it"], [
        ["Transfer learning", "Few local photos; ImageNet already learned vision"],
        ["Data augmentation", "Flip, rotate, zoom, brightness — more variety"],
        ["Class weights", "Rare disease class is not ignored"],
        ["Dropout 0.3", "Stops memorizing training photos"],
        ["Early stopping", "Stop when validation stops improving"],
        ["Dynamic-range quantize", "Faster, smaller model for Pi CPU"],
        ["[-1, 1] normalize", "Matches MobileNetV2 training math"],
        ["5-gate inference", "Cuts false alarms in the garden"],
    ])

    s = sl(prs); set_bg(s); header(s, "On-device inference (5 gates)"); footer(s, "21")
    bullets(s, [
        "1. Quality: too blurry or too dark → RETAKE, not “disease”.",
        "2. Green pixels: < 15% green → skip (no leaf in view).",
        "3. Split photo into 3×3 patches; classify each patch.",
        "4. Vote: more than 4 of 9 patches must be diseased.",
        "5. Confidence: each diseased patch needs ≥ 70% softmax.",
        "Then: knowledge-base advice + buzzer/LED + save JPEG.",
    ], t=1.2, sz=20, gap=0.7)

    s = sl(prs); set_bg(s); header(s, "Testing & evaluation"); footer(s, "22")
    bullets(s, [
        "Hardware scripts: soil, water, DHT, relay, motors, camera, alerts — all PASS.",
        "Soil dry-air ADC ~26 300 → 0%; wet ~9 500 → ~100%.",
        "Pump starts < 35%, stops ≥ 65% or after 60 s.",
        "GPS: stop-and-check bursts; waypoint done at ≤ 2.5 m.",
        "AI: val. accuracy typically ~88–95% after local photos (vs ~40–50% domain shift).",
        "Pi inference ~280 ms/frame. Interlocks verified (no dual high-current loads).",
    ], t=1.2, sz=18, gap=0.68)

    s = sl(prs); set_bg(s); header(s, "ML results (what to say in viva)"); footer(s, "23")
    table_slide(s, ["Check", "Result"], [
        ["Custom 5-class (local plant)", "Validation about 88–93%"],
        ["PlantVillage 8-class mix", "Validation about 91–95%"],
        ["False-alarm control", "Blur/green/vote/70% gates"],
        ["Latency on Pi 4 CPU", "~280 ms per frame"],
        ["Model file", "Quantized .tflite + labels.txt"],
        ["Real camera test", "test_disease_camera.py live demo"],
    ])

    s = sl(prs); set_bg(s); header(s, "Dashboard — local Flask"); footer(s, "24")
    pic(s, "dash_local.jpg", 0.45, 1.1, 12.4, 5.9)

    s = sl(prs); set_bg(s); header(s, "Dashboard — AWS cloud"); footer(s, "25")
    pic(s, "dash_cloud.jpg", 0.45, 1.1, 12.4, 5.9)

    s = sl(prs); set_bg(s); header(s, "Dashboard — farm command center"); footer(s, "26")
    pic(s, "dash_farm.jpg", 0.45, 1.1, 12.4, 5.9)

    s = sl(prs); set_bg(s); header(s, "Dashboard — disease capture UI"); footer(s, "27")
    pic(s, "dash_disease_ui.jpg", 0.45, 1.1, 12.4, 5.9)

    s = sl(prs); set_bg(s); header(s, "Dashboard — 3x3 disease vote"); footer(s, "28")
    pic(s, "dash_disease.jpg", 0.45, 1.1, 12.4, 5.9)

    s = sl(prs); set_bg(s); header(s, "Applications"); footer(s, "27")
    bullets(s, [
        "Small farms (1–5 acre): auto water + leaf check.",
        "Home / terrace gardens: mow + phone monitoring.",
        "Nurseries: catch disease early, less chemical spray.",
        "Colleges: teaching IoT, robotics and edge AI.",
        "Off-grid: local Flask works even without internet.",
    ], t=1.25, sz=22, gap=0.78)

    s = sl(prs); set_bg(s); header(s, "Future scope"); footer(s, "28")
    bullets(s, [
        "Better obstacle sense (ultrasonic already started) + wheel encoders.",
        "Solar + battery monitor for full off-grid use.",
        "YOLO to find the leaf first, then classify disease.",
        "More local crops; rain-aware watering; phone app.",
        "INT8 / Coral TPU for faster AI.",
    ], t=1.25, sz=22, gap=0.78)

    s = sl(prs); set_bg(s); header(s, "Conclusion"); footer(s, "29")
    bullets(s, [
        "One affordable rover does irrigation, mowing, GPS and edge AI.",
        "Local photos + transfer learning solved the “lab vs field camera” gap.",
        "Safety interlocks and FSM keep high-current parts under control.",
        "Cloud dashboard is extra; core farming still works offline.",
        "Shows that smart farming is possible without expensive machinery.",
    ], t=1.25, sz=20, gap=0.72)

    s = sl(prs); set_bg(s); header(s, "References"); footer(s, "30")
    bullets(s, [
        "[1] FAO, The State of Food and Agriculture, 2021.",
        "[2] Sandler et al., MobileNetV2, IEEE CVPR, 2018.",
        "[3] Mohanty et al., DL plant disease, Front. Plant Sci., 2016.",
        "[4] Bac et al., Harvesting robots, J. Field Robot., 2014.",
        "[5] Khanna & Kaur, IoT in precision agriculture, 2019.",
        "[6] TensorFlow Lite guide; Raspberry Pi 4 datasheet.",
        "[7] PlantVillage / Kaggle plantdisease dataset.",
        "[8] TI ADS1115 datasheet; Honeywell HMC5883L datasheet.",
    ], t=1.2, sz=17, gap=0.55)

    s = sl(prs); set_bg(s); header(s, "Acknowledgement"); footer(s, "31")
    bullets(s, [
        "Project guide [Name] — guidance and reviews.",
        "HOD and department — lab, tools, and time on the rover.",
        "Institute — workspace and academic support.",
        "Families — patience during build and testing.",
        "Open source: TensorFlow, Raspberry Pi, PlantVillage, Python.",
    ], t=1.3, sz=20, gap=0.75)

    s = sl(prs)
    set_bg(s, BG2)
    rect(s, 0, 0, 13.333, 0.18, GREEN)
    rect(s, 0, 7.32, 13.333, 0.18, GREEN)
    tb(s, "Thank You", 0.5, 2.2, 12.3, 1.0, sz=60, bold=True, col=GREEN, al=PP_ALIGN.CENTER)
    tb(s, "Questions are welcome", 0.5, 3.3, 12.3, 0.5, sz=24, col=WHITE, al=PP_ALIGN.CENTER)
    shape(s, 4.6, 4.0, 4.1, 0.06, GREEN)
    tb(s, "AgroNex-Pi  ·  Edge-AI  ·  IoT  ·  Robotics  ·  Cloud", 0.5, 4.3, 12.3, 0.4, sz=16, col=CYAN, al=PP_ALIGN.CENTER)
    tb(s, "Raspberry Pi 4  |  Arduino  |  TensorFlow Lite  |  AWS", 0.5, 4.85, 12.3, 0.35, sz=14, col=GOLD, al=PP_ALIGN.CENTER)

    prs.save(OUT)
    print(f"Saved {OUT}  slides={len(prs.slides)}")


if __name__ == "__main__":
    build()
