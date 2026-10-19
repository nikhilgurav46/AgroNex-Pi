# AgroNex-Pi PPT — Full Explanation (simple words)

Use this file while you practise. **Speak only the short lines on the slides.** Use the paragraphs here when an examiner says “explain this.”

**Files**
- Presentation: `AgroNex_Pi_Presentation.pptx` (widescreen 16:9, 36 slides)
- This notes file: `PPT_EXPLANATION.md`

**Before the viva, fill in:** team names, guide name, college name, and your **real validation accuracy** from the last training log (replace the 88–95% range if you have the exact number).

**Time:** about 12–15 minutes if you stay short. Spend extra time on dataset + model slides (18–25). Point at pictures; do not read every bullet.

---

## How to present

1. Title ? problem ? SDGs ? papers ? hardware pictures ? architecture/flowchart ? **dataset & ML** ? tests ? dashboards ? end.
2. If they ask only about AI, jump to slides 18–25.
3. If they ask only about hardware, jump to slides 9–17.

---

## Slide 1 — Title

**Say:** This is our major project, **AgroNex-Pi**: a small farm robot. It drives, waters plants, cuts grass, photographs leaves, and tells us if the plant looks sick. The main brain is a **Raspberry Pi 4**. A helper board, **Arduino Uno**, handles motors.

**Words they may ask**
- **Autonomous** — after we start it, it follows programmed rules by itself (with safety limits). A human should still watch it.
- **Edge-AI** — the neural network runs on the robot, not only on the internet.
- **Telemetry** — sending live sensor numbers (soil %, temperature, GPS) to a screen or cloud.
- **IoT** — Internet of Things: sensors + software + (optional) cloud talking together.

---

## Slide 2 — Contents

Just tell the flow in one sentence: problem ? SDGs ? literature ? parts ? diagrams ? how we made photos and the AI ? tests ? dashboard ? conclusion.

---

## Slide 3 — Abstract

This is the whole project in 30 seconds.

We built a **low-cost rover**. It does **five jobs**:

1. **Irrigation** — waters only when soil is dry.
2. **Grass cutting** — on a timer.
3. **Navigation** — GPS + compass toward a point in the field.
4. **Disease detection** — camera + AI on the Pi.
5. **Dashboard / cloud** — farmer watches from phone or laptop.

The AI is **MobileNetV2** converted to **TensorFlow Lite** (small and fast). We trained it on public plant photos **and** photos we took of **local plants** with our own camera.

**Safety:** pump, cutter and wheels do not run at the same time, so the battery voltage does not collapse.

---

## Slide 4 — Introduction

**Problem**
- FAO (Food and Agriculture Organization of the UN) says plant disease can destroy about **10–40%** of crops.
- Small farmers cannot pay an expert to walk the field every day.
- Timer watering wastes water (it waters even if soil is already wet).
- Phone apps that send every photo to the cloud fail when the village has weak 4G.

**Our idea**  
One chassis, one Pi, sensors + motors + camera. The farmer still watches, but checking soil, watering, and scanning a leaf can be automatic.

---

## Slide 5 — Objectives

What we planned to finish:

1. One affordable rover for water + mow + drive + scan.
2. Disease AI that works **offline** on the Pi, trained with **our** photos.
3. Smart watering: pump only if soil moisture is below **35%**.
4. Dashboards: local website always; AWS cloud if internet exists.
5. Safety interlocks so high-current devices do not fight for power.

---

## Slide 6 — Sustainable Development Goals (SDG)

SDGs are **17 world goals** from the United Nations (Agenda 2030). Our project maps to four:

| SDG | Simple meaning here |
|-----|---------------------|
| **2 Zero Hunger** | Catch disease early so more food is saved. |
| **6 Clean Water** | Water only if soil is under **35%**. Stop at **65%**. |
| **9 Industry & Innovation** | Cheap robot + on-device AI, not a very expensive machine. |
| **12 Responsible production** | Spray / treat only when the model is sure, not “just in case”. |

If asked “which SDG is strongest?” say **2 and 6** — food and water.

---

## Slide 7 — Literature review

**Literature review** = we read what other people already built, so we do not repeat it blindly.

- **Mohanty 2016** — famous paper. A CNN on the **PlantVillage** photo set got about **99%** in the lab. Gap: photos are clean, often white background. Real garden is messy. Also no robot.
- **Bac 2014** — harvest robots in greenhouses. Gap: expensive, needs a structured farm.
- **Plantix / PlantSnap** — phone apps. Gap: usually need internet for every photo.
- **IoT irrigation papers** — soil sensor + pump. Gap: no disease AI, no driving.
- **GPS farm robots** — can drive. Gap: usually no watering + AI together.

**CNN** = Convolutional Neural Network. It is a type of AI that looks at images by sliding small filters to find patterns (edges, spots, colour).

---

## Slide 8 — Gap analysis

**Gap** = what is still missing in those papers/products.

1. Irrigation, mowing, GPS and AI are usually **separate** student projects.
2. Lab datasets **do not look like** a Raspberry Pi camera in a garden. This mismatch is called **domain shift**. A 99% lab model can fall to ~40–50% in the field.
3. Rural farms have weak internet, so **cloud-only AI** is risky.

**What we did**
- Combine all five jobs on one chassis.
- Photograph **our** plants with **our** camera, then train.
- Run AI **on the Pi**. Cloud is optional extra.

---

## Slides 9–10 — Components (with pictures)

Walk left to right. One line each.

### Brain
- **Raspberry Pi 4B (4 GB)** — main computer: Python, AI, website.
- **Arduino Uno R3** — helper. Pi sends serial text at **115200 baud**. Arduino moves motors, soil-probe servo, ultrasonics. This keeps the Pi free for AI.

### Sensors
- **Capacitive soil sensor** — analog voltage changes with wetness. Lasts longer than rusty two-pin probes.
- **ADS1115** — 16-bit ADC. Pi has **no analog pins**, so we convert voltage to a number on I2C address **0x48**. Channel **A0** = soil, **A1** = tank water.
- **HW-038 water level** — so we do not run the pump on an empty tank (stop below ~20%).
- **DHT11/22** — air temperature and humidity (GPIO4).
- **OV5647 CSI camera** — leaf photos (`picamera2`).
- **NEO-7M GPS** — latitude/longitude (UART).
- **HMC5883L compass** — heading (I2C 0x1E, same wires as ADS1115).
- **HC-SR04 x2** — distance front/back (on Arduino).

### Actuators / power
- **2-channel 5 V relay (active LOW)** — GPIO LOW = ON. CH1 pump, CH2 cutter.
- **5 V mini pump** — must run from **buck 5 V**, never raw 12 V (it will burn).
- **12 V cutter motor** — grass; there should be a **physical kill switch**.
- **BTS7960 x2** — high-current H-bridges for 4 wheels (left pair / right pair).
- **4WD aluminium chassis**.
- **LM2596 / XL4015 buck** — 12 V ? **5.0 V** for Pi and pump.
- **12 V battery** (~7 Ah).
- **Buzzer + LED** — disease alarm (GPIO22 / 23).

**Tiny dictionary**
- **I2C** — two wires (SDA/SCL) shared by several chips.
- **UART** — serial TX/RX (used for GPS and Pi–Arduino).
- **PWM** — fast on/off pulses to control motor speed.
- **H-bridge** — chip that can spin a motor forward or reverse.
- **ADC** — Analog to Digital Converter (voltage ? number).
- **CSI** — camera ribbon port on the Pi.
- **Active-LOW relay** — the relay turns ON when the Pi pin is 0 V, not 3.3 V.

---

## Slide 11 — System specification

Memorize these numbers:

- Irrigation: **ON if soil < 35%**, **OFF if ? 65%**, max pump **60 s**, wait **120 s** before next pump.
- Disease: confidence **? 70%**, **more than 4 of 9** patches diseased.
- GPS: ignore old fix (older than **5 s**), arrived if distance **? 2.5 m**.
- Cloud: POST every **5 s**. Dashboard refresh about **3 s**.
- AI input: **224 x 224** RGB. Latency about **280 ms** on Pi CPU.
- Arduino link: USB serial **115200 baud**.

---

## Slide 12 — System architecture (block diagram)

This picture is the real hardware/software map of AgroNex-Pi.

Explain **boxes**, not every line.

**Left — power and actuators**
- 12 V battery ? buck converter ? 5 V for Pi and pump.
- Relays switch pump and cutter.
- Common ground (all GNDs tied together). If grounds float, motors behave randomly and GPIO can get damaged.

**Centre — brains**
- **Raspberry Pi 4** = supervisor: FSM, AI, Flask, AWS relay.
- **Arduino Uno** = muscles: motors, probe, ultrasonic.

**Right — sensing and data**
- Camera, ADC, DHT, GPS, compass.
- Edge AI pipeline.
- Local dashboard + AWS (API Gateway ? Lambda ? S3).

**Data flow in one sentence:** sensors ? Pi decides ? motors/pump/alerts ? log in SQLite ? optional cloud.

---

## Slide 13 — Software layers

We did **not** dump all GPIO code in one file.

1. **hardware.py** — the only place that talks to pins. If a sensor changes, we edit this file. This is a **HAL** (Hardware Abstraction Layer).
2. **Controllers** — `irrigation.py`, `cutter.py`, `navigation.py`, `disease_detect.py`. They ask hardware objects “what is moisture?” They do not bit-bang pins.
3. **main.py** — **FSM** (finite state machine): the robot is always in **one named state**.
4. **Four threads** = four jobs at once:
   - 3-second control loop
   - disease scanner
   - web server (Flask port **5000**)
   - watchdog (if control-loop heartbeat is older than **30 s**, log timeout)
5. **SAFE_STATE** — something failed at boot ? no motors, no pump.
6. **aws_relay.py** — optional cloud upload.

**FSM states (names):** BOOT, SELF_TEST, IDLE, MONITORING, IRRIGATING, CUTTING, NAVIGATING, SCANNING, SAFE_STATE.

---

## Slide 14 — System flowchart (simple)

Trace with a finger:

BOOT ? SELF_TEST ? if fail, SAFE_STATE.  
If pass ? IDLE ? **MONITORING**.  
From monitoring, pick a job:

- soil dry ? **IRRIGATING**
- mow time ? **CUTTING**
- waypoint waiting ? **NAVIGATING**
- leaf in view / button ? **SCANNING**

Then log, maybe upload, back to MONITORING.

**Hysteresis (irrigation):** not one number. If we used “water at 50%” the pump would chatter ON/OFF. Two numbers (35 and 65) give a **band**.

**Haversine:** formula for distance between two GPS points on Earth.

**Compass error > 12 degrees** ? short pivot; else drive **1 s** and check again. We have **no wheel encoder**, so we do **stop-and-recheck** (safer than driving blind).

---

## Slide 15 — Formal operational flowchart

Same story in a more “exam diagram” style: power on, init drivers, self-test, then the monitoring loop with branches (obstacle / irrigate / cut / navigate / scan). If self-test fails, go to SAFE_STATE.

You only need to walk the **main path**. Do not read every box.

---

## Slides 16–17 — Hardware and software integration

**Question they love:** “How does a Python line become water in the soil?”

Answer, step by step:

1. Capacitive probe voltage goes to **ADS1115 A0**.
2. Software reads a raw integer (example: dry air ~26300, wet ~9500).
3. Two-point formula turns it into **moisture %**.
4. If % < 35, tank is OK (>20%), and cooldown finished ? `hardware` sets relay pin **LOW**.
5. Pump spins. Chassis is already stopped (interlock).
6. When % ? 65 or 60 s timeout ? pin HIGH (OFF). SQLite stores the cycle.

**Boot safety:** active-LOW relays can glitch ON if the pin is 0 at startup. We set the pin **HIGH first**, then switch it to OUTPUT.

**Interlock:** before pump or cutter, **stop motors**. One 12 V battery cannot happily drive wheels + cutter together.

**Arduino:** Pi sends a short text command (motor speeds / servo). Uno applies PWM. If USB unplugs, code can fall back to Pi GPIO PWM.

**Offline:** Flask on port **5000** always. AWS is extra. If Wi-Fi dies, farming still works.

---

## Slides 18–20 — How we built the dataset (most important ML part)

### Why we took our own photos

**PlantVillage / Kaggle** photos: studio, often white background, phone or DSLR.  
**Our OV5647:** noisier, different colour, soil/pots in the background, focus at **10–15 cm**.

If you train only on studio photos, field accuracy can drop to about **40–50%**. Training on the **same camera** is **domain adaptation / in-situ data**. Accuracy can jump toward **~90%**.

### What we did, step by step

1. **Focus the lens ring** so a leaf at 10–15 cm is sharp (factory focus is often infinity).
2. Run **`capture_field_dataset.py`** on the Pi (live web studio on port 8080, or GUI).
3. Save into folders under `field_dataset/`:
   - `Local_healthy`
   - `Local_unhealthy` (spots / damage)
   - `Local_yellow`
   - `Local_dried`
   - `background_not_a_leaf` (pots, soil, table — **negative class**)
4. Shoot many **angles** (top, 15–30° tilt, 5–15 cm close-up) and two **lights** (sun + room). About **30–50 photos per class** is a practical student set; more is better.
5. Optionally also keep PlantVillage tomato / potato / pepper (capped about **180 per class** so one class does not dominate).
6. Merge field folders into `training_subset/`.
7. Split **80% train / 20% validation** (fixed random seed so it is repeatable). Field images are **not capped**.

**Label = folder name.** The model never “reads English”. It learns “folder A looks like this colour/texture.”

**Negative class** teaches: “this is not a leaf, do not scream disease.”

**Scripts**
- Collect: `capture_field_dataset.py`
- Train local 5-class: `train_custom_plant_model.py`
- Train PlantVillage mix + field: `train_plant_disease_model.py`

---

## Slide 21 — Building the model (transfer learning)

### What is the model?

A **CNN** slides filters over the image. **MobileNetV2** is a **small** CNN made for phones and Pi. It uses **depthwise separable convolutions** (cheaper math) and **inverted residuals**.

**ImageNet** = a huge photo contest dataset (1000 classes: cats, cars, …). MobileNetV2 already knows generic vision (edges, textures). We **reuse** that. That is **transfer learning**. We only teach it **our** leaf classes.

### Architecture we used

Input **224 x 224 x 3**  
? MobileNetV2 **without** the old 1000-class top  
? **Global Average Pooling** (turn the feature map into one vector)  
? **Dropout 0.3** (randomly ignore 30% of neurons while training so it cannot memorize)  
? **Dense + Softmax** (one probability per class; they add to 1)

Pixels scaled to **[-1, 1]** with `(x / 127.5) - 1`. This is what MobileNet expects.

### Two-stage training

**Stage 1 — frozen backbone**  
Do not smash ImageNet weights. Only train the new last layer. Optimizer **Adam**, learning rate **0.001**. Loss = **sparse categorical cross-entropy** (standard for integer labels).

**Stage 2 — fine-tune**  
Unfreeze upper layers (bottom ~100 layers stay frozen). Learning rate **10x or 100x smaller** (`1e-4` or `1e-5`) so we **nudge** features toward leaves.

### Export

Convert Keras model ? **quantized TFLite** (`Optimize.DEFAULT`, dynamic-range). Copy to Pi:

- `models/plant_model.tflite`
- `models/labels.txt`

(We also keep `custom_plant_model.tflite` / `custom_labels.txt`.)

**Why TFLite?** Full TensorFlow is huge. TFLite is a slim runtime for **inference only** (using the model, not training) on the Pi CPU.

**Why MobileNetV2 not ResNet/VGG?** Those are heavy. Pi has no big GPU.

---

## Slide 22 — ML techniques (one line each)

| Technique | Plain meaning |
|-----------|----------------|
| Transfer learning | Reuse a brain that already saw millions of photos. |
| Data augmentation | Fake extra photos: flip, rotate, zoom, contrast, small shift. Helps with sun and tilt. Applied in the **data pipeline**, not baked into the Pi model (some Keras random layers break TFLite). |
| Class weights | If “dried” has fewer photos, those examples count more in the loss. |
| Dropout 0.3 | Fight **overfitting** (great on train photos, bad on a new leaf). |
| Early stopping | If validation loss stops improving, stop and restore best weights. |
| Quantization | Smaller, faster `.tflite` for Pi CPU. |
| [-1, 1] normalize | Same math as original MobileNet training. |
| 5-gate inference | Extra rules after the model, so a blurry pot is not called “disease”. |

---

## Slide 23 — On-device inference (5 gates)

Training is only half. In the garden we **refuse** bad photos.

1. **Quality / Laplacian variance** — blurry or too dark ? `RETAKE_NEEDED`, not disease. Laplacian = a sharpness number.
2. **Green % in HSV** — if green pixels < **15%**, it is soil/sky, skip. HSV = Hue-Saturation-Value colour space; green hue is roughly 35–90.
3. **3 x 3 grid** — nine mini-images. One dirty corner should not decide the whole plant.
4. **Majority vote** — need **more than 4/9** diseased patches.
5. **70% confidence** — softmax must be sure.

Then `disease_db.py` adds **name, cause, treatment**. Buzzer/LED. Save JPEG. Upload if cloud is on.

This is how we cut **false alarms**.

**Dual model (if asked):** environment variable can switch a **custom local 5-class** model or a **PlantVillage 8-class** model (tomato/potato/pepper) without rewriting code.

---

## Slides 24–25 — Testing and ML results

**Hardware:** each `test_*.py` script (soil, water, DHT, relay, motors, camera, alerts). Say they **passed** on the real rover.

**Irrigation:** hysteresis band observed; timeout works.

**GPS:** arrival within about **2.5 m**. Consumer GPS is ±2–5 m. Do **not** claim centimetres.

**ML numbers to quote** (honest range — replace with your log if you have it):

- Local 5-class: about **88–93%** validation.
- PlantVillage mix: about **91–95%**.
- Without our photos, field camera often ~**40–50%** (domain shift).
- About **280 ms** per frame on Pi 4 CPU.

If the examiner has your training log, **read the real `val_accuracy`**. That is stronger than a range.

**Confusion matrix (if asked):** table of true class vs predicted class. Diagonal = correct.

**Live demo script:** `python test_disease_camera.py`

---

## Slides 26–30 — Dashboards (point at the photos)

### Local Flask (`templates/dashboard.html`, port 5000)
Works on LAN with **no AWS**. Soil %, tank, temp, humidity, FSM badge, pump/cutter buttons, scan button, logs. Screenshot shows the real UI (values fill when the rover is running).

### AWS Cloud Command Center
Pi ? **API Gateway** ? **Lambda** ? **S3** `state.json`. Page on S3 reads it every few seconds. Commands go the other way (`command.json`). Map = Leaflet.js. Login for farmers/admin. Disease alert banner, live tiles, E-STOP, chatbot (English / Hindi / Marathi).

### Farm command center
A friendlier “farm” theme of the same telemetry: soil 48%, air 30.5 °C, humidity 61%, pump/cutter OFF.

### Disease capture UI
Upload or take a leaf photo, press Analyze. Result + recent scans.

### 3 x 3 vote graphic
Shows how 6 of 9 patches diseased + 86% confidence becomes an alert, then advice and buzzer.

**If internet dies:** local dashboard still runs. Only cloud tiles freeze.

---

## Slide 31 — Applications

- Small farm (1–5 acre): auto water + leaf check.
- Home / terrace garden: mow + phone monitoring.
- Nursery: catch disease early, less chemical spray.
- College lab: teaching IoT, robotics, edge AI.
- Off-grid plot: Flask works without internet.

Stress **cost** and **offline AI**.

---

## Slide 32 — Future scope

Do **not** claim we already did these. Say “next”:

- Stronger obstacle avoidance, wheel encoders (odometry).
- Solar charging, battery voltage monitor.
- **YOLO**: first **find** the leaf, then classify disease.
- More crops, rain sensor to skip watering.
- Faster AI (INT8 / Coral TPU).
- Phone app / OTA updates.

---

## Slide 33 — Conclusion

One sentence: **five farm jobs, one cheap rover, AI on the edge, data we photographed ourselves.**

Safety interlocks + FSM keep power under control. Cloud is extra; farming still works offline. Smart farming does not need a 10-lakh machine.

---

## Slide 34 — References

Do not read all. “Full list is on the slide; main papers are FAO, MobileNetV2, Mohanty PlantVillage.”

---

## Slide 35 — Acknowledgement

Thank guide, HOD, college, family, open-source (TensorFlow, Raspberry Pi, PlantVillage). **Put real names** in the square brackets on the slide.

---

## Slide 36 — Thank you

Smile, stop talking, wait for questions.

---

# Extra viva Q&A (simple)

**Q. Why MobileNetV2 not ResNet/VGG?**  
A. Those are heavy. Pi has no big GPU. MobileNet is built for mobile/edge.

**Q. Why TFLite?**  
A. Full TensorFlow is huge. TFLite is the slim runtime for inference only.

**Q. Why Arduino plus Pi?**  
A. Motors and servos need reliable PWM. Pi CPU should stay free for the neural net. USB serial links them.

**Q. Why capacitive soil sensor?**  
A. Resistive probes corrode in soil. Capacitive lasts longer.

**Q. Why 35% and 65%?**  
A. Hysteresis. One threshold makes the pump flicker.

**Q. What is softmax?**  
A. Turns raw scores into probabilities that add to 1.

**Q. What is overfitting?**  
A. Model memorizes training photos and fails on a new leaf. Dropout + augmentation + early stopping fight this.

**Q. What is quantization?**  
A. Storing weights with less precision so the file is smaller and the Pi CPU is faster.

**Q. Can it detect any plant?**  
A. Only classes it was trained on. New crop ? new photos ? retrain.

**Q. Obstacle detection?**  
A. Ultrasonics are on the Arduino path; we still require a **human observer**. No LiDAR. Do not oversell.

**Q. Indoor GPS?**  
A. NEO-7M needs sky. Indoor / dense trees = no good fix. Rover waits.

**Q. Why 224 x 224?**  
A. That is the official MobileNetV2 input size. Other sizes would need a different pretrained network.

**Q. Train/val split?**  
A. 80% train, 20% validation. Validation photos are held out so we measure generalization, not memory.

---

# 60-second closing speech (memorize)

> AgroNex-Pi is a Raspberry Pi farm rover with an Arduino helper. It waters using soil moisture with a 35–65% band, mows on a schedule, drives to GPS points, and classifies local leaves on-device with MobileNetV2 TFLite. We collected our own photos because lab datasets do not match the Pi camera. Five software gates reduce false disease alarms. A local dashboard always works; AWS is for remote view. The design is low-cost and aligned with SDGs 2, 6, 9 and 12.

---

*Fill in your exact validation accuracy, team names, and guide name before the presentation.*
