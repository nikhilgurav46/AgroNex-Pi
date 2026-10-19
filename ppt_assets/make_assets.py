# -*- coding: utf-8 -*-
#!/usr/bin/env python3

"""Create component photos, diagrams, and dashboard shots for the AgroNex-Pi PPT."""

import math

import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter



BASE = os.path.dirname(os.path.abspath(__file__))

os.makedirs(BASE, exist_ok=True)



W, H = 900, 700





def font(size, bold=False):

    for name in (

        "C:/Windows/Fonts/segoeui.ttf",

        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",

        "C:/Windows/Fonts/arial.ttf",

        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",

    ):

        if os.path.exists(name):

            try:

                return ImageFont.truetype(name, size)

            except Exception:

                pass

    return ImageFont.load_default()





def save(img, name):

    path = os.path.join(BASE, name)

    img.save(path, "JPEG", quality=92)

    return path





def card(bg=(18, 32, 48)):

    im = Image.new("RGB", (W, H), bg)

    d = ImageDraw.Draw(im)

    d.rounded_rectangle((18, 18, W - 18, H - 18), 28, fill=(12, 24, 38), outline=(16, 185, 129), width=4)

    return im, d





def label(d, title, sub):

    d.text((40, 40), title, fill=(236, 253, 245), font=font(36, True))

    d.text((40, 92), sub, fill=(148, 163, 184), font=font(22))





def rpi():

    im, d = card()

    label(d, "Raspberry Pi 4 Model B", "Main brain - AI + control (4 GB)")

    d.rounded_rectangle((160, 180, 740, 580), 18, fill=(46, 125, 50), outline=(200, 230, 201), width=3)

    d.rectangle((180, 200, 420, 360), fill=(20, 20, 20))

    d.text((200, 250), "BCM2711", fill=(16, 185, 129), font=font(28, True))

    d.rectangle((460, 210, 720, 270), fill=(139, 0, 0))

    d.text((480, 222), "USB 3.0  USB 2.0", fill=(255, 255, 255), font=font(20))

    d.rectangle((460, 290, 620, 340), fill=(80, 80, 90))

    d.text((475, 300), "Ethernet", fill=(255, 255, 255), font=font(18))

    d.ellipse((200, 400, 280, 480), fill=(30, 30, 30), outline=(180, 180, 180), width=3)

    d.text((190, 500), "GPIO header", fill=(255, 255, 255), font=font(20))

    d.rectangle((340, 410, 700, 470), fill=(40, 40, 40))

    for i in range(12):

        d.ellipse((360 + i * 28, 422, 376 + i * 28, 438), fill=(212, 175, 55))

        d.ellipse((360 + i * 28, 444, 376 + i * 28, 460), fill=(212, 175, 55))

    return save(im, "comp_rpi.jpg")





def soil():

    im, d = card((20, 40, 28))

    label(d, "Capacitive Soil Sensor v1.2", "Measures how wet / dry the soil is")

    d.rounded_rectangle((330, 170, 570, 260), 10, fill=(46, 125, 50))

    d.text((360, 198), "v1.2  analog", fill=(255, 255, 255), font=font(22))

    d.polygon([(360, 260), (540, 260), (500, 620), (400, 620)], fill=(30, 30, 30), outline=(80, 80, 80))

    d.rectangle((430, 270, 470, 600), fill=(20, 20, 20))

    d.text((250, 640), "ADS1115 A0  ?  moisture %", fill=(167, 243, 208), font=font(22))

    return save(im, "comp_soil.jpg")





def ads():

    im, d = card()

    label(d, "ADS1115 16-bit ADC", "Turns analog sensor voltage into numbers")

    d.rounded_rectangle((220, 200, 680, 520), 16, fill=(25, 55, 109), outline=(96, 165, 250), width=3)

    d.rectangle((300, 250, 600, 340), fill=(15, 23, 42))

    d.text((330, 275), "ADS1115  I2C 0x48", fill=(147, 197, 253), font=font(28, True))

    for i, name in enumerate(["A0 Soil", "A1 Water", "SDA", "SCL"]):

        x = 260 + i * 100

        d.ellipse((x, 400, x + 50, 450), fill=(212, 175, 55))

        d.text((x - 10, 460), name, fill=(226, 232, 240), font=font(16))

    return save(im, "comp_ads.jpg")





def water():

    im, d = card((10, 30, 50))

    label(d, "HW-038 Water Level Sensor", "Checks tank water so pump never runs dry")

    d.rounded_rectangle((300, 180, 600, 580), 20, fill=(14, 116, 144), outline=(103, 232, 249), width=3)

    d.rectangle((320, 360, 580, 560), fill=(8, 47, 73))

    d.polygon([(320, 360), (580, 360), (580, 250), (320, 320)], fill=(56, 189, 248))

    d.text((360, 420), "WATER", fill=(255, 255, 255), font=font(32, True))

    return save(im, "comp_water.jpg")





def dht():

    im, d = card()

    label(d, "DHT11 / DHT22", "Air temperature and humidity")

    d.rounded_rectangle((330, 180, 570, 420), 12, fill=(30, 64, 175), outline=(147, 197, 253), width=3)

    d.rectangle((360, 220, 540, 300), fill=(15, 23, 42))

    d.text((390, 245), "DHT11", fill=(255, 255, 255), font=font(32, True))

    for i in range(3):

        d.rectangle((380 + i * 50, 430, 410 + i * 50, 560), fill=(180, 180, 180))

    d.text((360, 580), "VCC  DATA  GND", fill=(203, 213, 225), font=font(20))

    return save(im, "comp_dht.jpg")





def camera():

    im, d = card((20, 20, 24))

    label(d, "OV5647 CSI Camera", "Takes leaf photos for disease AI")

    d.rounded_rectangle((250, 200, 650, 480), 18, fill=(15, 15, 18), outline=(100, 100, 110), width=3)

    d.ellipse((380, 250, 520, 390), fill=(40, 40, 48), outline=(180, 180, 190), width=4)

    d.ellipse((420, 290, 480, 350), fill=(8, 47, 73))

    d.rectangle((270, 490, 630, 540), fill=(30, 30, 30))

    d.text((330, 500), "CSI ribbon  ?  Pi camera port", fill=(226, 232, 240), font=font(20))

    return save(im, "comp_camera.jpg")





def relay():

    im, d = card()

    label(d, "2-Channel 5 V Relay", "Safe switch for pump and cutter")

    d.rounded_rectangle((180, 180, 720, 560), 14, fill=(30, 58, 138), outline=(147, 197, 253), width=3)

    d.rounded_rectangle((230, 230, 420, 420), 10, fill=(226, 232, 240), outline=(100, 116, 139), width=2)

    d.rounded_rectangle((480, 230, 670, 420), 10, fill=(226, 232, 240), outline=(100, 116, 139), width=2)

    d.text((265, 300), "CH1\nPUMP", fill=(15, 23, 42), font=font(26, True))

    d.text((515, 300), "CH2\nCUTTER", fill=(15, 23, 42), font=font(26, True))

    d.text((240, 470), "Active-LOW  GPIO17 / GPIO27", fill=(255, 255, 255), font=font(22))

    return save(im, "comp_relay.jpg")





def pump():

    im, d = card((8, 40, 40))

    label(d, "5 V Mini Water Pump", "Pushes water to plants (~120 L/hr)")

    d.ellipse((300, 220, 600, 520), fill=(6, 95, 70), outline=(52, 211, 153), width=4)

    d.rectangle((430, 180, 470, 240), fill=(100, 116, 139))

    d.rectangle((560, 340, 700, 380), fill=(100, 116, 139))

    d.text((360, 350), "PUMP", fill=(236, 253, 245), font=font(36, True))

    d.text((300, 560), "Powered from 5 V buck, not 12 V battery", fill=(167, 243, 208), font=font(20))

    return save(im, "comp_pump.jpg")





def cutter():

    im, d = card((40, 20, 16))

    label(d, "12 V Grass Cutter Motor", "Trims grass on a timer")

    d.rounded_rectangle((340, 200, 560, 420), 20, fill=(69, 10, 10), outline=(248, 113, 113), width=3)

    d.ellipse((300, 430, 600, 620), fill=(120, 53, 15), outline=(251, 191, 36), width=3)

    d.line((310, 525, 590, 525), fill=(253, 224, 71), width=8)

    d.line((450, 440, 450, 610), fill=(253, 224, 71), width=8)

    d.text((365, 280), "12 V DC", fill=(254, 226, 226), font=font(28, True))

    return save(im, "comp_cutter.jpg")





def bts():

    im, d = card()

    label(d, "BTS7960 H-Bridge (x2)", "Drives left / right 12 V motors")

    d.rounded_rectangle((160, 190, 740, 560), 12, fill=(127, 29, 29), outline=(252, 165, 165), width=3)

    d.rectangle((200, 240, 700, 340), fill=(30, 30, 30))

    d.text((250, 265), "LEFT pair   |   RIGHT pair", fill=(254, 226, 226), font=font(28, True))

    d.text((220, 380), "RPWM / LPWM  1 kHz PWM", fill=(255, 255, 255), font=font(24))

    d.text((220, 450), "Arduino Uno slave  OR  Pi GPIO", fill=(254, 202, 202), font=font(22))

    return save(im, "comp_bts.jpg")





def gps():

    im, d = card((16, 24, 40))

    label(d, "NEO-7M GPS Module", "Tells the rover where it is")

    d.rounded_rectangle((280, 200, 620, 500), 14, fill=(30, 41, 59), outline=(125, 211, 252), width=3)

    d.rounded_rectangle((340, 240, 560, 380), 8, fill=(226, 232, 240))

    d.text((365, 290), "CERAMIC", fill=(15, 23, 42), font=font(26, True))

    d.text((365, 325), "ANTENNA", fill=(15, 23, 42), font=font(26, True))

    d.text((320, 420), "UART 9600  ?  Pi RX", fill=(186, 230, 253), font=font(22))

    d.text((300, 540), "Waypoint navigation (Haversine)", fill=(148, 163, 184), font=font(20))

    return save(im, "comp_gps.jpg")





def compass():

    im, d = card()

    label(d, "HMC5883L Compass", "Tells the rover which way it faces")

    d.rounded_rectangle((300, 200, 600, 500), 16, fill=(76, 29, 149), outline=(196, 181, 253), width=3)

    cx, cy, r = 450, 350, 90

    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(250, 250, 250), width=4)

    d.line((cx, cy - 70, cx, cy + 70), fill=(248, 113, 113), width=4)

    d.polygon([(cx, cy - 80), (cx - 14, cy - 40), (cx + 14, cy - 40)], fill=(248, 113, 113))

    d.text((330, 530), "I2C 0x1E  shared with ADS1115", fill=(221, 214, 254), font=font(20))

    return save(im, "comp_compass.jpg")





def buck():

    im, d = card((40, 28, 10))

    label(d, "LM2596 Buck Converter", "12 V battery  ?  safe 5 V for Pi & pump")

    d.rounded_rectangle((200, 220, 700, 500), 12, fill=(120, 53, 15), outline=(253, 186, 116), width=3)

    d.ellipse((250, 280, 380, 410), fill=(80, 80, 90))

    d.text((270, 330), "COIL", fill=(255, 255, 255), font=font(20, True))

    d.text((420, 310), "IN 12 V", fill=(254, 215, 170), font=font(24, True))

    d.text((420, 360), "OUT 5.0 V", fill=(187, 247, 208), font=font(24, True))

    return save(im, "comp_buck.jpg")





def chassis():

    im, d = card((24, 24, 28))

    label(d, "4WD Aluminium Chassis", "Four 12 V geared motors + frame")

    d.rounded_rectangle((220, 260, 680, 480), 20, fill=(71, 85, 105), outline=(203, 213, 225), width=3)

    for x, y in ((200, 240), (640, 240), (200, 460), (640, 460)):

        d.ellipse((x, y, x + 80, y + 80), fill=(15, 15, 18), outline=(148, 163, 184), width=4)

    d.text((360, 350), "ROVER", fill=(255, 255, 255), font=font(32, True))

    return save(im, "comp_chassis.jpg")





def arduino():

    im, d = card((12, 28, 36))

    label(d, "Arduino Uno R3 (Slave)", "Motors, probe servo, ultrasonic - USB serial")

    d.rounded_rectangle((200, 180, 700, 560), 16, fill=(14, 116, 144), outline=(103, 232, 249), width=3)

    d.rectangle((240, 220, 520, 400), fill=(15, 23, 42))

    d.text((270, 280), "ATmega328P", fill=(165, 243, 252), font=font(28, True))

    d.rectangle((560, 220, 670, 300), fill=(0, 0, 0))

    d.text((575, 245), "USB", fill=(255, 255, 255), font=font(22, True))

    d.text((250, 440), "115200 baud  ?  Raspberry Pi", fill=(255, 255, 255), font=font(22))

    d.text((250, 490), "Frees Pi CPU for AI inference", fill=(165, 243, 252), font=font(20))

    return save(im, "comp_arduino.jpg")





def ultra():

    im, d = card()

    label(d, "HC-SR04 Ultrasonic (x2)", "Front / rear distance (Arduino slave)")

    d.rounded_rectangle((200, 220, 700, 500), 14, fill=(51, 65, 85), outline=(148, 163, 184), width=3)

    d.ellipse((260, 280, 420, 440), fill=(226, 232, 240), outline=(100, 116, 139), width=3)

    d.ellipse((480, 280, 640, 440), fill=(226, 232, 240), outline=(100, 116, 139), width=3)

    d.ellipse((310, 330, 370, 390), fill=(30, 41, 59))

    d.ellipse((530, 330, 590, 390), fill=(30, 41, 59))

    return save(im, "comp_ultra.jpg")





def battery():

    im, d = card((32, 20, 12))

    label(d, "12 V Battery Pack", "Powers motors, cutter, and buck 5 V rail")

    d.rounded_rectangle((250, 240, 650, 500), 18, fill=(69, 26, 3), outline=(253, 186, 116), width=4)

    d.text((340, 340), "12 V  7 Ah", fill=(255, 247, 237), font=font(40, True))

    d.rectangle((300, 220, 360, 250), fill=(220, 38, 38))

    d.rectangle((540, 220, 600, 250), fill=(15, 15, 18))

    return save(im, "comp_battery.jpg")





def buzzer():

    im, d = card()

    label(d, "Buzzer + Red LED", "Sounds and lights when disease is found")

    d.ellipse((220, 240, 420, 440), fill=(30, 30, 30), outline=(148, 163, 184), width=4)

    d.ellipse((280, 300, 360, 380), fill=(71, 85, 105))

    d.ellipse((500, 260, 680, 440), fill=(220, 38, 38), outline=(254, 202, 202), width=4)

    d.ellipse((560, 320, 620, 380), fill=(254, 226, 226))

    d.text((250, 500), "GPIO22 buzzer", fill=(226, 232, 240), font=font(22))

    d.text((520, 500), "GPIO23 LED", fill=(254, 202, 202), font=font(22))

    return save(im, "comp_alert.jpg")





def leaf_class(name, color, spots=None, filename=""):

    im = Image.new("RGB", (640, 640), (15, 28, 22))

    d = ImageDraw.Draw(im)

    d.rounded_rectangle((20, 20, 620, 620), 24, fill=(12, 24, 18), outline=(16, 185, 129), width=3)

    d.ellipse((140, 120, 500, 500), fill=color)

    d.polygon([(310, 480), (340, 480), (330, 580), (300, 580)], fill=(21, 128, 61))

    if spots == "brown":

        for xy in [(220, 220, 270, 270), (360, 180, 420, 240), (280, 340, 340, 400), (400, 320, 450, 370)]:

            d.ellipse(xy, fill=(120, 53, 15))

    elif spots == "yellow":

        d.ellipse((140, 120, 500, 500), fill=(202, 138, 4))

        d.ellipse((220, 200, 300, 280), fill=(34, 197, 94))

    elif spots == "dry":

        d.ellipse((140, 120, 500, 500), fill=(120, 80, 40))

        d.line((180, 200, 460, 420), fill=(69, 26, 3), width=6)

        d.line((420, 180, 200, 430), fill=(69, 26, 3), width=5)

    elif spots == "bg":

        d.rectangle((80, 140, 560, 500), fill=(87, 83, 78))

        d.text((180, 280), "NOT A LEAF", fill=(255, 255, 255), font=font(36, True))

    d.text((40, 40), name, fill=(236, 253, 245), font=font(28, True))

    return save(im, filename)





def architecture():

    import matplotlib

    matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch



    fig, ax = plt.subplots(figsize=(16, 9), dpi=140)

    fig.patch.set_facecolor("#0d233a")

    ax.set_xlim(0, 16)

    ax.set_ylim(0, 9)

    ax.axis("off")

    ax.set_title("AgroNex-Pi System Architecture", color="#e2e8f0", fontsize=20, pad=12, fontweight="bold")



    def box(x, y, w, h, text, color, fs=9):

        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",

                           facecolor=color, edgecolor="white", linewidth=1.2)

        ax.add_patch(p)

        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color="white",

                fontsize=fs, fontweight="bold", wrap=True)



    box(0.3, 6.6, 3.2, 1.8, "SENSORS\nSoil  Water  DHT\nCamera  GPS  Compass\nUltrasonic", "#0369a1", 10)

    box(0.3, 3.6, 3.2, 2.4, "POWER\n12 V Battery\nLM2596 ? 5 V\nCommon ground", "#b45309", 10)

    box(0.3, 0.4, 3.2, 2.6, "ACTUATORS\nPump  Cutter\n4WD motors\nProbe servo  Alerts", "#065f46", 10)



    box(4.4, 2.6, 4.4, 4.4, "RASPBERRY PI 4\n(main controller)\n\nPython FSM\nTFLite MobileNetV2\nFlask dashboard\nAWS relay", "#14532d", 12)

    box(4.4, 0.4, 4.4, 1.8, "ARDUINO UNO SLAVE\nUSB 115200 baud\nMotors + servo + HC-SR04", "#0e7490", 10)



    box(9.6, 5.8, 3.0, 2.4, "EDGE AI\nMobileNetV2\nTFLite quantized\n5-gate pipeline", "#6d28d9", 10)

    box(12.8, 5.8, 2.9, 2.4, "LOCAL UI\nFlask :5000\nGauges + control", "#1d4ed8", 10)

    box(9.6, 2.8, 6.1, 2.4, "AWS CLOUD\nAPI Gateway ? Lambda ? S3\nLive dashboard + remote commands", "#1e3a8a", 11)

    box(9.6, 0.4, 6.1, 2.0, "STORAGE\nSQLite logs  |  scan JPEGs  |  labels + .tflite", "#334155", 10)



    for a, b in [((3.5, 7.4), (4.4, 5.4)), ((3.5, 4.6), (4.4, 4.4)), ((3.5, 1.6), (4.4, 3.2)),

                 ((6.6, 2.6), (6.6, 2.2)), ((8.8, 5.4), (9.6, 6.8)), ((8.8, 4.6), (9.6, 4.0))]:

        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=14, color="#34d399", lw=1.6))

    fig.tight_layout()

    path = os.path.join(BASE, "architecture.png")

    fig.savefig(path, facecolor=fig.get_facecolor())

    plt.close()

    Image.open(path).convert("RGB").save(os.path.join(BASE, "architecture.jpg"), quality=92)

    return path





def flowchart():

    import matplotlib

    matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch



    fig, ax = plt.subplots(figsize=(16, 9), dpi=140)

    fig.patch.set_facecolor("#0d233a")

    ax.set_xlim(0, 16)

    ax.set_ylim(0, 9)

    ax.axis("off")

    ax.set_title("AgroNex-Pi Main Flowchart", color="#e2e8f0", fontsize=20, pad=10, fontweight="bold")



    def box(x, y, w, h, text, color="#065f46"):

        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.12",

                           facecolor=color, edgecolor="white", lw=1.1)

        ax.add_patch(p)

        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color="white", fontsize=9, fontweight="bold")



    def diamond(x, y, w, h, text):

        pts = [(x + w / 2, y + h), (x + w, y + h / 2), (x + w / 2, y), (x, y + h / 2)]

        ax.add_patch(Polygon(pts, closed=True, facecolor="#1e3a8a", edgecolor="white", lw=1.1))

        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color="white", fontsize=8, fontweight="bold")



    box(6.4, 8.1, 3.2, 0.7, "BOOT  (init modules)", "#14532d")

    box(6.4, 7.1, 3.2, 0.7, "SELF-TEST hardware", "#14532d")

    diamond(5.9, 5.9, 4.2, 1.0, "All sensors OK?")

    box(11.2, 6.05, 4.0, 0.7, "SAFE STATE\nactuators OFF", "#7f1d1d")

    box(6.4, 5.0, 3.2, 0.7, "IDLE ? MONITORING", "#065f46")

    diamond(5.7, 3.7, 4.6, 1.1, "What is needed?")

    box(0.3, 2.2, 3.4, 1.1, "IRRIGATING\nsoil < 35% ? pump ON\nstop at 65% / 60 s", "#0e7490")

    box(4.2, 2.2, 3.4, 1.1, "CUTTING\n30 s mow cycle\nmotors stopped", "#b45309")

    box(8.2, 2.2, 3.6, 1.1, "NAVIGATING\nGPS + compass\narrive ? 2.5 m", "#1d4ed8")

    box(12.2, 2.2, 3.5, 1.1, "SCANNING\n5-gate TFLite AI\nalert if diseased", "#6d28d9")

    box(4.8, 0.35, 6.4, 1.1, "Log to SQLite  ?  push AWS every 5 s  ?  back to MONITORING", "#334155")



    arrows = [

        ((8.0, 8.1), (8.0, 7.8)),

        ((8.0, 7.1), (8.0, 6.9)),

        ((10.1, 6.4), (11.2, 6.4)),

        ((8.0, 5.9), (8.0, 5.7)),

        ((8.0, 5.0), (8.0, 4.8)),

        ((6.2, 4.1), (2.0, 3.3)),

        ((7.2, 3.7), (5.9, 3.3)),

        ((9.0, 3.7), (10.0, 3.3)),

        ((9.8, 4.1), (13.9, 3.3)),

        ((2.0, 2.2), (6.5, 1.45)),

        ((5.9, 2.2), (7.2, 1.45)),

        ((10.0, 2.2), (8.6, 1.45)),

        ((13.9, 2.2), (9.8, 1.45)),

    ]

    for a, b in arrows:

        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=12, color="#34d399", lw=1.3))

    ax.text(10.4, 6.7, "NO", color="#fca5a5", fontsize=9)

    ax.text(8.15, 5.75, "YES", color="#86efac", fontsize=9)

    path = os.path.join(BASE, "flowchart.png")

    fig.savefig(path, facecolor=fig.get_facecolor())

    plt.close()

    Image.open(path).convert("RGB").save(os.path.join(BASE, "flowchart.jpg"), quality=92)

    return path





def dashboard_local():

    im = Image.new("RGB", (1600, 900), (15, 23, 42))

    d = ImageDraw.Draw(im)

    d.rectangle((0, 0, 1600, 90), fill=(6, 95, 70))

    d.text((40, 22), "AgroNex-Pi  -  Local Dashboard", fill=(255, 255, 255), font=font(36, True))

    d.text((40, 58), "http://raspberrypi:5000   |   FSM: MONITORING   |   Wi-Fi OK", fill=(167, 243, 208), font=font(18))

    tiles = [

        (40, 120, "Soil moisture", "42%", (16, 185, 129)),

        (430, 120, "Water tank", "78%", (6, 182, 212)),

        (820, 120, "Temperature", "28  degC", (251, 191, 36)),

        (1210, 120, "Humidity", "61%", (96, 165, 250)),

    ]

    for x, y, t, v, c in tiles:

        d.rounded_rectangle((x, y, x + 350, y + 180), 18, fill=(30, 41, 59), outline=c, width=3)

        d.text((x + 24, y + 24), t, fill=(148, 163, 184), font=font(20))

        d.text((x + 24, y + 70), v, fill=c, font=font(48, True))

    d.rounded_rectangle((40, 330, 980, 860), 18, fill=(30, 41, 59))

    d.text((60, 350), "Soil moisture (last 30 min)", fill=(226, 232, 240), font=font(22, True))

    pts = []

    for i in range(40):

        x = 80 + i * 22

        val = 40 + 12 * math.sin(i / 5) + (8 if i > 22 else 0)

        y = 780 - val * 4

        pts.append((x, y))

    d.line(pts, fill=(16, 185, 129), width=4)

    d.line((80, 620, 940, 620), fill=(239, 68, 68), width=2)

    d.text((90, 590), "ON threshold 35%", fill=(252, 165, 165), font=font(16))

    d.rounded_rectangle((1020, 330, 1560, 860), 18, fill=(30, 41, 59))

    d.text((1040, 350), "Latest disease scan", fill=(226, 232, 240), font=font(22, True))

    d.ellipse((1120, 420, 1460, 740), fill=(22, 101, 52), outline=(74, 222, 128), width=4)

    d.ellipse((1220, 500, 1280, 560), fill=(120, 53, 15))

    d.text((1040, 770), "Local_unhealthy   86%", fill=(252, 165, 165), font=font(22, True))

    d.text((1040, 810), "Advice: isolate leaf, neem spray", fill=(148, 163, 184), font=font(18))

    return save(im, "dash_local.jpg")





def dashboard_cloud():

    im = Image.new("RGB", (1600, 900), (7, 13, 20))

    d = ImageDraw.Draw(im)

    d.rectangle((0, 0, 260, 900), fill=(14, 25, 41))

    d.text((24, 30), "AgroNex", fill=(16, 185, 129), font=font(28, True))

    d.text((24, 68), "Cloud Command", fill=(148, 163, 184), font=font(16))

    for i, name in enumerate(["Overview", "Disease", "Navigation", "Controls", "Library", "Chatbot"]):

        y = 130 + i * 55

        fill = (16, 185, 129) if i == 0 else (20, 35, 58)

        d.rounded_rectangle((18, y, 242, y + 44), 10, fill=fill)

        d.text((36, y + 10), name, fill=(255, 255, 255), font=font(18))

    d.text((300, 28), "Farm live telemetry   -   ap-south-1   -   S3 state.json", fill=(226, 232, 240), font=font(26, True))

    d.text((300, 70), "Updated 3 s ago   |   Rover ONLINE   |   GPS fix 18 sats", fill=(52, 211, 153), font=font(18))

    boxes = [

        (300, 120, "Soil", "38%", "#"),

        (620, 120, "Pump", "STANDBY", "#"),

        (940, 120, "Cutter", "IDLE", "#"),

        (1260, 120, "AI", "HEALTHY", "#"),

    ]

    cols = [(16, 185, 129), (251, 191, 36), (148, 163, 184), (52, 211, 153)]

    for (x, y, t, v, _), c in zip(boxes, cols):

        d.rounded_rectangle((x, y, x + 300, y + 150), 16, fill=(14, 25, 41), outline=c, width=2)

        d.text((x + 20, y + 24), t, fill=(148, 163, 184), font=font(18))

        d.text((x + 20, y + 70), v, fill=c, font=font(32, True))

    d.rounded_rectangle((300, 300, 980, 860), 16, fill=(14, 25, 41), outline=(56, 189, 248), width=2)

    d.text((320, 320), "Waypoint map (Leaflet)", fill=(186, 230, 253), font=font(22, True))

    d.rectangle((340, 370, 940, 820), fill=(15, 40, 30))

    d.ellipse((520, 500, 760, 720), fill=(22, 80, 50))

    d.line([(400, 760), (500, 640), (620, 580), (780, 500), (860, 420)], fill=(56, 189, 248), width=5)

    d.ellipse((850, 405, 870, 425), fill=(239, 68, 68))

    d.text((360, 780), "Current  ?  WP2  (1.8 m remaining)", fill=(125, 211, 252), font=font(18))

    d.rounded_rectangle((1020, 300, 1560, 860), 16, fill=(14, 25, 41), outline=(16, 185, 129), width=2)

    d.text((1040, 320), "Remote controls", fill=(167, 243, 208), font=font(22, True))

    for i, (lab, col) in enumerate([("PUMP ON", (6, 95, 70)), ("CUTTER", (120, 53, 15)),

                                    ("E-STOP", (127, 29, 29)), ("SCAN NOW", (30, 64, 175))]):

        y = 390 + i * 100

        d.rounded_rectangle((1060, y, 1520, y + 70), 12, fill=col)

        d.text((1120, y + 18), lab, fill=(255, 255, 255), font=font(24, True))

    return save(im, "dash_cloud.jpg")





def dashboard_disease():

    im = Image.new("RGB", (1600, 900), (15, 23, 42))

    d = ImageDraw.Draw(im)

    d.rectangle((0, 0, 1600, 80), fill=(88, 28, 135))

    d.text((40, 22), "Disease tab  -  3x3 majority vote  -  70% confidence gate", fill=(255, 255, 255), font=font(28, True))

    d.rounded_rectangle((40, 110, 820, 860), 16, fill=(30, 41, 59))

    d.text((60, 130), "Camera frame + 3x3 grid", fill=(221, 214, 254), font=font(22, True))

    d.ellipse((180, 220, 680, 720), fill=(21, 128, 61))

    d.ellipse((360, 340, 440, 430), fill=(120, 53, 15))

    d.ellipse((480, 480, 560, 560), fill=(69, 26, 3))

    for i in range(1, 3):

        d.line((180 + i * 167, 220, 180 + i * 167, 720), fill=(255, 255, 255), width=2)

        d.line((180, 220 + i * 167, 680, 220 + i * 167), fill=(255, 255, 255), width=2)

    d.text((60, 780), "Diseased segments: 6 / 9   ?   ALERT", fill=(252, 165, 165), font=font(22, True))

    d.rounded_rectangle((860, 110, 1560, 860), 16, fill=(30, 41, 59))

    d.text((880, 140), "Result", fill=(226, 232, 240), font=font(26, True))

    rows = [

        "Class: Local_unhealthy",

        "Confidence: 86%",

        "Quality gate: PASS (sharp, bright)",

        "Green pixels: 41%  (leaf present)",

        "Vote: 6 of 9 diseased",

        "Cause: fungal / pest damage",

        "Treat: neem oil, remove bad leaves",

        "Buzzer + LED: ON",

        "Saved: SQLite + S3 scan JPEG",

    ]

    for i, r in enumerate(rows):

        d.text((900, 220 + i * 60), "*  " + r, fill=(196, 181, 253), font=font(22))

    return save(im, "dash_disease.jpg")





def capture_process():

    im = Image.new("RGB", (1400, 500), (13, 35, 58))

    d = ImageDraw.Draw(im)

    steps = [

        (40, "1. Focus\nOV5647 at\n10-15 cm"),

        (310, "2. Shoot\nPi camera\nlive studio"),

        (580, "3. Folder\nfield_dataset\n/class_name"),

        (850, "4. Mix light\nsun + indoor\nmany angles"),

        (1120, "5. Train\nMobileNetV2\nexport TFLite"),

    ]

    d.text((40, 20), "How we built the local plant dataset", fill=(255, 255, 255), font=font(28, True))

    for x, t in steps:

        d.rounded_rectangle((x, 90, x + 240, 420), 18, fill=(6, 95, 70))

        d.text((x + 20, 150), t, fill=(236, 253, 245), font=font(22, True))

        if x != 1120:

            d.polygon([(x + 250, 240), (x + 250, 270), (x + 280, 255)], fill=(52, 211, 153))

    return save(im, "dataset_process.jpg")





def integration():

    import matplotlib

    matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch



    fig, ax = plt.subplots(figsize=(16, 8), dpi=140)

    fig.patch.set_facecolor("#0d233a")

    ax.set_xlim(0, 16)

    ax.set_ylim(0, 8)

    ax.axis("off")

    ax.set_title("Hardware  ?  Software Integration", color="white", fontsize=18, fontweight="bold")



    def box(x, y, w, h, t, c):

        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",

                                    facecolor=c, edgecolor="white", lw=1))

        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", color="white", fontsize=9, fontweight="bold")



    box(0.4, 5.5, 3.4, 1.8, "I2C bus\nADS1115 + Compass\nsmbus2", "#0369a1")

    box(4.2, 5.5, 3.4, 1.8, "1-wire / UART / CSI\nDHT  GPS  Camera\nadafruit / serial / picamera2", "#1d4ed8")

    box(8.0, 5.5, 3.6, 1.8, "GPIO + PWM\nRelays  Motors  Alerts\nRPi.GPIO / Arduino", "#b45309")

    box(12.0, 5.5, 3.5, 1.8, "USB serial\nPi ? Arduino Uno\n115200 baud", "#0e7490")

    box(4.0, 2.8, 8.0, 2.0, "hardware.py  HAL\nOnly this file talks to pins. Controllers get objects.", "#14532d")

    box(0.5, 0.4, 3.5, 1.8, "irrigation.py\ncutter.py", "#065f46")

    box(4.3, 0.4, 3.6, 1.8, "navigation.py\ndisease_detect.py", "#6d28d9")

    box(8.3, 0.4, 3.5, 1.8, "main.py FSM\n4 threads", "#1e3a8a")

    box(12.1, 0.4, 3.4, 1.8, "app.py + aws_relay\nFlask + S3", "#334155")

    for a, b in [((2.1, 5.5), (6.5, 4.8)), ((5.9, 5.5), (7.5, 4.8)), ((9.8, 5.5), (8.5, 4.8)),

                 ((13.7, 5.5), (9.5, 4.8)), ((8.0, 2.8), (2.2, 2.2)), ((8.0, 2.8), (6.1, 2.2)),

                 ((8.0, 2.8), (10.0, 2.2)), ((8.0, 2.8), (13.8, 2.2))]:

        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=12, color="#34d399", lw=1.2))

    path = os.path.join(BASE, "integration.png")

    fig.savefig(path, facecolor=fig.get_facecolor())

    plt.close()

    Image.open(path).convert("RGB").save(os.path.join(BASE, "integration.jpg"), quality=92)





def main():

    makers = [rpi, soil, ads, water, dht, camera, relay, pump, cutter, bts, gps, compass,

              buck, chassis, arduino, ultra, battery, buzzer]

    for fn in makers:

        fn()

    leaf_class("Local_healthy", (34, 197, 94), None, "leaf_healthy.jpg")

    leaf_class("Local_unhealthy", (22, 163, 74), "brown", "leaf_unhealthy.jpg")

    leaf_class("Local_yellow", (202, 138, 4), "yellow", "leaf_yellow.jpg")

    leaf_class("Local_dried", (120, 80, 40), "dry", "leaf_dried.jpg")

    leaf_class("background_not_a_leaf", (87, 83, 78), "bg", "leaf_bg.jpg")

    architecture()

    flowchart()

    dashboard_local()

    dashboard_cloud()

    dashboard_disease()

    capture_process()

    integration()

    print("Assets ready in", BASE)





if __name__ == "__main__":

    main()

