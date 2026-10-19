/*
 * ============================================================================
 * AgroNex-Pi: Arduino Uno Multi-Subsystem Slave Controller
 * ============================================================================
 * Hardware Targets:
 *   - Arduino Uno R3 (ATmega328P)
 * 
 * Subsystems Handled:
 *   1. 4WD Motors (Dual BTS7960 43A High-Current H-Bridges)
 *      - BTS #1 (Left 2 Motors in parallel): Pins 5, 6 (Timer 0 PWM)
 *      - BTS #2 (Right 2 Motors in parallel): Pins 3, 11 (Timer 2 PWM)
 *   2. Servos (Soil Probe Actuator + Ultrasonic Radar Scanners)
 *      - Probe Servo: Pin 9
 *      - Front Ultrasonic Pan Servo: Pin 10
 *      - Rear Ultrasonic Pan Servo: Pin 12
 *   3. Dual HC-SR04 Ultrasonic Distance Sensors
 *      - Front: Trig Pin 2, Echo Pin 8
 *      - Rear:  Trig Pin A0, Echo Pin A1
 *   4. High-Speed USB Serial Interface with Raspberry Pi (115200 baud)
 *      - Also supports interactive single-letter testing via Serial Monitor!
 * 
 * NOTE ON ARDUINO PWM TIMERS:
 *   Arduino's Servo library claims Timer 1 (disabling PWM on pins 9 & 10).
 *   Therefore, motor PWM is routed through Timer 0 (pins 5, 6) and 
 *   Timer 2 (pins 3, 11). Servos run smoothly on pins 9, 10, and 12!
 * ============================================================================
 */

#include <Servo.h>

// ============================================================================
// 1. PIN DEFINITIONS
// ============================================================================

// --- BTS7960 Motor Driver #1 (Left 2 Wheels) ---
const int PIN_L_EN_REN   = 4;   // Left Enable (Bridge R_EN and L_EN to Pin 4)
const int PIN_L_RPWM     = 5;   // Left Forward (Timer 0 PWM)
const int PIN_L_LPWM     = 6;   // Left Reverse (Timer 0 PWM)

// --- BTS7960 Motor Driver #2 (Right 2 Wheels) ---
const int PIN_R_EN_REN   = 7;   // Right Enable (Bridge R_EN and L_EN to Pin 7)
const int PIN_R_RPWM     = 3;   // Right Forward (Timer 2 PWM)
const int PIN_R_LPWM     = 11;  // Right Reverse (Timer 2 PWM)

// --- Servos ---
const int PIN_SERVO_PROBE = 9;  // 3D-printed Soil Moisture Probe Actuator Servo
const int PIN_SERVO_FRONT = 10; // Front Ultrasonic Pan Servo
const int PIN_SERVO_REAR  = 12; // Rear Ultrasonic Pan Servo

// --- Ultrasonic Sensors (HC-SR04) ---
const int PIN_US_FRONT_TRIG = 2;
const int PIN_US_FRONT_ECHO = 8;
const int PIN_US_REAR_TRIG  = A0; // Analog pin A0 used as digital Output
const int PIN_US_REAR_ECHO  = A1; // Analog pin A1 used as digital Input

// ============================================================================
// 2. CONSTANTS & OBJECTS
// ============================================================================

Servo servoProbe;
Servo servoFrontUS;
Servo servoRearUS;

// Soil probe actuator angles (calibrated for smooth travel)
const int PROBE_RETRACTED_ANGLE = 175; // Upward stowed position
const int PROBE_DEPLOYED_ANGLE  = 15;  // Downward inserted into soil

int currentProbeAngle = PROBE_RETRACTED_ANGLE;

// Forward function declarations
void stopMotors();
void driveMotors(int leftDuty, int rightDuty);
void deployProbe();
void retractProbe();
long readUltrasonicCM(int trigPin, int echoPin);
void handleCommand(const String& cmd);

// ============================================================================
// 3. SETUP
// ============================================================================

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(50);

  // Configure Motor Pins
  pinMode(PIN_L_EN_REN, OUTPUT);
  pinMode(PIN_L_RPWM, OUTPUT);
  pinMode(PIN_L_LPWM, OUTPUT);

  pinMode(PIN_R_EN_REN, OUTPUT);
  pinMode(PIN_R_RPWM, OUTPUT);
  pinMode(PIN_R_LPWM, OUTPUT);

  // Enable Both Motor Bridges
  digitalWrite(PIN_L_EN_REN, HIGH);
  digitalWrite(PIN_R_EN_REN, HIGH);
  stopMotors();

  // Attach and Home Servos
  servoProbe.attach(PIN_SERVO_PROBE);
  servoFrontUS.attach(PIN_SERVO_FRONT);
  servoRearUS.attach(PIN_SERVO_REAR);

  servoProbe.write(PROBE_RETRACTED_ANGLE); // Safely stowed upward
  servoFrontUS.write(90);                 // Facing straight ahead
  servoRearUS.write(90);                  // Facing straight behind

  // Configure Ultrasonic Pins
  pinMode(PIN_US_FRONT_TRIG, OUTPUT);
  pinMode(PIN_US_FRONT_ECHO, INPUT);
  pinMode(PIN_US_REAR_TRIG, OUTPUT);
  pinMode(PIN_US_REAR_ECHO, INPUT);

  digitalWrite(PIN_US_FRONT_TRIG, LOW);
  digitalWrite(PIN_US_REAR_TRIG, LOW);

  // Announce ready to Pi and Serial Monitor
  Serial.println(F("AGRONEX_ARDUINO_READY"));
}

// ============================================================================
// 4. MAIN LOOP
// ============================================================================

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.length() > 0) {
      handleCommand(cmd);
    }
  }
}

// ============================================================================
// 5. MOTOR CONTROL FUNCTIONS
// ============================================================================

/**
 * Drives Left and Right wheel groups.
 * @param leftDuty:  -255 (full reverse) to +255 (full forward)
 * @param rightDuty: -255 (full reverse) to +255 (full forward)
 */
void driveMotors(int leftDuty, int rightDuty) {
  // Left Motors (Front-Left & Rear-Left in parallel)
  if (leftDuty > 0) {
    analogWrite(PIN_L_RPWM, constrain(leftDuty, 0, 255));
    analogWrite(PIN_L_LPWM, 0);
  } else if (leftDuty < 0) {
    analogWrite(PIN_L_RPWM, 0);
    analogWrite(PIN_L_LPWM, constrain(-leftDuty, 0, 255));
  } else {
    analogWrite(PIN_L_RPWM, 0);
    analogWrite(PIN_L_LPWM, 0);
  }

  // Right Motors (Front-Right & Rear-Right in parallel)
  if (rightDuty > 0) {
    analogWrite(PIN_R_RPWM, constrain(rightDuty, 0, 255));
    analogWrite(PIN_R_LPWM, 0);
  } else if (rightDuty < 0) {
    analogWrite(PIN_R_RPWM, 0);
    analogWrite(PIN_R_LPWM, constrain(-rightDuty, 0, 255));
  } else {
    analogWrite(PIN_R_RPWM, 0);
    analogWrite(PIN_R_LPWM, 0);
  }
}

void stopMotors() {
  analogWrite(PIN_L_RPWM, 0);
  analogWrite(PIN_L_LPWM, 0);
  analogWrite(PIN_R_RPWM, 0);
  analogWrite(PIN_R_LPWM, 0);
}

// ============================================================================
// 6. SERVO ACTUATOR FUNCTIONS
// ============================================================================

// Smoothly lowers the soil moisture probe into the ground
void deployProbe() {
  stopMotors(); // Interlock: NEVER move chassis while probe is inserted!
  for (int a = currentProbeAngle; a >= PROBE_DEPLOYED_ANGLE; a -= 4) {
    servoProbe.write(a);
    delay(20);
  }
  currentProbeAngle = PROBE_DEPLOYED_ANGLE;
  servoProbe.write(PROBE_DEPLOYED_ANGLE);
}

// Smoothly retracts the soil moisture probe upward
void retractProbe() {
  for (int a = currentProbeAngle; a <= PROBE_RETRACTED_ANGLE; a += 4) {
    servoProbe.write(a);
    delay(20);
  }
  currentProbeAngle = PROBE_RETRACTED_ANGLE;
  servoProbe.write(PROBE_RETRACTED_ANGLE);
}

// ============================================================================
// 7. ULTRASONIC DISTANCE SENSOR (HC-SR04)
// ============================================================================

long readUltrasonicCM(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // 25ms timeout (~4.2m distance)
  long duration = pulseIn(echoPin, HIGH, 25000);
  if (duration <= 0) return 999; // 999cm = clear / no obstacle detected
  return (long)(duration * 0.034 / 2);
}

// ============================================================================
// 8. COMMAND PARSER (Supports Raspberry Pi Python API & Serial Monitor)
// ============================================================================

void handleCommand(const String& cmd) {
  // --- 1. Python Supervisor Driving Protocol: "M,leftSpeed,rightSpeed" ---
  if (cmd.startsWith("M,")) {
    if (currentProbeAngle < PROBE_RETRACTED_ANGLE - 20) {
      Serial.println(F("ERR_PROBE_DEPLOYED_CANNOT_DRIVE"));
      return;
    }
    int firstComma = cmd.indexOf(',');
    int secondComma = cmd.indexOf(',', firstComma + 1);
    if (secondComma > 0) {
      int left = cmd.substring(firstComma + 1, secondComma).toInt();
      int right = cmd.substring(secondComma + 1).toInt();
      driveMotors(left, right);
      Serial.println(F("OK_M"));
    }
  }

  // --- 2. Stop Motors: "STOP" or "S" ---
  else if (cmd == "STOP" || cmd == "S") {
    stopMotors();
    Serial.println(F("OK_STOP"));
  }

  // --- 3. Soil Probe Deploy: "PROBE_DOWN" or "P1" ---
  else if (cmd == "PROBE_DOWN" || cmd == "P1") {
    deployProbe();
    Serial.println(F("OK_PROBE_DOWN"));
  }

  // --- 4. Soil Probe Retract: "PROBE_UP" or "P0" ---
  else if (cmd == "PROBE_UP" || cmd == "P0") {
    retractProbe();
    Serial.println(F("OK_PROBE_UP"));
  }

  // --- 5. Front Ultrasonic Radar: "SCAN_F" or "SCAN_F,angle" ---
  else if (cmd.startsWith("SCAN_F") || cmd == "UF") {
    int angle = 90;
    int comma = cmd.indexOf(',');
    if (comma > 0) {
      angle = constrain(cmd.substring(comma + 1).toInt(), 15, 165);
      servoFrontUS.write(angle);
      delay(120);
    }
    long dist = readUltrasonicCM(PIN_US_FRONT_TRIG, PIN_US_FRONT_ECHO);
    Serial.print(F("DIST_F:"));
    Serial.println(dist);
  }

  // --- 6. Rear Ultrasonic Radar: "SCAN_R" or "SCAN_R,angle" ---
  else if (cmd.startsWith("SCAN_R") || cmd == "UR") {
    int angle = 90;
    int comma = cmd.indexOf(',');
    if (comma > 0) {
      angle = constrain(cmd.substring(comma + 1).toInt(), 15, 165);
      servoRearUS.write(angle);
      delay(120);
    }
    long dist = readUltrasonicCM(PIN_US_REAR_TRIG, PIN_US_REAR_ECHO);
    Serial.print(F("DIST_R:"));
    Serial.println(dist);
  }

  // --- 7. Quick Single-Key Manual Testing (Serial Monitor) ---
  else if (cmd == "F" || cmd == "FORWARD") {
    driveMotors(180, 180);
    Serial.println(F("DRIVING_FORWARD"));
  }
  else if (cmd == "B" || cmd == "BACKWARD") {
    driveMotors(-180, -180);
    Serial.println(F("DRIVING_BACKWARD"));
  }
  else if (cmd == "L" || cmd == "LEFT") {
    driveMotors(-160, 160);
    Serial.println(F("TURNING_LEFT"));
  }
  else if (cmd == "R" || cmd == "RIGHT") {
    driveMotors(160, -160);
    Serial.println(F("TURNING_RIGHT"));
  }

  // --- 8. Direct Servo Angle Controls ---
  else if (cmd.startsWith("ACTUATOR,")) {
    int angle = constrain(cmd.substring(9).toInt(), 0, 180);
    servoProbe.write(angle);
    currentProbeAngle = angle;
    Serial.print(F("OK_ACTUATOR:"));
    Serial.println(angle);
  }
  else if (cmd.startsWith("SERVO_F,")) {
    int angle = constrain(cmd.substring(8).toInt(), 0, 180);
    servoFrontUS.write(angle);
    Serial.print(F("OK_SERVO_F:"));
    Serial.println(angle);
  }
  else if (cmd.startsWith("SERVO_R,")) {
    int angle = constrain(cmd.substring(8).toInt(), 0, 180);
    servoRearUS.write(angle);
    Serial.print(F("OK_SERVO_R:"));
    Serial.println(angle);
  }

  // --- 9. Full Diagnostic Status: "STATUS" ---
  else if (cmd == "STATUS") {
    long df = readUltrasonicCM(PIN_US_FRONT_TRIG, PIN_US_FRONT_ECHO);
    long dr = readUltrasonicCM(PIN_US_REAR_TRIG, PIN_US_REAR_ECHO);
    Serial.print(F("STATUS:PROBE="));
    Serial.print(currentProbeAngle);
    Serial.print(F(",DIST_F="));
    Serial.print(df);
    Serial.print(F(",DIST_R="));
    Serial.println(dr);
  }

  // --- 10. Health Check: "PING" ---
  else if (cmd == "PING") {
    Serial.println(F("PONG"));
  }
}
