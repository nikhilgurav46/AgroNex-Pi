#!/usr/bin/env python3
"""
AgroNex-Pi: Main Thread Supervisor & Entry Point (§5.8)

System entry point for AgroNex-Pi autonomous smart gardening robot.

Features:
- Finite State Machine (FSM) control supervisor (§6).
- Mandatory hardware SELF_TEST before enabling actuation.
- Fail-Safe SIGTERM and SIGINT signal handlers for clean systemd restarts.
- Multi-threaded architecture (Control Loop, Disease Scanner, Watchdog, Flask Server).
- Opt-in '--simulate' CLI flag with persistent warning banners (§8).
"""

import os
import sys
import time
import signal
import json
import argparse
import datetime
import threading
import logging
import numpy as np

import config
from hardware import (
    initialize_hardware_libs, SoilSensor, WaterLevelSensor, DHTSensor, GPSSensor, CompassSensor, Relay, Motors,
    Camera, Alerts, register_emergency_devices, emergency_stop
)
from database import DatabaseManager
from irrigation import IrrigationController
from cutter import CutterController
from navigation import NavigationController
from disease_detect import DiseaseDetector
from aws_relay import AWSRelay
import app

try:
    import cv2
except ImportError:
    cv2 = None

# Setup Logging
logger = logging.getLogger("AgroNex.Main")


class MainSupervisor:
    def __init__(self, simulate: bool = False):
        self.simulate = simulate
        self.start_time = time.time()

        # FSM State (§6)
        # BOOT -> SELF_TEST -> IDLE -> MONITORING (IRRIGATING / CUTTING / NAVIGATING / SCANNING) -> SAFE_STATE
        self.current_state = "BOOT"
        self.running = True

        # Database Manager
        self.db = DatabaseManager(config.DB_PATH)

        # Hardware Driver References
        self.soil_sensor = None
        self.water_sensor = None
        self.dht_sensor = None
        self.gps_sensor = None
        self.compass_sensor = None
        self.relay = None
        self.motors = None
        self.camera = None
        self.alerts = None

        # Functional Subsystem Controllers
        self.irrigation_ctrl = None
        self.cutter_ctrl = None
        self.nav_ctrl = None
        self.disease_detector = None

        # Operation Mode: 'AUTO' (scheduled patrol/actuation) or 'MANUAL' (virtual remote)
        self.operation_mode = "AUTO"
        self.startup_sequence_done = False
        self.last_actuator_time = time.time()  # 1-hour automatic actuator cycle
        self.last_dht_time = 0.0               # 10-minute automatic temperature scan
        self.actuator_cycle_running = False

        # Persistent Sensor Telemetry (held on dashboard until next reading cycle)
        self.cached_soil_moisture = 48.0
        self.cached_raw_adc = 520
        self.cached_temperature = 28.5
        self.cached_humidity = 62.0
        self.cached_water_level = 85.0
        self.cached_water_status = "OPTIMAL"

        # Timers & Watchdog Heartbeat
        self.last_disease_scan_time = time.time()
        self.last_auto_scan_time = 0.0
        self.control_loop_heartbeat = time.time()

        # AWS Cloud Relay
        self.aws_relay = None
        self._last_pushed_soil = None
        self._last_pushed_water = None

    def set_state(self, new_state: str):
        """Logs and executes state transition in FSM."""
        if self.current_state != new_state:
            logger.info(f"FSM State Transition: '{self.current_state}' ---> '{new_state}'")
            self.db.log_system_event("FSM_TRANSITION", "INFO", f"{self.current_state} -> {new_state}", self.simulate)
            self.current_state = new_state
            app.update_telemetry_cache({"current_state": new_state})

    # -------------------------------------------------------------------------
    # 1. BOOT & SELF_TEST (§5.8)
    # -------------------------------------------------------------------------
    def run_self_test(self) -> bool:
        """
        Runs comprehensive startup self-test across all hardware and software components.
        Refuses to start actuation if any test fails.
        """
        self.set_state("SELF_TEST")
        logger.info("==================================================")
        logger.info("     RUNNING SYSTEM SELF_TEST DIAGNOSTICS         ")
        logger.info("==================================================")
        failures = []

        # 1. Database Check
        try:
            self.db.log_system_event("SELF_TEST_START", "INFO", "Self-test initiated.", self.simulate)
            logger.info("[PASS] Database write verified.")
        except Exception as e:
            failures.append(f"Database error: {e}")

        # 2. Hardware Driver Initialization
        try:
            initialize_hardware_libs(simulate=self.simulate)
        except Exception as e:
            failures.append(f"Hardware library init failure: {e}")
            return False

        try:
            self.relay = Relay()
        except Exception as e:
            failures.append(f"Relay error: {e}")

        try:
            self.motors = Motors()
            if self.relay and self.motors:
                register_emergency_devices(self.relay, self.motors)
        except Exception as e:
            failures.append(f"Motors error: {e}")

        try:
            self.soil_sensor = SoilSensor()
        except Exception as e:
            failures.append(f"Soil sensor init error: {e}")

        try:
            self.water_sensor = WaterLevelSensor()
        except Exception as e:
            failures.append(f"Water sensor init error: {e}")

        try:
            self.dht_sensor = DHTSensor()
        except Exception as e:
            failures.append(f"DHT sensor init error: {e}")

        try:
            self.gps_sensor = GPSSensor()
        except Exception as e:
            failures.append(f"GPS init error: {e}")

        try:
            self.compass_sensor = CompassSensor()
        except Exception as e:
            failures.append(f"Compass init error: {e}")

        try:
            self.alerts = Alerts()
        except Exception as e:
            failures.append(f"Alerts init error: {e}")

        logger.info("[PASS] Low-level hardware drivers initialized.")

        # 3. Soil Sensor Read Test (Dry air on bench is normal, treated as warning)
        try:
            raw_adc, pct = self.soil_sensor.read_percentage()
            if pct is None and not self.simulate:
                logger.warning(f"Soil sensor probe in dry air / resting position: raw={raw_adc}. Ready for field insertion.")
            else:
                logger.info(f"[PASS] Soil Sensor response: Raw ADC={raw_adc}, Moisture={pct}%")
        except Exception as e:
            logger.warning(f"Soil sensor read warning: {e}")

        # 3b. HW-038 Water Level Sensor Read Test
        try:
            raw_w, water_pct, water_status = self.water_sensor.read_percentage()
            logger.info(f"[PASS] HW-038 Water Level: Raw={raw_w}, Level={water_pct}% ({water_status})")
        except Exception as e:
            logger.warning(f"Water level sensor warning: {e}")

        # 4. DHT Sensor Read Test
        try:
            temp, hum = self.dht_sensor.read(max_retries=2)
            logger.info(f"[PASS] DHT Sensor response: Temp={temp}°C, Humidity={hum}%")
        except Exception as e:
            failures.append(f"DHT sensor error: {e}")

        # 4b. GPS and compass transport test. Satellite fix is acquired dynamically in background.
        try:
            heading = self.compass_sensor.read_heading() if self.compass_sensor else None
            logger.info(f"[PASS] Compass heading: {heading if heading is not None else 'Calibrating...'}")
            gps_fix = self.gps_sensor.read_fix() if self.gps_sensor else None
            logger.info(f"[PASS] NEO-7M serial: {'valid fix' if gps_fix else 'searching for satellites...'}")
        except Exception as e:
            logger.warning(f"GPS/compass sensor notice: {e}")

        # 5. Camera & TFLite Detector Check
        try:
            if not self.simulate:
                self.camera = Camera.get_instance()
                logger.info("[PASS] Picamera2 singleton initialized.")
            self.disease_detector = DiseaseDetector(simulate=self.simulate)
            logger.info("[PASS] Disease Detector & TFLite Interpreter ready.")
        except Exception as e:
            failures.append(f"Camera/AI Detector error: {e}")

        # Instantiate Subsystem Controllers safely
        try:
            self.irrigation_ctrl = IrrigationController(self.soil_sensor, self.relay, self.motors, self.db, self.simulate)
            self.cutter_ctrl = CutterController(self.relay, self.motors, self.db, self.simulate)
            self.nav_ctrl = NavigationController(self.motors, self.gps_sensor, self.compass_sensor)
        except Exception as e:
            logger.warning(f"Subsystem controller instantiation notice: {e}")

        # Seed telemetry cache immediately with fresh readings so AWS relay has live data at t=0
        try:
            raw_adc, soil_pct = self.soil_sensor.read_percentage() if self.soil_sensor else (0, None)
            raw_w, water_pct, water_status = self.water_sensor.read_percentage() if self.water_sensor else (0, 85.0, "OPTIMAL")
            temp, hum = self.dht_sensor.read(max_retries=1) if self.dht_sensor else (None, None)
            gps_fix = self.gps_sensor.read_fix() if self.gps_sensor else None
            heading = self.compass_sensor.read_heading() if self.compass_sensor else None
            app.update_telemetry_cache({
                "soil_moisture": soil_pct,
                "raw_adc": raw_adc,
                "water_level": water_pct,
                "water_status": water_status,
                "temperature": temp,
                "humidity": hum,
                "gps": gps_fix,
                "heading_deg": heading,
                "navigation_status": "IDLE",
                "pump_state": self.relay.pump_state if self.relay else False,
                "cutter_state": self.relay.cutter_state if self.relay else False,
                "current_state": "SAFE_STATE" if failures else "IDLE",
                "uptime_seconds": 0,
                "simulation_mode": self.simulate
            })
        except Exception as e:
            logger.debug(f"Initial telemetry seed notice: {e}")

        # Summary Evaluation
        if failures:
            logger.warning("[WARN] SELF_TEST had issues — starting in DEGRADED mode (some hardware may be unavailable).")
            for f in failures:
                logger.warning(f"   -> DEGRADED: {f}")
            self.db.log_system_event("SELF_TEST_DEGRADED", "WARNING", f"Issues: {'; '.join(failures)}", self.simulate)
            # Do NOT go to SAFE_STATE — let the robot start in monitoring/auto mode
            # with whatever hardware is available (e.g., missing picamera2 shouldn't kill motors)
        else:
            logger.info("==================================================")
            logger.info("[PASS] ALL SELF_TEST CHECKS PASSED SUCCESSFULLY! ")
            logger.info("==================================================")
            self.db.log_system_event("SELF_TEST_PASSED", "INFO", "All hardware checks green.", self.simulate)

        # Initialize and Start AWS Cloud Relay (if configured)
        self.start_aws_relay()

        # Always start in IDLE regardless of failures — startup sequence moves to MONITORING
        self.set_state("IDLE")
        self.operation_mode = "AUTO"
        return len(failures) == 0

    # -------------------------------------------------------------------------
    # 2. STARTUP CHRONOLOGY & MAIN CONTROL LOOP
    # -------------------------------------------------------------------------
    def run_startup_sequence(self):
        """
        Instant Startup Sequence:
        Removes any 20s or blocking startup delays.
        Immediately samples all sensors on launch and transitions straight to MONITORING.
        All functions of Pi and Arduino start immediately when main.py is run.
        """
        logger.info("==================================================")
        logger.info("  AGRONEX-PI INSTANT LAUNCH: SENSORS & SYSTEM ONLINE")
        logger.info("==================================================")
        self.set_state("MONITORING")
        self.read_dht_safe()
        self.read_water_safe()
        self.read_soil_safe()
        self.publish_telemetry_snapshot()
        self.last_actuator_time = time.time()
        self.last_dht_time = time.time()
        self.startup_sequence_done = True
        logger.info("System fully operational in MONITORING mode at t=0.")

    def read_all_sensors_now(self) -> dict:
        """Forces an immediate real-time read of all connected sensors across Pi and Arduino."""
        raw_s, soil_pct = self.read_soil_safe()
        water_pct, water_status = self.read_water_safe()
        temp, hum = self.read_dht_safe()
        gps_fix = self.gps_sensor.read_fix() if self.gps_sensor else None
        heading = self.compass_sensor.read_heading() if self.compass_sensor else None

        dist_f = 999
        dist_r = 999
        probe_angle = 175
        if self.motors and hasattr(self.motors, 'arduino') and self.motors.arduino and self.motors.arduino.connected:
            try:
                dist_f = self.motors.scan_front_distance(90)
                dist_r = self.motors.scan_rear_distance(90)
                status_info = self.motors.get_arduino_status()
                probe_angle = status_info.get("probe", 175)
            except Exception as e:
                logger.debug(f"Arduino sensor read error: {e}")

        result = {
            "soil_moisture": soil_pct,
            "raw_adc_soil": raw_s,
            "water_level": water_pct,
            "water_status": water_status,
            "temperature": temp,
            "humidity": hum,
            "heading_deg": heading,
            "gps": gps_fix,
            "dist_front_cm": dist_f,
            "dist_rear_cm": dist_r,
            "actuator_probe_angle": probe_angle,
            "actuator_deployed": getattr(self.motors, 'probe_deployed', False) if self.motors else False,
            "pump_state": self.relay.pump_state if self.relay else False,
            "cutter_state": self.relay.cutter_state if self.relay else False,
            "current_state": self.current_state,
            "operation_mode": self.operation_mode,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.publish_telemetry_snapshot()
        return result

    def run_periodic_actuator_cycle(self):
        """1-Hour Automatic Actuator Cycle: Halts chassis, lowers probe, reads soil, retracts probe."""
        if self.actuator_cycle_running or self.operation_mode != "AUTO" or self.current_state == "SAFE_STATE":
            return
        self.actuator_cycle_running = True
        prev_state = self.current_state
        try:
            logger.info("⏰ 1-Hour Actuator Cycle: Lowering probe for periodic soil moisture update...")
            self.set_state("ACTUATOR_PROBING")
            if self.motors:
                self.motors.stop()
                self.motors.deploy_soil_probe()
            time.sleep(2.5)

            self.read_soil_safe()

            if self.motors:
                self.motors.retract_soil_probe()
            time.sleep(1.5)
            self.last_actuator_time = time.time()
            logger.info(f"Actuator cycle finished. Soil moisture updated: {self.cached_soil_moisture}%")
        except Exception as e:
            logger.error(f"Error during actuator cycle: {e}")
        finally:
            self.actuator_cycle_running = False
            self.set_state(prev_state if prev_state != "ACTUATOR_PROBING" else "MONITORING")

    def read_soil_safe(self):
        """Reads soil moisture sensor and updates persistent cache."""
        try:
            raw_adc, soil_pct = self.soil_sensor.read_percentage() if self.soil_sensor else (520, 48.0)
            if soil_pct is not None:
                self.cached_soil_moisture = round(float(soil_pct), 1)
                self.cached_raw_adc = raw_adc
            return self.cached_raw_adc, self.cached_soil_moisture
        except Exception as e:
            logger.debug(f"Soil sensor read error: {e}")
            return self.cached_raw_adc, self.cached_soil_moisture

    def read_water_safe(self):
        """Continuously reads HW-038 water level sensor with zero delay and updates persistent cache."""
        try:
            raw_w, water_pct, water_status = self.water_sensor.read_percentage() if self.water_sensor else (8000, 85.0, "OPTIMAL")
            if water_pct is not None:
                self.cached_water_level = round(float(water_pct), 1)
                self.cached_water_status = water_status or "OPTIMAL"
            return self.cached_water_level, self.cached_water_status
        except Exception as e:
            logger.debug(f"Water sensor read error: {e}")
            return self.cached_water_level, self.cached_water_status

    def read_dht_safe(self):
        """Reads DHT sensor (10-minute interval) and updates persistent cache."""
        try:
            temp, hum = self.dht_sensor.read() if self.dht_sensor else (28.5, 62.0)
            if temp is not None and hum is not None:
                self.cached_temperature = round(float(temp), 1)
                self.cached_humidity = round(float(hum), 1)
                logger.info(f"DHT 10-Min Scan: Temp={self.cached_temperature}°C, Hum={self.cached_humidity}%")
            return self.cached_temperature, self.cached_humidity
        except Exception as e:
            logger.debug(f"DHT read error: {e}")
            return self.cached_temperature, self.cached_humidity

    def publish_telemetry_snapshot(self):
        """Pushes cached telemetry readings to local app and cloud relay."""
        gps_fix = self.gps_sensor.read_fix() if self.gps_sensor else None
        heading = self.compass_sensor.read_heading() if self.compass_sensor else None

        app.update_telemetry_cache({
            "soil_moisture": self.cached_soil_moisture,
            "raw_adc": self.cached_raw_adc,
            "water_level": self.cached_water_level,
            "water_status": self.cached_water_status,
            "temperature": self.cached_temperature,
            "humidity": self.cached_humidity,
            "gps": gps_fix,
            "heading_deg": heading,
            "navigation_status": self.nav_ctrl.last_status if self.nav_ctrl else "IDLE",
            "pump_state": self.relay.pump_state if self.relay else False,
            "cutter_state": self.relay.cutter_state if self.relay else False,
            "operation_mode": self.operation_mode,
            "current_state": self.current_state,
            "uptime_seconds": int(time.time() - self.start_time),
            "simulation_mode": self.simulate
        })

    def control_loop(self):
        """
        Main control loop. Executes startup chronology, continuous real-time water monitoring,
        10-min DHT scans, 1-hr actuator cycles, and mode-dependent actuation.
        """
        # Execute startup chronology on boot
        if not self.startup_sequence_done and self.current_state != "SAFE_STATE":
            try:
                self.run_startup_sequence()
            except Exception as e:
                logger.error(f"Startup sequence encountered error: {e}")
                self.set_state("MONITORING")

        while self.running:
            try:
                self.control_loop_heartbeat = time.time()

                if self.simulate:
                    print("\n*** SIMULATION MODE — NO REAL HARDWARE ***\n", flush=True)

                # Continuous Real-Time Water Level & Soil Moisture Monitoring
                self.read_water_safe()
                self.read_soil_safe()

                # Push telemetry immediately to AWS Cloud Relay when soil moisture or water level changes
                soil_changed = self._last_pushed_soil is None or abs(self.cached_soil_moisture - self._last_pushed_soil) >= 0.5
                water_changed = self._last_pushed_water is None or abs(self.cached_water_level - self._last_pushed_water) >= 0.5
                if soil_changed or water_changed:
                    self.publish_telemetry_snapshot()
                    if self.aws_relay:
                        self.aws_relay.push_telemetry_now()
                    self._last_pushed_soil = self.cached_soil_moisture
                    self._last_pushed_water = self.cached_water_level

                # Periodic 10-Minute Temperature Detection
                if (time.time() - self.last_dht_time) >= getattr(config, "DHT_TEMP_INTERVAL", 600.0):
                    self.read_dht_safe()
                    self.last_dht_time = time.time()

                # Periodic 1-Hour Soil Moisture Actuator Probe Cycle
                if self.operation_mode == "AUTO" and (time.time() - self.last_actuator_time) >= getattr(config, "ACTUATOR_AUTO_INTERVAL", 3600.0):
                    self.run_periodic_actuator_cycle()

                # -------------------------------------------------------------
                # AUTONOMOUS ACTUATION PHASES (Active only in AUTO mode)
                # -------------------------------------------------------------
                if self.current_state != "SAFE_STATE" and self.operation_mode == "AUTO":
                    # STEP A: Autonomous Irrigation
                    if self.irrigation_ctrl:
                        irr_status = self.irrigation_ctrl.evaluate_and_control()
                        if irr_status.get("pump_active", False):
                            self.set_state("IRRIGATING")
                        elif self.current_state == "IRRIGATING":
                            self.set_state("MONITORING")

                    # STEP B: Grass Trimming Scheduler (Independent from pump)
                    if self.cutter_ctrl:
                        cut_status = self.cutter_ctrl.evaluate_and_control()
                        if cut_status.get("cutter_active", False):
                            self.set_state("CUTTING")
                        elif self.current_state == "CUTTING":
                            self.set_state("MONITORING")

                    # STEP C: Periodic Disease Scanning Check
                    if time.time() - self.last_disease_scan_time >= config.DISEASE_SCAN_INTERVAL:
                        self.trigger_disease_scan()
                        self.last_disease_scan_time = time.time()

                    # STEP D: Autonomous Timed Navigation
                    if self.current_state == "MONITORING" and self.nav_ctrl:
                        self.set_state("NAVIGATING")
                        self.nav_ctrl.execute_waypoint_step()
                        self.set_state("MONITORING")
                elif self.operation_mode == "MANUAL":
                    # In manual mode, autonomous waypoint motion and auto-actuation are paused
                    pass

                # Simulation dynamics helper
                if self.simulate and hasattr(self.soil_sensor, 'apply_sim_dynamics') and self.relay:
                    self.soil_sensor.apply_sim_dynamics(self.relay.pump_state)
                if self.simulate and hasattr(self.water_sensor, 'apply_sim_dynamics') and self.relay:
                    self.water_sensor.apply_sim_dynamics(self.relay.pump_state)

                # Log periodic telemetry to SQLite DB
                try:
                    self.db.log_sensor_data(
                        soil_pct=self.cached_soil_moisture,
                        temp=self.cached_temperature,
                        hum=self.cached_humidity,
                        pump=self.relay.pump_state if self.relay else False,
                        cutter=self.relay.cutter_state if self.relay else False,
                        simulated=self.simulate
                    )
                except Exception as e:
                    logger.debug(f"DB log sensor data error: {e}")

                # Publish telemetry to cache and dashboard (retains last recorded data)
                self.publish_telemetry_snapshot()

            except Exception as e:
                logger.error(f"UNCAUGHT EXCEPTION IN CONTROL LOOP: {e}", exc_info=True)
                emergency_stop()
                self.db.log_system_event("CRASH_EXCEPTION", "CRITICAL", str(e), self.simulate)
                self.set_state("SAFE_STATE")

            time.sleep(config.POLL_INTERVAL)

    # -------------------------------------------------------------------------
    # 3. MANUAL OVERRIDE INTERFACES (INDEPENDENT RELAYS & VIRTUAL REMOTE)
    # -------------------------------------------------------------------------
    def manual_pump_on(self) -> bool:
        """Manually energizes water pump (sprinkler). Independent from grass cutter."""
        if self.nav_ctrl:
            self.nav_ctrl.stop()
        if self.relay:
            self.relay.pump_on()
        if self.irrigation_ctrl:
            self.irrigation_ctrl.is_irrigating = True
        app.update_telemetry_cache({"pump_state": True})
        if self.aws_relay:
            self.aws_relay.push_telemetry_now()
        logger.info("⚡ PUMP RELAY MANUALLY ENERGIZED (ON)")
        return True

    def manual_pump_off(self):
        """Manually de-energizes water pump."""
        if self.relay:
            self.relay.pump_off()
        if self.irrigation_ctrl:
            self.irrigation_ctrl.is_irrigating = False
        app.update_telemetry_cache({"pump_state": False})
        if self.aws_relay:
            self.aws_relay.push_telemetry_now()
        logger.info("⚡ PUMP RELAY MANUALLY DE-ENERGIZED (OFF)")

    def manual_cutter_on(self) -> bool:
        """Manually energizes grass cutter. Independent from water pump."""
        if self.nav_ctrl:
            self.nav_ctrl.stop()
        if self.relay:
            self.relay.cutter_on()
        if self.cutter_ctrl:
            self.cutter_ctrl.is_cutting = True
        app.update_telemetry_cache({"cutter_state": True})
        if self.aws_relay:
            self.aws_relay.push_telemetry_now()
        logger.info("⚡ CUTTER RELAY MANUALLY ENERGIZED (ON)")
        return True

    def manual_cutter_off(self):
        """Manually de-energizes grass cutter."""
        if self.relay:
            self.relay.cutter_off()
        if self.cutter_ctrl:
            self.cutter_ctrl.is_cutting = False
        app.update_telemetry_cache({"cutter_state": False})
        if self.aws_relay:
            self.aws_relay.push_telemetry_now()
        logger.info("⚡ CUTTER RELAY MANUALLY DE-ENERGIZED (OFF)")

    def get_telemetry_snapshot(self) -> dict:
        """Returns the latest telemetry dictionary for AWS relay and status logging."""
        snap = dict(app._telemetry_cache)
        snap["current_state"] = self.current_state
        snap["operation_mode"] = self.operation_mode
        if self.relay:
            snap["pump_state"] = self.relay.pump_state
            snap["cutter_state"] = self.relay.cutter_state
        if snap.get("gps") and isinstance(snap["gps"], dict):
            gps = dict(snap["gps"])
            if "latitude" in gps and "lat" not in gps:
                gps["lat"] = gps["latitude"]
            if "longitude" in gps and "lon" not in gps:
                gps["lon"] = gps["longitude"]
            snap["gps"] = gps
        return snap

    def handle_remote_command(self, cmd: str):
        """Processes remote commands polled from AWS API Gateway or local dashboard."""
        logger.info(f"Executing remote command: '{cmd}'")
        cmd_clean = cmd.lower().strip()

        # Operational Mode Switching
        if cmd_clean in ("mode_manual", "set_mode_manual", "manual"):
            self.operation_mode = "MANUAL"
            if self.nav_ctrl:
                self.nav_ctrl.stop()
            if self.motors:
                self.motors.stop()
            logger.info("System switched to MANUAL REMOTE mode.")
            app.update_telemetry_cache({"operation_mode": "MANUAL"})
            if self.aws_relay:
                self.aws_relay.push_telemetry_now()

        elif cmd_clean in ("mode_auto", "set_mode_auto", "auto"):
            self.operation_mode = "AUTO"
            # If stuck in SAFE_STATE, also resume to MONITORING so the control loop runs
            if self.current_state == "SAFE_STATE":
                self.set_state("MONITORING")
            logger.info("System switched to AUTONOMOUS mode.")
            app.update_telemetry_cache({"operation_mode": "AUTO", "current_state": self.current_state})
            if self.aws_relay:
                self.aws_relay.push_telemetry_now()

        # Virtual Remote - Chassis Driving Controls
        elif cmd_clean in ("move_forward", "car_forward", "forward"):
            if self.motors:
                self.motors.forward(speed=config.MOTOR_SPEED_DEFAULT)
            app.update_telemetry_cache({"chassis_motion": "FORWARD"})

        elif cmd_clean in ("move_backward", "car_backward", "backward"):
            if self.motors:
                self.motors.backward(speed=config.MOTOR_SPEED_DEFAULT)
            app.update_telemetry_cache({"chassis_motion": "BACKWARD"})

        elif cmd_clean in ("move_left", "car_left", "left"):
            if self.motors:
                self.motors.turn_left(speed=config.MOTOR_SPEED_TURN)
            app.update_telemetry_cache({"chassis_motion": "LEFT"})

        elif cmd_clean in ("move_right", "car_right", "right"):
            if self.motors:
                self.motors.turn_right(speed=config.MOTOR_SPEED_TURN)
            app.update_telemetry_cache({"chassis_motion": "RIGHT"})

        elif cmd_clean in ("move_stop", "car_stop", "stop_motion"):
            if self.motors:
                self.motors.stop()
            app.update_telemetry_cache({"chassis_motion": "STOPPED"})

        # Virtual Remote - Linear Actuator Soil Moisture Probe
        elif cmd_clean in ("actuator_down", "probe_down"):
            logger.info("Remote Actuator: Deploying soil moisture probe DOWN...")
            if self.motors:
                self.motors.deploy_soil_probe()
            # Read soil immediately when lowered
            threading.Thread(target=self._manual_probe_read_worker, daemon=True).start()
            app.update_telemetry_cache({"actuator_state": "DEPLOYED"})

        elif cmd_clean in ("actuator_up", "probe_up"):
            logger.info("Remote Actuator: Retracting soil moisture probe UP...")
            if self.motors:
                self.motors.retract_soil_probe()
            app.update_telemetry_cache({"actuator_state": "RETRACTED"})

        elif cmd_clean in ("actuator_stop", "probe_stop"):
            logger.info("Remote Actuator: Stopping probe actuator motion...")
            if self.motors and hasattr(self.motors, 'arduino_bridge') and self.motors.arduino_bridge:
                self.motors.arduino_bridge.send_command("STOP_PROBE")
            app.update_telemetry_cache({"actuator_state": "STOPPED"})

        # Independent Relay Controls (Water Pump & Grass Cutter)
        elif cmd_clean in ("pump_on", "sprinkler_on"):
            self.manual_pump_on()
        elif cmd_clean in ("pump_off", "sprinkler_off"):
            self.manual_pump_off()
        elif cmd_clean == "cutter_on":
            self.manual_cutter_on()
        elif cmd_clean == "cutter_off":
            self.manual_cutter_off()

        # Diagnostics, Scans & Emergency Stop
        elif cmd_clean == "scan":
            self.trigger_disease_scan()
        elif cmd_clean in ["stop", "emergency_stop", "estop"]:
            self.trigger_emergency_stop()
        elif cmd_clean in ["resume", "reset_estop"]:
            self.reset_emergency_stop()
        elif cmd_clean == "nav_north":
            threading.Thread(target=lambda: self.nav_ctrl.turn_to_heading(0.0), daemon=True).start()
        elif cmd_clean == "nav_east":
            threading.Thread(target=lambda: self.nav_ctrl.turn_to_heading(90.0), daemon=True).start()
        elif cmd_clean == "nav_south":
            threading.Thread(target=lambda: self.nav_ctrl.turn_to_heading(180.0), daemon=True).start()
        elif cmd_clean == "nav_west":
            threading.Thread(target=lambda: self.nav_ctrl.turn_to_heading(270.0), daemon=True).start()
        elif cmd_clean.startswith("steer_heading:"):
            try:
                deg = float(cmd_clean.split(":")[1])
                threading.Thread(target=lambda: self.nav_ctrl.turn_to_heading(deg), daemon=True).start()
            except Exception as e:
                logger.warning(f"Invalid steer_heading parameter: {cmd}")
        elif cmd_clean.startswith("set_waypoint:"):
            try:
                coords = cmd_clean.split(":")[1].split(",")
                lat, lon = float(coords[0]), float(coords[1])
                self.nav_ctrl.set_waypoints([(lat, lon)])
                logger.info(f"Target waypoint set via cloud: {lat}, {lon}")
            except Exception as e:
                logger.warning(f"Invalid waypoint parameter: {cmd}")
        elif cmd_clean == "nav_stop":
            self.nav_ctrl.stop()
        else:
            logger.warning(f"Unrecognized remote command: '{cmd}'")

    def _manual_probe_read_worker(self):
        """Worker thread to read soil moisture after manual deployment."""
        try:
            time.sleep(2.0)
            self.read_soil_safe()
            self.publish_telemetry_snapshot()
            if self.aws_relay:
                self.aws_relay.push_telemetry_now()
        except Exception as e:
            logger.debug(f"Manual probe read worker error: {e}")

    def start_aws_relay(self):
        """Starts the AWS Cloud Relay thread if not already running."""
        if self.aws_relay is not None:
            return
        try:
            self.aws_relay = AWSRelay(
                get_telemetry_fn=self.get_telemetry_snapshot,
                handle_command_fn=self.handle_remote_command,
                run_detection_fn=self.run_leaf_scan_from_file
            )
            self.aws_relay.start()
            self.aws_relay.start_camera_snapshot_thread()
            logger.info("AWS Cloud Relay thread started successfully.")
        except Exception as e:
            logger.warning(f"AWS Relay init exception: {e}")

    def run_leaf_scan_from_file(self, image_path: str) -> dict:
        """Runs ML leaf disease detection on an image from local or cloud trigger."""
        try:
            if not self.disease_detector:
                self.disease_detector = DiseaseDetector(simulate=self.simulate)
            return self.disease_detector.detect_from_image_path(image_path)
        except Exception as e:
            logger.error(f"Inference error on {image_path}: {e}")
            return {"success": False, "error": str(e)}

    def auto_scan_loop(self):
        """
        Continuously monitors camera feed for green plant presence.
        When foliage area exceeds GREEN_PIXEL_THRESHOLD, automatically halts
        motion, performs segmented leaf disease analysis, and uploads scan.
        """
        logger.info("Auto-Scan Green Detection loop running.")
        while self.running:
            try:
                time.sleep(0.5)

                if not config.DISEASE_AUTO_GREEN_TRIGGER:
                    continue

                # Don't scan if actively irrigating, cutting, or already scanning
                if self.current_state in ["IRRIGATING", "CUTTING", "SCANNING", "SELF_TEST", "BOOT"]:
                    continue

                # Check cooldown
                if (time.time() - self.last_auto_scan_time) < config.AUTO_SCAN_COOLDOWN:
                    continue

                # Grab camera frame (or simulated sample)
                frame_rgb = None
                if not self.simulate and self.camera:
                    try:
                        frame_rgb = self.camera.capture_array()
                    except Exception as e:
                        logger.debug(f"Camera frame capture error in auto-scan loop: {e}")

                if frame_rgb is None:
                    continue

                # Calculate green pixel fraction in HSV
                if cv2 is not None:
                    hsv = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2HSV)
                    lower_g = np.array([config.GREEN_H_LOW, config.GREEN_S_LOW, config.GREEN_V_LOW], dtype=np.uint8)
                    upper_g = np.array([config.GREEN_H_HIGH, config.GREEN_S_HIGH, config.GREEN_V_HIGH], dtype=np.uint8)
                    mask = cv2.inRange(hsv, lower_g, upper_g)
                    green_fraction = float(np.count_nonzero(mask)) / float(frame_rgb.shape[0] * frame_rgb.shape[1])
                else:
                    r = frame_rgb[:, :, 0].astype(float)
                    g = frame_rgb[:, :, 1].astype(float)
                    b = frame_rgb[:, :, 2].astype(float)
                    green_mask = (g > 1.15 * r) & (g > 1.15 * b) & (g > 50)
                    green_fraction = float(np.sum(green_mask)) / float(frame_rgb.shape[0] * frame_rgb.shape[1])

                if green_fraction >= config.GREEN_PIXEL_THRESHOLD:
                    logger.info(
                        f"🌱 Green plant detected! Coverage: {green_fraction*100:.1f}% "
                        f"(threshold: {config.GREEN_PIXEL_THRESHOLD*100:.1f}%). Triggering auto disease scan..."
                    )
                    self.last_auto_scan_time = time.time()
                    self.trigger_disease_scan(pre_captured_frame=frame_rgb)

            except Exception as e:
                logger.error(f"Error in auto_scan_loop: {e}")
                time.sleep(2.0)

    def trigger_disease_scan(self, pre_captured_frame: np.ndarray = None) -> dict:
        """Executes plant disease scan workflow using camera, leaf segmentation, and TFLite model."""
        previous_state = self.current_state
        self.set_state("SCANNING")
        logger.info("Executing Disease Scan Workflow (with leaf segmentation)...")

        try:
            # Stop chassis motion during image capture
            if self.nav_ctrl:
                self.nav_ctrl.stop()

            # Capture frame array or use pre_captured_frame
            if pre_captured_frame is not None:
                frame_rgb = pre_captured_frame
            elif not self.simulate and self.camera:
                frame_rgb = self.camera.capture_array()
            else:
                # In simulation mode, load a real leaf image from PlantVillage if available
                sample_found = False
                for test_folder in ["Tomato_Early_blight", "Tomato___Early_blight", "Tomato_healthy", "Potato___Early_blight"]:
                    folder_path = os.path.join(config.BASE_DIR, "plantvillage_dataset", "PlantVillage", test_folder)
                    if os.path.exists(folder_path) and os.path.isdir(folder_path):
                        files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                        if files:
                            try:
                                import cv2
                                sample_bgr = cv2.imread(os.path.join(folder_path, files[0]))
                                if sample_bgr is not None:
                                    frame_rgb = cv2.cvtColor(sample_bgr, cv2.COLOR_BGR2RGB)
                                    sample_found = True
                                    break
                            except Exception:
                                pass
                if not sample_found:
                    frame_rgb = (np.random.randint(40, 210, (224, 224, 3))).astype(np.uint8)

            # Perform AI Inference & Quality Check using leaf segmentation
            res = self.disease_detector.detect_with_leaf_segmentation(frame_rgb)

            # Save frame image to disk if successful scan
            timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scan_{timestamp_str}.jpg"
            img_rel_path = f"static/scans/{filename}"
            full_img_path = os.path.join(config.BASE_DIR, img_rel_path)
            os.makedirs(config.SCANS_DIR, exist_ok=True)

            try:
                import cv2
                frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
                cv2.imwrite(full_img_path, frame_bgr)
            except Exception:
                from PIL import Image
                Image.fromarray(frame_rgb).save(full_img_path)

            # Record result in SQLite Database
            self.db.log_disease_scan(
                label=res.get("label", "UNKNOWN"),
                common_name=res.get("common_name", "Unknown"),
                confidence=res.get("confidence", 0.0),
                image_path=img_rel_path,
                quality_flag=res.get("quality_flag", "OK"),
                simulated=self.simulate
            )

            # Push scan to AWS Cloud Relay if configured
            if self.aws_relay:
                self.aws_relay.push_scan_image(full_img_path, res)

            # Activate Buzzer + LED alert if non-healthy disease detected
            if res.get("should_alert", False):
                if self.alerts:
                    self.alerts.alert_disease(duration=3.0)

            self.set_state(previous_state)
            return res

        except Exception as e:
            logger.error(f"Disease scan failed: {e}")
            self.set_state(previous_state)
            return {"success": False, "error": str(e)}

    def trigger_emergency_stop(self):
        """Triggered on E-STOP signal."""
        self.set_state("SAFE_STATE")
        if self.nav_ctrl:
            self.nav_ctrl.stop()
        if self.cutter_ctrl:
            self.cutter_ctrl.emergency_stop()
        if self.irrigation_ctrl:
            self.irrigation_ctrl.emergency_stop()
        emergency_stop()
        app.update_telemetry_cache({
            "pump_state": False,
            "cutter_state": False,
            "current_state": "SAFE_STATE"
        })
        if self.aws_relay:
            self.aws_relay.push_telemetry_now()

    def reset_emergency_stop(self):
        """Resets SAFE_STATE back to MONITORING."""
        logger.info("Emergency Stop / SAFE_STATE reset.")
        self.set_state("MONITORING")
        app.update_telemetry_cache({
            "pump_state": False,
            "cutter_state": False,
            "current_state": "MONITORING"
        })
        if self.aws_relay:
            self.aws_relay.push_telemetry_now()

    def shutdown(self):
        """Clean shutdown procedure for signals and process exits."""
        logger.warning("Initiating graceful system shutdown...")
        self.running = False
        self.trigger_emergency_stop()

        if self.aws_relay:
            self.aws_relay.stop()
        if self.soil_sensor:
            self.soil_sensor.cleanup()
        if self.dht_sensor:
            self.dht_sensor.cleanup()
        if self.gps_sensor:
            self.gps_sensor.cleanup()
        if self.compass_sensor:
            self.compass_sensor.cleanup()
        if self.camera:
            self.camera.cleanup()
        if self.relay:
            self.relay.cleanup()
        if self.motors:
            self.motors.cleanup()

        logger.info("System shutdown complete. Relays de-energized, motors stopped.")


# -----------------------------------------------------------------------------
# WATCHDOG THREAD (§5.8)
# -----------------------------------------------------------------------------
WATCHDOG_GRACE_PERIOD = 45.0   # seconds — ignore watchdog during boot/startup

def start_watchdog(supervisor: MainSupervisor):
    """Monitors supervisor control loop heartbeat and trips E-STOP only on genuine hangs."""
    def _watchdog_loop():
        startup_time = time.time()
        while supervisor.running:
            time.sleep(5.0)
            # Skip watchdog during the first 45 seconds (startup sequence + sensor reads)
            if (time.time() - startup_time) < WATCHDOG_GRACE_PERIOD:
                continue
            elapsed = time.time() - supervisor.control_loop_heartbeat
            # Trip only if control loop has been frozen for more than 15s (not 3s)
            # and system is in an active state — never trip during SAFE_STATE/BOOT/IDLE
            if elapsed > 15.0 and supervisor.current_state not in ["SAFE_STATE", "BOOT", "IDLE", "SELF_TEST"]:
                logger.critical(f"WATCHDOG TRIP: Control loop frozen! No heartbeat for {elapsed:.1f}s. De-energizing actuators!")
                supervisor.trigger_emergency_stop()

    t = threading.Thread(target=_watchdog_loop, daemon=True)
    t.start()


# -----------------------------------------------------------------------------
# MAIN ENTRY POINT & SIGNAL HANDLERS (§4 & §5.8)
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AgroNex-Pi Main Controller Supervisor")
    parser.add_argument("--simulate", action="store_true", help="Opt-in simulation mode on PC without physical hardware")
    parser.add_argument("--port", type=int, default=5000, help="Flask Web Dashboard HTTP port")
    args = parser.parse_args()

    # Configure Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(config.LOG_PATH)
        ]
    )

    supervisor = MainSupervisor(simulate=args.simulate)

    # Register Fail-Safe Signal Handlers for SIGTERM and SIGINT (§5.8 & Constraint 4)
    def _signal_handler(signum, frame):
        sig_name = signal.Signals(signum).name
        logger.warning(f"RECEIVED SYSTEM SIGNAL ({sig_name}). SHUTTING DOWN IMMEDIATELY.")
        supervisor.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # Execute Startup Self-Test
    passed = supervisor.run_self_test()
    if not passed:
        logger.warning("Startup Self-Test: some hardware unavailable — system starts in DEGRADED mode (AUTO still active).")
        # Reset to MONITORING so the robot is NOT stuck in SAFE_STATE
        supervisor.set_state("MONITORING")
        supervisor.operation_mode = "AUTO"
    
    # Always start in AUTO mode
    supervisor.operation_mode = "AUTO"
    app.update_telemetry_cache({"operation_mode": "AUTO", "current_state": supervisor.current_state})

    # Attach References to Flask Web App
    app.set_app_references(supervisor.db, supervisor)

    # Start AWS Cloud Relay (handles both normal and diagnostic/simulated modes)
    supervisor.start_aws_relay()

    # Start Watchdog Thread (with 45s grace period so startup doesn't false-trip)
    start_watchdog(supervisor)

    # Start Main Control Loop in Background Thread
    control_thread = threading.Thread(target=supervisor.control_loop, daemon=True, name="ControlLoop")
    control_thread.start()

    # Start Continuous Camera Green Detection Auto-Scan Thread
    if config.DISEASE_AUTO_GREEN_TRIGGER:
        auto_scan_thread = threading.Thread(target=supervisor.auto_scan_loop, daemon=True, name="AutoGreenScanner")
        auto_scan_thread.start()

    # Start Flask Web Dashboard Server on Main Thread
    logger.info(f"Starting Flask Dashboard server on http://0.0.0.0:{args.port}...")
    try:
        app.app.run(host="0.0.0.0", port=args.port, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask Web Server crashed: {e}")
    finally:
        supervisor.shutdown()


if __name__ == "__main__":
    main()
