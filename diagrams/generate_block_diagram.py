def generate_svg():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1100" width="100%" height="100%" style="background-color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <!-- Gradients -->
    <linearGradient id="grad-title" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#34d399"/>
      <stop offset="100%" stop-color="#3b82f6"/>
    </linearGradient>
    
    <linearGradient id="grad-pi" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>

    <linearGradient id="grad-esp" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#1e1b4b"/>
    </linearGradient>

    <linearGradient id="grad-pwr" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#b45309"/>
      <stop offset="100%" stop-color="#d97706"/>
    </linearGradient>

    <linearGradient id="grad-motor" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0369a1"/>
      <stop offset="100%" stop-color="#0284c7"/>
    </linearGradient>

    <linearGradient id="grad-actuator" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#065f46"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>

    <!-- Drop Shadows -->
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>
    </filter>

    <!-- Arrow Markers -->
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#34d399"/>
    </marker>
    <marker id="arrow-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#fbbf24"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#f87171"/>
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#c084fc"/>
    </marker>
  </defs>

  <!-- ================= HEADER ================= -->
  <rect x="30" y="25" width="1540" height="75" rx="12" fill="#1e293b" stroke="#334155" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="60" y="62" font-size="24" font-weight="800" fill="url(#grad-title)" letter-spacing="1">AGRONEX-PI : COMPLETE SYSTEM ARCHITECTURE &amp; PROCESS BLOCK DIAGRAM</text>
  <text x="60" y="85" font-size="13" font-weight="500" fill="#94a3b8">Autonomous Agricultural Rover — Power Isolation, Multi-Brain Interfacing, Closed-Loop Drive &amp; Edge Vision Pipeline</text>
  <rect x="1380" y="45" width="160" height="34" rx="17" fill="#065f46" stroke="#10b981" stroke-width="1"/>
  <circle cx="1400" cy="62" r="5" fill="#34d399"/>
  <text x="1415" y="67" font-size="12" font-weight="700" fill="#ecfdf5">HARDWARE v2.0</text>

  <!-- ================= LEFT COLUMN: POWER & ACTUATION ================= -->
  
  <!-- Group 1: Power Subsystem -->
  <rect x="30" y="120" width="310" height="340" rx="14" fill="#1e293b" stroke="#475569" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="30" y="120" width="310" height="42" rx="14" fill="url(#grad-pwr)"/>
  <text x="50" y="147" font-size="15" font-weight="700" fill="#ffffff">1. POWER DISTRIBUTION</text>
  
  <!-- 12V Li-Ion Battery -->
  <rect x="50" y="180" width="270" height="65" rx="8" fill="#0f172a" stroke="#d97706" stroke-width="2"/>
  <text x="70" y="208" font-size="14" font-weight="700" fill="#fef3c7">12V Li-Ion Battery Pack</text>
  <text x="70" y="228" font-size="11" fill="#cbd5e1">12.6V Peak / High Discharge Capacity</text>
  
  <!-- Buck Converter -->
  <rect x="50" y="275" width="270" height="70" rx="8" fill="#0f172a" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="70" y="303" font-size="13" font-weight="700" fill="#93c5fd">XL4015 / MP1584 Buck Converter</text>
  <text x="70" y="322" font-size="11" fill="#cbd5e1">Step-down: 12V → 5.1V / 3A Clean Rail</text>
  <text x="70" y="337" font-size="10" font-weight="600" fill="#34d399">✓ Decoupled logic rail (Anti-Brownout)</text>

  <!-- Star Ground -->
  <rect x="50" y="370" width="270" height="65" rx="8" fill="#0f172a" stroke="#64748b" stroke-width="1.5"/>
  <text x="70" y="398" font-size="13" font-weight="700" fill="#e2e8f0">Central Star Grounding Point</text>
  <text x="70" y="418" font-size="11" fill="#94a3b8">Joins Motor GND + Logic GND (No loops)</text>

  <!-- Power Wire Connections -->
  <path d="M 185 245 L 185 275" fill="none" stroke="#fbbf24" stroke-width="2.5" marker-end="url(#arrow-amber)"/>
  <path d="M 185 345 L 185 370" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,3"/>


  <!-- Group 2: High-Current Actuators (Pump & Cutter) -->
  <rect x="30" y="480" width="310" height="290" rx="14" fill="#1e293b" stroke="#475569" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="30" y="480" width="310" height="42" rx="14" fill="url(#grad-actuator)"/>
  <text x="50" y="507" font-size="15" font-weight="700" fill="#ffffff">2. RELAY-ISOLATED ACTUATORS</text>

  <!-- 2-Channel Relay Module -->
  <rect x="50" y="538" width="270" height="75" rx="8" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
  <text x="70" y="563" font-size="13" font-weight="700" fill="#6ee7b7">2-Channel 5V Relay Board</text>
  <text x="70" y="582" font-size="11" fill="#94a3b8">Active-LOW Optocoupler Triggered</text>
  <text x="70" y="598" font-size="10" fill="#fef08a">Safety: Init HIGH before GPIO.setup</text>

  <!-- 12V Water Pump -->
  <rect x="50" y="630" width="125" height="65" rx="8" fill="#064e3b" stroke="#34d399" stroke-width="1.5"/>
  <text x="60" y="655" font-size="11" font-weight="700" fill="#ffffff">12V Water Pump</text>
  <text x="60" y="672" font-size="9" fill="#a7f3d0">CH1 (GPIO17)</text>
  <text x="60" y="685" font-size="9" fill="#fcd34d">Max 60s runtime</text>

  <!-- 12V Cutter Motor -->
  <rect x="195" y="630" width="125" height="65" rx="8" fill="#78350f" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="205" y="655" font-size="11" font-weight="700" fill="#ffffff">12V Grass Cutter</text>
  <text x="205" y="672" font-size="9" fill="#fde68a">CH2 (GPIO27)</text>
  <text x="205" y="685" font-size="9" fill="#fca5a5">Motor Interlock</text>

  <!-- Water Tank Sensor -->
  <rect x="50" y="708" width="270" height="46" rx="6" fill="#0f172a" stroke="#0ea5e9" stroke-width="1"/>
  <text x="65" y="730" font-size="11" font-weight="700" fill="#38bdf8">Water Tank Float/Level Switch</text>
  <text x="65" y="744" font-size="9.5" fill="#94a3b8">Signals EMPTY → triggers Auto-Docking refill</text>

  <!-- Wiring: 12V direct to relays -->
  <path d="M 320 212 Q 360 212 360 560 L 320 560" fill="none" stroke="#fbbf24" stroke-width="2" stroke-dasharray="5,4" marker-end="url(#arrow-amber)"/>


  <!-- Group 3: Docking Station -->
  <rect x="30" y="790" width="310" height="275" rx="14" fill="#1e293b" stroke="#475569" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="30" y="790" width="310" height="42" rx="14" fill="#475569"/>
  <text x="50" y="817" font-size="15" font-weight="700" fill="#ffffff">3. GPS WAYPOINT MISSION</text>

  <rect x="50" y="848" width="270" height="90" rx="8" fill="#0f172a" stroke="#cbd5e1" stroke-width="1.5"/>
  <!-- GPS mission representation -->
  <rect x="65" y="860" width="40" height="40" fill="#ffffff"/>
  <rect x="73" y="868" width="24" height="24" fill="#000000"/>
  <rect x="79" y="874" width="12" height="12" fill="#ffffff"/>
  <text x="120" y="875" font-size="12" font-weight="700" fill="#f8fafc">NEO-7M Coordinates</text>
  <text x="120" y="893" font-size="10" fill="#94a3b8">Family: tag36h11 (ID: 0)</text>
  <text x="120" y="908" font-size="9.5" fill="#38bdf8">Visual Servoing Docking Reference</text>
  <text x="120" y="922" font-size="9.5" fill="#34d399">Positional Precision: ±5 mm</text>

  <rect x="50" y="955" width="270" height="85" rx="8" fill="#0f172a" stroke="#334155" stroke-width="1"/>
  <text x="65" y="978" font-size="11.5" font-weight="700" fill="#cbd5e1">Docking Refill Mechanism:</text>
  <text x="65" y="996" font-size="10" fill="#94a3b8">1. Visual Alignment via Picamera2</text>
  <text x="65" y="1010" font-size="10" fill="#94a3b8">2. Precision deceleration (&lt;0.1 m/s)</text>
  <text x="65" y="1024" font-size="10" fill="#94a3b8">3. Solenoid Water Valve triggers on contact</text>


  <!-- ================= CENTER COLUMN: THE MAIN COMPUTERS ================= -->

  <!-- Group 4: BRAIN 1 - RASPBERRY PI 4B -->
  <rect x="390" y="120" width="480" height="520" rx="14" fill="url(#grad-pi)" stroke="#10b981" stroke-width="2" filter="url(#shadow)"/>
  <rect x="390" y="120" width="480" height="46" rx="14" fill="#064e3b"/>
  <text x="415" y="149" font-size="16" font-weight="800" fill="#34d399">BRAIN 1 : RASPBERRY PI 4B (4GB RAM)</text>
  <text x="740" y="149" font-size="11" font-weight="600" fill="#a7f3d0">HIGH-LEVEL COGNITION</text>

  <!-- Pi Internal Subsystems -->
  <!-- 1. OS & Supervisor -->
  <rect x="410" y="180" width="440" height="80" rx="8" fill="#0f172a" stroke="#334155" stroke-width="1.5"/>
  <text x="425" y="203" font-size="13" font-weight="700" fill="#f8fafc">FSM Supervisor &amp; Watchdog Thread (main.py)</text>
  <text x="425" y="222" font-size="10.5" fill="#94a3b8">• State Machine: BOOT → SELF_TEST → IDLE → MONITORING → SAFE_STATE</text>
  <text x="425" y="237" font-size="10.5" fill="#94a3b8">• Watchdog trip after 90s heartbeat loss | POSIX SIGINT/SIGTERM handlers</text>
  <text x="425" y="251" font-size="10" font-weight="600" fill="#38bdf8">• Thread-safe Shared Telemetry Cache (_telemetry_cache)</text>

  <!-- 2. AI Edge Vision -->
  <rect x="410" y="272" width="440" height="95" rx="8" fill="#0f172a" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="425" y="295" font-size="13" font-weight="700" fill="#60a5fa">Edge AI Leaf Disease Classifier (disease_detect.py)</text>
  <text x="425" y="313" font-size="10.5" fill="#cbd5e1">• Model: MobileNetV2 Quantized (plant_model.tflite, ~55ms latency)</text>
  <text x="425" y="328" font-size="10.5" fill="#cbd5e1">• Quality Gates: Laplacian Variance &gt; 50 (anti-blur) | Luminance 35–225</text>
  <text x="425" y="343" font-size="10.5" fill="#cbd5e1">• Softmax Confidence Gate ≥ 0.70 | Links to Agronomic Database (disease_db.py)</text>
  <text x="425" y="358" font-size="10" font-weight="600" fill="#34d399">• PlantVillage 7-class recognition (Tomato/Potato blights vs healthy)</text>

  <!-- 3. Web UI & REST API -->
  <rect x="410" y="380" width="440" height="75" rx="8" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
  <text x="425" y="403" font-size="13" font-weight="700" fill="#34d399">Flask Web Dashboard &amp; REST Server (app.py)</text>
  <text x="425" y="422" font-size="10.5" fill="#94a3b8">• Zero-CDN Offline Dashboard (templates/dashboard.html &amp; dashboard.css)</text>
  <text x="425" y="437" font-size="10.5" fill="#94a3b8">• Endpoints: /api/sensor, /api/history, /api/control, /api/estop, /api/health</text>
  <text x="425" y="450" font-size="10" font-weight="600" fill="#fbbf24">• Real-time SVG soil chart, gauge alerts &amp; Emergency Stop triggers</text>

  <!-- 4. Database Layer -->
  <rect x="410" y="468" width="440" height="55" rx="8" fill="#0f172a" stroke="#475569" stroke-width="1"/>
  <text x="425" y="490" font-size="12" font-weight="700" fill="#cbd5e1">SQLite High-Concurrency Storage (database.py)</text>
  <text x="425" y="508" font-size="10" fill="#94a3b8">WAL Mode (Write-Ahead Logging) | Tables: sensor_log, irrigation_events, disease_log</text>

  <!-- 5. GPIO / Hardware Abstraction -->
  <rect x="410" y="535" width="440" height="85" rx="8" fill="#0f172a" stroke="#818cf8" stroke-width="1"/>
  <text x="425" y="556" font-size="12" font-weight="700" fill="#a5b4fc">Hardware Abstraction Layer (hardware.py)</text>
  <text x="425" y="573" font-size="10" fill="#cbd5e1">• SPI0 Bus: GPIO 10(MOSI), 9(MISO), 11(SCLK), 8(CE0) with threading.Lock()</text>
  <text x="425" y="588" font-size="10" fill="#cbd5e1">• 1-Wire: GPIO 4 (DHT) | Outputs: GPIO 17(Pump), 27(Cutter), 22(Buzzer), 23(LED)</text>
  <text x="425" y="603" font-size="10" font-weight="600" fill="#f87171">• Global emergency_stop(): grounds PWM, de-energizes all relays immediately</text>


  <!-- Group 5: GPS + COMPASS NAVIGATION -->
  <rect x="390" y="665" width="480" height="400" rx="14" fill="url(#grad-esp)" stroke="#6366f1" stroke-width="2" filter="url(#shadow)"/>
  <rect x="390" y="665" width="480" height="46" rx="14" fill="#312e81"/>
  <text x="415" y="694" font-size="16" font-weight="800" fill="#a5b4fc">GPS + COMPASS NAVIGATION</text>
  <text x="735" y="694" font-size="11" font-weight="600" fill="#c7d2fe">PI SUPERVISED</text>

  <!-- GPS and compass navigation modules -->
  <rect x="410" y="725" width="440" height="80" rx="8" fill="#0f172a" stroke="#4f46e5" stroke-width="1.5"/>
  <text x="425" y="748" font-size="13" font-weight="700" fill="#c7d2fe">NEO-7M GPS Waypoint Position</text>
  <text x="425" y="767" font-size="10.5" fill="#94a3b8">• UART NMEA location fixes from the outdoor GPS receiver</text>
  <text x="425" y="782" font-size="10.5" fill="#94a3b8">• Stale or invalid GPS fix keeps the rover stationary</text>
  <text x="425" y="796" font-size="10" font-weight="600" fill="#34d399">• Uses configured latitude/longitude mission waypoints</text>

  <rect x="410" y="818" width="440" height="80" rx="8" fill="#0f172a" stroke="#4f46e5" stroke-width="1.5"/>
  <text x="425" y="841" font-size="13" font-weight="700" fill="#c7d2fe">HMC5883L Compass Heading Control</text>
  <text x="425" y="860" font-size="10.5" fill="#94a3b8">• I2C magnetic heading aligns rover to waypoint bearing</text>
  <text x="425" y="875" font-size="10.5" fill="#94a3b8">• Turns and drives in short stop-and-recheck bursts</text>
  <text x="425" y="889" font-size="10" font-weight="600" fill="#38bdf8">• 1 kHz PWM commands drive dual BTS7960 H-bridges</text>

  <rect x="410" y="910" width="440" height="65" rx="8" fill="#0f172a" stroke="#dc2626" stroke-width="1"/>
  <text x="425" y="932" font-size="12.5" font-weight="700" fill="#fca5a5">Navigation Failsafe</text>
  <text x="425" y="950" font-size="10" fill="#94a3b8">• No waypoint, no valid GPS fix, or E-stop keeps motors stopped</text>
  <text x="425" y="964" font-size="10" fill="#fca5a5">• No obstacle sensor: human safety observer is required</text>

  <rect x="410" y="985" width="440" height="65" rx="8" fill="#0f172a" stroke="#6366f1" stroke-width="1"/>
  <text x="425" y="1007" font-size="12" font-weight="700" fill="#c7d2fe">Raspberry Pi Sensor Buses</text>
  <text x="425" y="1025" font-size="10" fill="#94a3b8">• NEO-7M UART @ 9600 baud | HMC5883L I2C bus</text>
  <text x="425" y="1039" font-size="10" fill="#38bdf8">• Pi evaluates bearing, heading and safety before every drive slice</text>


  <!-- Inter-Brain Communication Arrow -->
  <path d="M 630 640 L 630 665" fill="none" stroke="#a855f7" stroke-width="4" marker-end="url(#arrow-purple)"/>
  <path d="M 645 665 L 645 640" fill="none" stroke="#a855f7" stroke-width="4" marker-end="url(#arrow-purple)"/>
  <rect x="575" y="643" width="120" height="18" rx="4" fill="#581c87"/>
  <text x="585" y="656" font-size="9" font-weight="700" fill="#f3e8ff">UART SERIAL BUS</text>

  <!-- Power delivery from Buck Converter to Pi & ESP -->
  <path d="M 320 310 L 390 310" fill="none" stroke="#3b82f6" stroke-width="3" marker-end="url(#arrow-blue)"/>
  <rect x="330" y="298" width="50" height="15" rx="3" fill="#1e3a8a"/>
  <text x="335" y="309" font-size="8.5" font-weight="700" fill="#bfdbfe">5.1V RAIL</text>

  <path d="M 355 310 Q 365 310 365 740 L 390 740" fill="none" stroke="#3b82f6" stroke-width="2" stroke-dasharray="4,3" marker-end="url(#arrow-blue)"/>


  <!-- ================= RIGHT COLUMN: SENSORS & 4WD CHASSIS ================= -->

  <!-- Group 6: Environmental & Vision Sensors -->
  <rect x="910" y="120" width="310" height="420" rx="14" fill="#1e293b" stroke="#475569" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="910" y="120" width="310" height="42" rx="14" fill="#0284c7"/>
  <text x="930" y="147" font-size="15" font-weight="700" fill="#ffffff">5. SENSOR PERCEPTION MATRIX</text>

  <!-- Picamera2 -->
  <rect x="930" y="175" width="270" height="75" rx="8" fill="#0f172a" stroke="#0284c7" stroke-width="1.5"/>
  <text x="950" y="200" font-size="13" font-weight="700" fill="#7dd3fc">Picamera2 (MIPI CSI-2)</text>
  <text x="950" y="218" font-size="10.5" fill="#94a3b8">Singleton camera driver | 1080p/720p</text>
  <text x="950" y="233" font-size="10" fill="#38bdf8">Captures leaves for offline disease AI</text>

  <!-- MCP3008 ADC + Soil Sensor -->
  <rect x="930" y="260" width="270" height="90" rx="8" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
  <text x="950" y="283" font-size="13" font-weight="700" fill="#6ee7b7">MCP3008 10-bit SPI ADC</text>
  <text x="950" y="301" font-size="10.5" fill="#cbd5e1">Channel 0: Capacitive Soil Probe v1.2</text>
  <text x="950" y="316" font-size="10" fill="#94a3b8">Hysteresis: &lt;35% ON, &gt;65% OFF</text>
  <text x="950" y="331" font-size="9.5" fill="#34d399">Corrosion-resistant analog output (0–3.3V)</text>

  <!-- DHT11/22 Climate Probe -->
  <rect x="930" y="360" width="270" height="60" rx="8" fill="#0f172a" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="950" y="383" font-size="12.5" font-weight="700" fill="#fcd34d">DHT11 / DHT22 Sensor</text>
  <text x="950" y="401" font-size="10" fill="#94a3b8">1-Wire Bus (GPIO4) with 10k pullup</text>
  <text x="950" y="413" font-size="9.5" fill="#cbd5e1">Ambient Temp (°C) &amp; Relative Humidity (%)</text>

  <!-- Alert Buzzer & LED -->
  <rect x="930" y="430" width="270" height="50" rx="8" fill="#0f172a" stroke="#ef4444" stroke-width="1"/>
  <text x="950" y="452" font-size="11.5" font-weight="700" fill="#fca5a5">Piezo Buzzer &amp; Red Alert LED</text>
  <text x="950" y="468" font-size="9.5" fill="#94a3b8">Audio/Optical Alarm on Disease Detection / Fault</text>

  <!-- GPS / Compass -->
  <rect x="930" y="490" width="270" height="42" rx="6" fill="#0f172a" stroke="#818cf8" stroke-width="1"/>
  <text x="945" y="510" font-size="11" font-weight="700" fill="#c7d2fe">NEO-7M GPS + HMC5883L Compass</text>
  <text x="945" y="524" font-size="9" fill="#94a3b8">UART location fixes + I2C magnetic heading</text>

  <!-- Connections from Sensors to Pi -->
  <path d="M 930 210 L 870 210" fill="none" stroke="#38bdf8" stroke-width="2" marker-end="url(#arrow-blue)"/>
  <path d="M 930 300 L 870 300" fill="none" stroke="#34d399" stroke-width="2" marker-end="url(#arrow-green)"/>
  <path d="M 930 390 L 870 390" fill="none" stroke="#fbbf24" stroke-width="2" marker-end="url(#arrow-amber)"/>


  <!-- Group 7: 4WD CHASSIS & BTS7960 -->
  <rect x="910" y="560" width="310" height="505" rx="14" fill="#1e293b" stroke="#475569" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="910" y="560" width="310" height="42" rx="14" fill="url(#grad-motor)"/>
  <text x="930" y="587" font-size="15" font-weight="700" fill="#ffffff">6. 4WD CHASSIS &amp; BTS7960</text>

  <!-- Dual BTS7960 Drivers -->
  <rect x="930" y="615" width="270" height="85" rx="8" fill="#0f172a" stroke="#0284c7" stroke-width="1.5"/>
  <text x="950" y="638" font-size="13" font-weight="700" fill="#38bdf8">Dual BTS7960 High-Current Drivers</text>
  <text x="950" y="656" font-size="10.5" fill="#94a3b8">• Driver #1: Front Left &amp; Rear Left Motors</text>
  <text x="950" y="670" font-size="10.5" fill="#94a3b8">• Driver #2: Front Right &amp; Rear Right Motors</text>
  <text x="950" y="685" font-size="10" font-weight="600" fill="#fcd34d">• 12V motor rail + 1 kHz PWM speed control</text>

  <!-- 4 Motors Diagram -->
  <g transform="translate(930, 715)">
    <!-- FL -->
    <rect x="0" y="0" width="125" height="70" rx="8" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="12" y="24" font-size="11" font-weight="700" fill="#ffffff">FRONT LEFT</text>
    <text x="12" y="40" font-size="9" fill="#94a3b8">12V 300 RPM</text>
    <rect x="12" y="48" width="100" height="15" rx="3" fill="#0369a1"/>
    <text x="18" y="59" font-size="8.5" font-weight="600" fill="#e0f2fe">12V 10A DC Motor</text>

    <!-- FR -->
    <rect x="145" y="0" width="125" height="70" rx="8" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="157" y="24" font-size="11" font-weight="700" fill="#ffffff">FRONT RIGHT</text>
    <text x="157" y="40" font-size="9" fill="#94a3b8">12V 300 RPM</text>
    <rect x="157" y="48" width="100" height="15" rx="3" fill="#0369a1"/>
    <text x="163" y="59" font-size="8.5" font-weight="600" fill="#e0f2fe">12V 10A DC Motor</text>

    <!-- RL -->
    <rect x="0" y="85" width="125" height="70" rx="8" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="12" y="109" font-size="11" font-weight="700" fill="#ffffff">REAR LEFT</text>
    <text x="12" y="125" font-size="9" fill="#94a3b8">12V 300 RPM</text>
    <rect x="12" y="133" width="100" height="15" rx="3" fill="#0369a1"/>
    <text x="18" y="144" font-size="8.5" font-weight="600" fill="#e0f2fe">12V 10A DC Motor</text>

    <!-- RR -->
    <rect x="145" y="85" width="125" height="70" rx="8" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>
    <text x="157" y="109" font-size="11" font-weight="700" fill="#ffffff">REAR RIGHT</text>
    <text x="157" y="125" font-size="9" fill="#94a3b8">12V 300 RPM</text>
    <rect x="157" y="133" width="100" height="15" rx="3" fill="#0369a1"/>
    <text x="163" y="144" font-size="8.5" font-weight="600" fill="#e0f2fe">12V 10A DC Motor</text>
  </g>

  <!-- BTS7960 detail box -->
  <rect x="930" y="885" width="270" height="90" rx="8" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
  <text x="945" y="908" font-size="12" font-weight="700" fill="#6ee7b7">BTS7960 Safety Notes:</text>
  <text x="945" y="926" font-size="10" fill="#94a3b8">• One driver per left/right motor pair</text>
  <text x="945" y="940" font-size="10" fill="#94a3b8">• R_EN and L_EN hardware enabled</text>
  <text x="945" y="954" font-size="10" fill="#94a3b8">• Fuse and cool for motor stall current</text>
  <text x="945" y="968" font-size="9.5" font-weight="600" fill="#34d399">• RPWM/LPWM GPIO controls only</text>

  <!-- Skid Steering Logic Callout -->
  <rect x="930" y="985" width="270" height="70" rx="8" fill="#0f172a" stroke="#475569" stroke-width="1"/>
  <text x="945" y="1008" font-size="11.5" font-weight="700" fill="#cbd5e1">Skid-Steering Kinematics:</text>
  <text x="945" y="1025" font-size="9.5" fill="#94a3b8">Forward: L_fwd + R_fwd | Turn Left: L_slow + R_fast</text>
  <text x="945" y="1039" font-size="9.5" fill="#94a3b8">Pivot In-Place: Left reverse (-PWM) + Right forward (+PWM)</text>

  <!-- Pi PWM connection to BTS7960 drivers -->
  <path d="M 870 770 L 930 660" fill="none" stroke="#38bdf8" stroke-width="2.5" marker-end="url(#arrow-blue)"/>
  <!-- GPS/compass feedback to Pi -->
  <path d="M 930 930 L 870 760" fill="none" stroke="#34d399" stroke-width="2" stroke-dasharray="4,3" marker-end="url(#arrow-green)"/>


  <!-- ================= FAR RIGHT COLUMN: DATAFLOW & UI ================= -->

  <!-- Group 8: Telemetry, Web UI & Cloud / Remote Monitoring -->
  <rect x="1260" y="120" width="310" height="945" rx="14" fill="#1e293b" stroke="#475569" stroke-width="1.5" filter="url(#shadow)"/>
  <rect x="1260" y="120" width="310" height="42" rx="14" fill="#334155"/>
  <text x="1280" y="147" font-size="15" font-weight="700" fill="#ffffff">7. DATA PIPELINE &amp; WEB DASHBOARD</text>

  <!-- Pipeline Flow 1: Vision -->
  <rect x="1280" y="180" width="270" height="155" rx="8" fill="#0f172a" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="1295" y="204" font-size="13" font-weight="700" fill="#60a5fa">A. Edge Vision AI Pipeline</text>
  <text x="1295" y="224" font-size="10" fill="#cbd5e1">1. Picamera2 frame acquisition (224×224)</text>
  <text x="1295" y="239" font-size="10" fill="#94a3b8">   ↓ Laplacian Variance (&gt;50) &amp; Lum (35-225)</text>
  <text x="1295" y="254" font-size="10" fill="#cbd5e1">2. TFLite Interpreter executes MobileNetV2</text>
  <text x="1295" y="269" font-size="10" fill="#94a3b8">   ↓ Softmax probability calculation</text>
  <text x="1295" y="284" font-size="10" fill="#cbd5e1">3. Confidence &gt; 70% threshold gating</text>
  <text x="1295" y="299" font-size="10" fill="#94a3b8">   ↓ Disease lookup in disease_db.py</text>
  <text x="1295" y="314" font-size="9.5" font-weight="600" fill="#34d399">4. Log to SQLite + Trigger Buzzer/LED</text>

  <!-- Pipeline Flow 2: Irrigation -->
  <rect x="1280" y="355" width="270" height="155" rx="8" fill="#0f172a" stroke="#10b981" stroke-width="1.5"/>
  <text x="1295" y="379" font-size="13" font-weight="700" fill="#34d399">B. Irrigation Control Pipeline</text>
  <text x="1295" y="399" font-size="10" fill="#cbd5e1">1. Polling MCP3008 ADC CH0 via SPI0</text>
  <text x="1295" y="414" font-size="10" fill="#94a3b8">   ↓ Calibrate Raw ADC (Dry 850, Wet 380)</text>
  <text x="1295" y="429" font-size="10" fill="#cbd5e1">2. Evaluate Soil Moisture Percentage</text>
  <text x="1295" y="444" font-size="10" fill="#94a3b8">   ↓ If &lt; 35% AND not in cooldown</text>
  <text x="1295" y="459" font-size="10" fill="#cbd5e1">3. Halt Chassis Drive (Probe Drag Safety)</text>
  <text x="1295" y="474" font-size="10" fill="#94a3b8">   ↓ Energize Pump Relay CH1 (Active-LOW)</text>
  <text x="1295" y="489" font-size="9.5" font-weight="600" fill="#fcd34d">4. Max 60s timeout / Cooldown 120s</text>

  <!-- Pipeline Flow 3: Mission & Docking -->
  <rect x="1280" y="530" width="270" height="175" rx="8" fill="#0f172a" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="1295" y="554" font-size="13" font-weight="700" fill="#fbbf24">C. Mission &amp; Docking Pipeline</text>
  <text x="1295" y="574" font-size="10" fill="#cbd5e1">1. Waypoint Patrol (Zone A → Zone B)</text>
  <text x="1295" y="589" font-size="10" fill="#94a3b8">   ↓ GPS freshness and compass heading check</text>
  <text x="1295" y="604" font-size="10" fill="#cbd5e1">2. Reactive Skid Avoidance &amp; Path Rejoin</text>
  <text x="1295" y="619" font-size="10" fill="#94a3b8">   ↓ Float Switch detects Low Water Tank</text>
  <text x="1295" y="634" font-size="10" fill="#cbd5e1">3. Save Current (X, Y, Heading) Position</text>
  <text x="1295" y="649" font-size="10" fill="#94a3b8">   ↓ Navigate to Docking Waypoint</text>
  <text x="1295" y="664" font-size="10" fill="#cbd5e1">4. GPS waypoint bearing and short drive slice</text>
  <text x="1295" y="679" font-size="9.5" font-weight="600" fill="#38bdf8">5. Return to Saved Coordinates &amp; Resume</text>

  <!-- Pipeline Flow 4: UI & Telemetry -->
  <rect x="1280" y="725" width="270" height="235" rx="8" fill="#0f172a" stroke="#818cf8" stroke-width="1.5"/>
  <text x="1295" y="749" font-size="13" font-weight="700" fill="#a5b4fc">D. Web Dashboard Telemetry</text>
  
  <rect x="1295" y="765" width="240" height="40" rx="5" fill="#1e293b" stroke="#334155"/>
  <text x="1305" y="783" font-size="10" font-weight="700" fill="#ffffff">SOIL MOISTURE</text>
  <text x="1305" y="797" font-size="12" font-weight="800" fill="#34d399">62.6% (OPTIMAL)</text>

  <rect x="1295" y="813" width="115" height="40" rx="5" fill="#1e293b" stroke="#334155"/>
  <text x="1305" y="830" font-size="9" font-weight="700" fill="#ffffff">TEMP</text>
  <text x="1305" y="845" font-size="11" font-weight="800" fill="#fcd34d">26.3 °C</text>

  <rect x="1420" y="813" width="115" height="40" rx="5" fill="#1e293b" stroke="#334155"/>
  <text x="1430" y="830" font-size="9" font-weight="700" fill="#ffffff">HUMIDITY</text>
  <text x="1430" y="845" font-size="11" font-weight="800" fill="#38bdf8">58.4 %</text>

  <rect x="1295" y="860" width="240" height="30" rx="5" fill="#1e293b" stroke="#334155"/>
  <text x="1305" y="879" font-size="9.5" fill="#cbd5e1">FSM State: <tspan font-weight="700" fill="#34d399">MONITORING</tspan></text>

  <rect x="1295" y="897" width="240" height="48" rx="6" fill="#7f1d1d" stroke="#ef4444"/>
  <text x="1325" y="919" font-size="11" font-weight="800" fill="#ffffff">GLOBAL EMERGENCY STOP</text>
  <text x="1340" y="934" font-size="9" fill="#fecaca">Instantly kills all actuators</text>

  <!-- Flow to Dashboard -->
  <path d="M 870 415 L 1280 770" fill="none" stroke="#a5b4fc" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow-purple)"/>

  <!-- ================= FOOTER / LEGEND ================= -->
  <rect x="30" y="1035" width="310" height="30" rx="6" fill="#1e293b" stroke="#334155"/>
  <circle cx="50" cy="1050" r="5" fill="#fbbf24"/>
  <text x="62" y="1054" font-size="10" fill="#cbd5e1">12V High-Current Rail</text>

  <circle cx="165" cy="1050" r="5" fill="#38bdf8"/>
  <text x="177" y="1054" font-size="10" fill="#cbd5e1">5.1V Logic Rail</text>

  <circle cx="255" cy="1050" r="5" fill="#34d399"/>
  <text x="267" y="1054" font-size="10" fill="#cbd5e1">Sensor Bus</text>

</svg>"""

    with open("diagrams/system_block_diagram.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("Successfully generated diagrams/system_block_diagram.svg")

if __name__ == "__main__":
    generate_svg()
