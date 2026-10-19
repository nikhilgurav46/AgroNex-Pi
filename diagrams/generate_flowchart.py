def generate_flowchart():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 2400" width="100%" height="100%" style="background-color: #0b1120; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <!-- Gradients -->
    <linearGradient id="grad-start" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#059669"/>
      <stop offset="100%" stop-color="#10b981"/>
    </linearGradient>
    <linearGradient id="grad-prep" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#334155"/>
    </linearGradient>
    <linearGradient id="grad-process" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284c7"/>
      <stop offset="100%" stop-color="#0369a1"/>
    </linearGradient>
    <linearGradient id="grad-io" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f766e"/>
      <stop offset="100%" stop-color="#115e59"/>
    </linearGradient>
    <linearGradient id="grad-decision" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#b45309"/>
      <stop offset="100%" stop-color="#d97706"/>
    </linearGradient>
    <linearGradient id="grad-stop" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#b91c1c"/>
      <stop offset="100%" stop-color="#ef4444"/>
    </linearGradient>
    <linearGradient id="grad-dock" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6366f1"/>
      <stop offset="100%" stop-color="#4f46e5"/>
    </linearGradient>

    <!-- Filters -->
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.5"/>
    </filter>

    <!-- Arrow Markers -->
    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#34d399"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#f87171"/>
    </marker>
    <marker id="arrow-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#fbbf24"/>
    </marker>
  </defs>

  <!-- ================= HEADER TITLE ================= -->
  <rect x="50" y="30" width="1500" height="90" rx="14" fill="#1e293b" stroke="#334155" stroke-width="2" filter="url(#shadow)"/>
  <text x="90" y="70" font-size="26" font-weight="800" fill="#34d399" letter-spacing="0.5">AGRONEX-PI : FORMAL SYSTEM OPERATIONAL FLOWCHART</text>
  <text x="90" y="98" font-size="13.5" font-weight="500" fill="#94a3b8">Standard Engineering Flowchart Symbols: Terminator (Oval) | Process (Rect) | Decision (Diamond) | I/O (Parallelogram) | Init (Hexagon)</text>

  <!-- Flowchart Legend Bar -->
  <g transform="translate(980, 50)">
    <!-- Oval -->
    <rect x="0" y="0" width="70" height="24" rx="12" fill="url(#grad-start)"/>
    <text x="14" y="16" font-size="10" font-weight="700" fill="#fff">Start/Stop</text>

    <!-- Rect -->
    <rect x="85" y="0" width="60" height="24" rx="4" fill="url(#grad-process)"/>
    <text x="94" y="16" font-size="10" font-weight="700" fill="#fff">Process</text>

    <!-- Diamond -->
    <polygon points="175,12 195,0 215,12 195,24" fill="url(#grad-decision)"/>
    <text x="180" y="16" font-size="9" font-weight="800" fill="#fff">Decide</text>

    <!-- Parallelogram -->
    <polygon points="235,24 245,0 295,0 285,24" fill="url(#grad-io)"/>
    <text x="252" y="16" font-size="9.5" font-weight="700" fill="#fff">Sensors</text>

    <!-- Hexagon -->
    <polygon points="310,12 320,0 365,0 375,12 365,24 320,24" fill="url(#grad-prep)"/>
    <text x="328" y="16" font-size="9.5" font-weight="700" fill="#fff">Init</text>
  </g>

  <!-- ================= 1. START / TERMINATOR ================= -->
  <!-- Shape: Oval (Terminator) -->
  <rect x="675" y="150" width="250" height="60" rx="30" fill="url(#grad-start)" stroke="#34d399" stroke-width="2" filter="url(#shadow)"/>
  <text x="800" y="185" font-size="16" font-weight="800" fill="#ffffff" text-anchor="middle">1. SYSTEM POWER ON / BOOT</text>
  <text x="800" y="200" font-size="10.5" font-weight="600" fill="#ecfdf5" text-anchor="middle">12V Battery Pack + 5.1V Buck Active</text>

  <!-- Down Arrow -->
  <path d="M 800 210 L 800 245" fill="none" stroke="#38bdf8" stroke-width="3" marker-end="url(#arrow)"/>

  <!-- ================= 2. INITIALIZATION / PREPARATION ================= -->
  <!-- Shape: Hexagon (Preparation) -->
  <polygon points="620,285 660,250 940,250 980,285 940,320 660,320" fill="url(#grad-prep)" stroke="#64748b" stroke-width="2" filter="url(#shadow)"/>
  <text x="800" y="278" font-size="14" font-weight="800" fill="#f8fafc" text-anchor="middle">2. HARDWARE &amp; DRIVER INITIALIZATION</text>
  <text x="800" y="296" font-size="11" fill="#94a3b8" text-anchor="middle">• SQLite WAL DB • MCP3008 SPI • Relays HIGH • Picamera2 • TFLite Model</text>

  <!-- Down Arrow -->
  <path d="M 800 320 L 800 355" fill="none" stroke="#38bdf8" stroke-width="3" marker-end="url(#arrow)"/>

  <!-- ================= 3. SELF_TEST DECISION ================= -->
  <!-- Shape: Diamond (Decision) -->
  <polygon points="800,360 990,430 800,500 610,430" fill="url(#grad-decision)" stroke="#f59e0b" stroke-width="2.5" filter="url(#shadow)"/>
  <text x="800" y="423" font-size="14" font-weight="800" fill="#ffffff" text-anchor="middle">3. SELF_TEST DIAGNOSTICS</text>
  <text x="800" y="442" font-size="11" font-weight="600" fill="#fef3c7" text-anchor="middle">All Sensors, Relays &amp; Drivers Verified?</text>

  <!-- FAIL Branch (Right -> Safe State) -->
  <path d="M 990 430 L 1150 430 L 1150 470" fill="none" stroke="#f87171" stroke-width="3" marker-end="url(#arrow-red)"/>
  <rect x="1030" y="412" width="70" height="20" rx="4" fill="#7f1d1d"/>
  <text x="1065" y="426" font-size="11" font-weight="800" fill="#fecaca" text-anchor="middle">FAIL (No)</text>

  <!-- Safe State Box -->
  <rect x="1050" y="475" width="200" height="70" rx="12" fill="url(#grad-stop)" stroke="#f87171" stroke-width="2" filter="url(#shadow)"/>
  <text x="1150" y="505" font-size="13" font-weight="800" fill="#ffffff" text-anchor="middle">ENTER SAFE_STATE</text>
  <text x="1150" y="525" font-size="10.5" fill="#fecaca" text-anchor="middle">• Ground PWM • Open Relays<br/>• Web Diagnostic Mode Only</text>

  <!-- PASS Branch (Down) -->
  <path d="M 800 500 L 800 545" fill="none" stroke="#34d399" stroke-width="3" marker-end="url(#arrow-green)"/>
  <rect x="810" y="510" width="80" height="20" rx="4" fill="#064e3b"/>
  <text x="850" y="524" font-size="11" font-weight="800" fill="#a7f3d0" text-anchor="middle">PASS (Yes)</text>

  <!-- ================= 4. FSM: IDLE & MONITORING ================= -->
  <!-- Shape: Rectangle (Process) -->
  <rect x="630" y="550" width="340" height="70" rx="10" fill="url(#grad-process)" stroke="#38bdf8" stroke-width="2" filter="url(#shadow)"/>
  <text x="800" y="578" font-size="14" font-weight="800" fill="#ffffff" text-anchor="middle">4. FSM TRANSITION: 'MONITORING'</text>
  <text x="800" y="598" font-size="11" fill="#e0f2fe" text-anchor="middle">Spawn Watchdog Thread | Start Control Loop (30s Tick)</text>

  <!-- Down Arrow -->
  <path d="M 800 620 L 800 655" fill="none" stroke="#38bdf8" stroke-width="3" marker-end="url(#arrow)"/>

  <!-- ================= 5. SENSOR DATA INGESTION ================= -->
  <!-- Shape: Parallelogram (Input / Output) -->
  <polygon points="620,730 660,660 980,660 940,730" fill="url(#grad-io)" stroke="#2dd4bf" stroke-width="2" filter="url(#shadow)"/>
  <text x="800" y="688" font-size="14" font-weight="800" fill="#ffffff" text-anchor="middle">5. INGEST SENSOR MATRIX</text>
  <text x="800" y="708" font-size="10.5" fill="#ccfbf1" text-anchor="middle">Sample Soil Moisture (MCP3008 ADC) | DHT11/22 | NEO-7M GPS | HMC5883L</text>

  <!-- Down Arrow -->
  <path d="M 800 730 L 800 765" fill="none" stroke="#38bdf8" stroke-width="3" marker-end="url(#arrow)"/>

  <!-- ================= 6. OBSTACLE AVOIDANCE DECISION ================= -->
  <!-- Shape: Diamond (Decision) -->
  <polygon points="800,770 990,840 800,910 610,840" fill="url(#grad-decision)" stroke="#f59e0b" stroke-width="2.5" filter="url(#shadow)"/>
  <text x="800" y="833" font-size="14" font-weight="800" fill="#ffffff" text-anchor="middle">6. FRONT OBSTACLE DETECTED?</text>
  <text x="800" y="852" font-size="11" font-weight="600" fill="#fef3c7" text-anchor="middle">Fresh GPS fix and configured waypoint?</text>

  <!-- YES (Obstacle -> Avoidance Subroutine) -->
  <path d="M 990 840 L 1180 840 L 1180 880" fill="none" stroke="#fbbf24" stroke-width="3" marker-end="url(#arrow-amber)"/>
  <rect x="1030" y="822" width="60" height="20" rx="4" fill="#78350f"/>
  <text x="1060" y="836" font-size="11" font-weight="800" fill="#fde68a" text-anchor="middle">YES</text>

  <!-- Avoidance Process Box -->
  <rect x="1050" y="885" width="260" height="85" rx="10" fill="url(#grad-process)" stroke="#38bdf8" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="1180" y="910" font-size="13" font-weight="800" fill="#ffffff" text-anchor="middle">REACTIVE OBSTACLE AVOIDANCE</text>
  <text x="1180" y="930" font-size="10.5" fill="#e0f2fe" text-anchor="middle">1. Halt 4WD Drive Immediately</text>
  <text x="1180" y="945" font-size="10.5" fill="#e0f2fe" text-anchor="middle">2. Read HMC5883L heading versus waypoint bearing</text>
  <text x="1180" y="960" font-size="10.5" fill="#34d399" text-anchor="middle">3. Pivot In-Place &amp; Resume Waypoint</text>

  <!-- Reconnect from Avoidance back to Main Spine -->
  <path d="M 1180 970 L 1180 1020 L 800 1020" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6,4"/>

  <!-- NO (Clear -> Continue Down) -->
  <path d="M 800 910 L 800 1040" fill="none" stroke="#34d399" stroke-width="3" marker-end="url(#arrow-green)"/>
  <rect x="810" y="945" width="60" height="20" rx="4" fill="#064e3b"/>
  <text x="840" y="959" font-size="11" font-weight="800" fill="#a7f3d0" text-anchor="middle">NO</text>


  <!-- ================= 7. SOIL MOISTURE HYSTERESIS DECISION ================= -->
  <!-- Shape: Diamond (Decision) -->
  <polygon points="800,1050 990,1120 800,1190 610,1120" fill="url(#grad-decision)" stroke="#f59e0b" stroke-width="2.5" filter="url(#shadow)"/>
  <text x="800" y="1112" font-size="14" font-weight="800" fill="#ffffff" text-anchor="middle">7. SOIL MOISTURE &lt; 35.0%?</text>
  <text x="800" y="1132" font-size="11" font-weight="600" fill="#fef3c7" text-anchor="middle">AND Pump Cooldown Expired (120s)?</text>

  <!-- YES (Irrigate) -->
  <path d="M 990 1120 L 1180 1120 L 1180 1160" fill="none" stroke="#34d399" stroke-width="3" marker-end="url(#arrow-green)"/>
  <rect x="1030" y="1102" width="60" height="20" rx="4" fill="#064e3b"/>
  <text x="1060" y="1116" font-size="11" font-weight="800" fill="#a7f3d0" text-anchor="middle">YES</text>

  <!-- Irrigation Subroutine Box -->
  <rect x="1050" y="1165" width="260" height="100" rx="10" fill="url(#grad-io)" stroke="#34d399" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="1180" y="1190" font-size="13" font-weight="800" fill="#ffffff" text-anchor="middle">EXECUTE IRRIGATION CYCLE</text>
  <text x="1180" y="1210" font-size="10.5" fill="#ccfbf1" text-anchor="middle">1. Halt Drive Motors (Probe Drag Safety)</text>
  <text x="1180" y="1225" font-size="10.5" fill="#ccfbf1" text-anchor="middle">2. Energize Pump Relay CH1 (GPIO17)</text>
  <text x="1180" y="1240" font-size="10.5" fill="#fcd34d" text-anchor="middle">3. Stop when Moisture &gt; 65% OR 60s timeout</text>
  <text x="1180" y="1255" font-size="10.5" fill="#ccfbf1" text-anchor="middle">4. Log event to SQLite &amp; start 120s cooldown</text>

  <!-- Reconnect from Irrigation back to Main Spine -->
  <path d="M 1180 1265 L 1180 1310 L 800 1310" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6,4"/>

  <!-- NO (Moisture OK -> Continue Down) -->
  <path d="M 800 1190 L 800 1330" fill="none" stroke="#38bdf8" stroke-width="3" marker-end="url(#arrow)"/>
  <rect x="810" y="1230" width="60" height="20" rx="4" fill="#1e293b"/>
  <text x="840" y="1244" font-size="11" font-weight="800" fill="#cbd5e1" text-anchor="middle">NO</text>


  <!-- ================= 8. GRASS CUTTER SCHEDULE DECISION ================= -->
  <!-- Shape: Diamond (Decision) -->
  <polygon points="800,1340 990,1410 800,1480 610,1410" fill="url(#grad-decision)" stroke="#f59e0b" stroke-width="2.5" filter="url(#shadow)"/>
  <text x="800" y="1402" font-size="14" font-weight="800" fill="#ffffff" text-anchor="middle">8. CUTTER INTERVAL (3600s) REACHED?</text>
  <text x="800" y="1422" font-size="11" font-weight="600" fill="#fef3c7" text-anchor="middle">OR Manual Trimming Requested from Web UI?</text>

  <!-- YES (Trim Grass) -->
  <path d="M 990 1410 L 1180 1410 L 1180 1450" fill="none" stroke="#fbbf24" stroke-width="3" marker-end="url(#arrow-amber)"/>
  <rect x="1030" y="1392" width="60" height="20" rx="4" fill="#78350f"/>
  <text x="1060" y="1406" font-size="11" font-weight="800" fill="#fde68a" text-anchor="middle">YES</text>

  <!-- Cutter Process Box -->
  <rect x="1050" y="1455" width="260" height="90" rx="10" fill="url(#grad-process)" stroke="#f59e0b" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="1180" y="1480" font-size="13" font-weight="800" fill="#ffffff" text-anchor="middle">EXECUTE GRASS TRIMMING</text>
  <text x="1180" y="1500" font-size="10.5" fill="#e0f2fe" text-anchor="middle">1. Halt Drive Motors (Interlock Safety)</text>
  <text x="1180" y="1515" font-size="10.5" fill="#fcd34d" text-anchor="middle">2. Energize Cutter Relay CH2 (GPIO27)</text>
  <text x="1180" y="1530" font-size="10.5" fill="#e0f2fe" text-anchor="middle">3. Run blade for 30s &amp; de-energize relay</text>

  <!-- Reconnect from Cutter back to Main Spine -->
  <path d="M 1180 1545 L 1180 1600 L 800 1600" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6,4"/>

  <!-- NO (Continue Down) -->
  <path d="M 800 1480 L 800 1620" fill="none" stroke="#38bdf8" stroke-width="3" marker-end="url(#arrow)"/>
  <rect x="810" y="1520" width="60" height="20" rx="4" fill="#1e293b"/>
  <text x="840" y="1534" font-size="11" font-weight="800" fill="#cbd5e1" text-anchor="middle">NO</text>


  <!-- ================= 9. AI DISEASE DETECTION & QUALITY GATE ================= -->
  <!-- Shape: Diamond (Decision) -->
  <polygon points="800,1630 990,1700 800,1770 610,1700" fill="url(#grad-decision)" stroke="#f59e0b" stroke-width="2.5" filter="url(#shadow)"/>
  <text x="800" y="1692" font-size="14" font-weight="800" fill="#ffffff" text-anchor="middle">9. TRIGGER OPTICAL LEAF SCAN?</text>
  <text x="800" y="1712" font-size="11" font-weight="600" fill="#fef3c7" text-anchor="middle">Periodic Auto-Interval (1800s) OR Web Scan Button?</text>

  <!-- YES (Run Vision AI) -->
  <path d="M 990 1700 L 1180 1700 L 1180 1740" fill="none" stroke="#38bdf8" stroke-width="3" marker-end="url(#arrow)"/>
  <rect x="1030" y="1682" width="60" height="20" rx="4" fill="#0369a1"/>
  <text x="1060" y="1696" font-size="11" font-weight="800" fill="#bae6fd" text-anchor="middle">YES</text>

  <!-- Vision AI Subroutine Box -->
  <rect x="1050" y="1745" width="280" height="120" rx="10" fill="url(#grad-prep)" stroke="#38bdf8" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="1190" y="1770" font-size="13" font-weight="800" fill="#60a5fa" text-anchor="middle">EDGE AI LEAF INFERENCE PIPELINE</text>
  <text x="1190" y="1790" font-size="10.5" fill="#cbd5e1" text-anchor="middle">1. Picamera2 Frame Capture (224×224)</text>
  <text x="1190" y="1805" font-size="10.5" fill="#34d399" text-anchor="middle">2. Gate: Laplacian Var &gt; 50 &amp; Lum in 35-225</text>
  <text x="1190" y="1820" font-size="10.5" fill="#cbd5e1" text-anchor="middle">3. TFLite MobileNetV2 Softmax Inference</text>
  <text x="1190" y="1835" font-size="10.5" fill="#fcd34d" text-anchor="middle">4. If Disease &amp; Conf ≥ 70%: Alarm Buzzer/LED</text>
  <text x="1190" y="1850" font-size="10.5" fill="#cbd5e1" text-anchor="middle">5. Query disease_db.py &amp; Log to SQLite</text>

  <!-- Reconnect from Vision AI back to Main Spine -->
  <path d="M 1190 1865 L 1190 1910 L 800 1910" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6,4"/>

  <!-- NO (Continue Down) -->
  <path d="M 800 1770 L 800 1930" fill="none" stroke="#38bdf8" stroke-width="3" marker-end="url(#arrow)"/>
  <rect x="810" y="1810" width="60" height="20" rx="4" fill="#1e293b"/>
  <text x="840" y="1824" font-size="11" font-weight="800" fill="#cbd5e1" text-anchor="middle">NO</text>


  <!-- ================= 10. WATER LEVEL & AUTONOMOUS DOCKING ================= -->
  <!-- Shape: Diamond (Decision) -->
  <polygon points="800,1940 990,2010 800,2080 610,2010" fill="url(#grad-decision)" stroke="#f59e0b" stroke-width="2.5" filter="url(#shadow)"/>
  <text x="800" y="2002" font-size="14" font-weight="800" fill="#ffffff" text-anchor="middle">10. WATER TANK LEVEL LOW / EMPTY?</text>
  <text x="800" y="2022" font-size="11" font-weight="600" fill="#fef3c7" text-anchor="middle">Float Switch / Level Sensor Triggered?</text>

  <!-- YES (Dock & Refill) -->
  <path d="M 990 2010 L 1180 2010 L 1180 2045" fill="none" stroke="#6366f1" stroke-width="3" marker-end="url(#arrow)"/>
  <rect x="1030" y="1992" width="60" height="20" rx="4" fill="#312e81"/>
  <text x="1060" y="2006" font-size="11" font-weight="800" fill="#c7d2fe" text-anchor="middle">YES</text>

  <!-- Docking Process Box -->
  <rect x="1050" y="2050" width="280" height="110" rx="10" fill="url(#grad-dock)" stroke="#818cf8" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="1190" y="2075" font-size="13" font-weight="800" fill="#ffffff" text-anchor="middle">GPS WAYPOINT NAVIGATION</text>
  <text x="1190" y="2095" font-size="10.5" fill="#e0e7ff" text-anchor="middle">1. Store (X, Y, Heading) Mission Checkpoint</text>
  <text x="1190" y="2110" font-size="10.5" fill="#e0e7ff" text-anchor="middle">2. Navigate to Water Station via Waypoints</text>
  <text x="1190" y="2125" font-size="10.5" fill="#a7f3d0" text-anchor="middle">3. Drive in a short burst, stop and re-check sensors</text>
  <text x="1190" y="2140" font-size="10.5" fill="#e0e7ff" text-anchor="middle">4. Solenoid Refill → Return to Checkpoint</text>

  <!-- Reconnect from Docking back to Loop -->
  <path d="M 1190 2160 L 1190 2200 L 800 2200" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6,4"/>

  <!-- NO (Continue Down) -->
  <path d="M 800 2080 L 800 2220" fill="none" stroke="#34d399" stroke-width="3" marker-end="url(#arrow-green)"/>
  <rect x="810" y="2100" width="60" height="20" rx="4" fill="#064e3b"/>
  <text x="840" y="2114" font-size="11" font-weight="800" fill="#a7f3d0" text-anchor="middle">NO</text>


  <!-- ================= 11. TELEMETRY CACHE & HEARTBEAT ================= -->
  <!-- Shape: Rectangle (Process) -->
  <rect x="620" y="2230" width="360" height="70" rx="10" fill="url(#grad-process)" stroke="#38bdf8" stroke-width="2" filter="url(#shadow)"/>
  <text x="800" y="2258" font-size="14" font-weight="800" fill="#ffffff" text-anchor="middle">11. UPDATE TELEMETRY &amp; RESET WATCHDOG</text>
  <text x="800" y="2278" font-size="11" fill="#e0f2fe" text-anchor="middle">Write to _telemetry_cache | Ping Watchdog | Sleep POLL_INTERVAL (30s)</text>


  <!-- ================= LOOP RECYCLE BACK TO MONITORING ================= -->
  <!-- Long Spine Loop Line from Step 11 back up to Step 5 -->
  <path d="M 620 2265 L 420 2265 L 420 695 L 635 695" fill="none" stroke="#34d399" stroke-width="3.5" stroke-dasharray="8,5" marker-end="url(#arrow-green)"/>
  <rect x="360" y="1450" width="120" height="30" rx="6" fill="#064e3b" stroke="#34d399" stroke-width="1.5"/>
  <text x="420" y="1470" font-size="11" font-weight="800" fill="#a7f3d0" text-anchor="middle">NEXT PATROL TICK</text>

</svg>"""

    with open("diagrams/project_flowchart.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("Successfully generated diagrams/project_flowchart.svg")

if __name__ == "__main__":
    generate_flowchart()
