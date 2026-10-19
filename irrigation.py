#!/usr/bin/env python3
"""
AgroNex-Pi: Soil Moisture Sensing & Irrigation Controller (§5.2)

Hysteresis-based irrigation controller:
- Moisture < 35%  --> Pump ON
- Moisture > 65%  --> Pump OFF
- Polling Interval --> 30 seconds

Safety Interlocks:
1. Max Continuous Runtime (PUMP_MAX_RUNTIME = 60s): Auto shut-off on dry tank/stuck valve.
2. Minimum Cooldown (PUMP_COOLDOWN = 120s): Protects relay contacts & motor winding.
3. Implausible Reading Rejection: Rejects open-circuit (1023) or short-circuit (0) ADC readings.
4. Detailed Event Logging: Logs start/end timestamps, durations, and moisture deltas to DB.

DOCUMENTED HARDWARE LIMITATION & BEHAVIORAL FIX:
The capacitive soil moisture probe is chassis-mounted and inserted into the ground.
If the rover chassis moves while the probe is in contact with soil, it causes probe drag,
soil disruption, and inaccurate readings across different locations during a single pump cycle.
MITIGATION IMPLEMENTED:
The supervisor state machine halts chassis movement during the read-and-water cycle ('IRRIGATING' state).
Chassis navigation only resumes after the pump is turned off and the pump cooldown period has elapsed.
"""

import time
import datetime
import logging

import config
from hardware import SoilSensor, Relay, Motors
from database import DatabaseManager

logger = logging.getLogger("AgroNex.Irrigation")


class IrrigationController:
    def __init__(self, soil_sensor: SoilSensor, relay: Relay, motors: Motors, db: DatabaseManager, simulate: bool = False):
        self.soil_sensor = soil_sensor
        self.relay = relay
        self.motors = motors
        self.db = db
        self.simulate = simulate

        self.last_pump_off_time = 0.0  # Timestamp of last pump turn-off (for cooldown calculation)
        self.is_irrigating = False
        self.pump_start_time = 0.0
        self.pump_start_moisture = 0.0
        self.pump_start_iso = ""

    def evaluate_and_control(self) -> dict:
        """
        Executes a single soil moisture polling and irrigation decision cycle.
        Returns telemetry status dictionary.
        """
        raw_adc, moisture_pct = self.soil_sensor.read_percentage()

        # Step 1: Reject implausible sensor readings (§5.2)
        if moisture_pct is None:
            logger.warning(f"Irrigation Cycle SKIPPED: Implausible raw ADC reading ({raw_adc}). Sensor may be disconnected.")
            self.db.log_system_event("SENSOR_IMPLAUSIBLE", "WARNING", f"Raw ADC {raw_adc} out of valid bounds ({config.ADC_MIN_VALID}-{config.ADC_MAX_VALID}).", self.simulate)
            return {
                "raw_adc": raw_adc,
                "moisture_pct": None,
                "pump_active": self.relay.pump_state,
                "status": "SENSOR_IMPLAUSIBLE"
            }

        logger.info(f"Soil Moisture Reading: {moisture_pct:.1f}% (Raw ADC: {raw_adc})")

        current_time = time.time()

        # Step 2: Handle active irrigation state
        if self.is_irrigating:
            runtime = current_time - self.pump_start_time

            # Condition A: Upper moisture threshold reached -> Normal completion
            if moisture_pct >= config.MOISTURE_HIGH:
                logger.info(f"Soil moisture reached target upper threshold ({moisture_pct:.1f}% >= {config.MOISTURE_HIGH}%). Stopping pump.")
                self._stop_pump(moisture_pct, trigger_type="HYSTERESIS_HIGH_TARGET")
                return {
                    "raw_adc": raw_adc,
                    "moisture_pct": moisture_pct,
                    "pump_active": False,
                    "status": "IRRIGATION_COMPLETE"
                }

            # Condition B: Max pump runtime exceeded -> Safety timeout shut-off
            if runtime >= config.PUMP_MAX_RUNTIME:
                logger.error(f"PUMP SAFETY TIMEOUT: Pump ran for {runtime:.1f}s without soil moisture rising to {config.MOISTURE_HIGH}%. Empty reservoir or leak suspected!")
                self.db.log_system_event("PUMP_TIMEOUT", "ERROR", f"Pump safety shutoff after {runtime:.1f}s. Moisture started at {self.pump_start_moisture:.1f}%, currently {moisture_pct:.1f}%.", self.simulate)
                self._stop_pump(moisture_pct, trigger_type="PUMP_SAFETY_TIMEOUT")
                return {
                    "raw_adc": raw_adc,
                    "moisture_pct": moisture_pct,
                    "pump_active": False,
                    "status": "PUMP_TIMEOUT_SHUTDOWN"
                }

            logger.info(f"Irrigation ongoing... Runtime: {runtime:.1f}s / {config.PUMP_MAX_RUNTIME}s. Current moisture: {moisture_pct:.1f}%")
            return {
                "raw_adc": raw_adc,
                "moisture_pct": moisture_pct,
                "pump_active": True,
                "status": "IRRIGATING"
            }

        # Step 3: Handle pump activation decision (Pump currently OFF)
        if moisture_pct < config.MOISTURE_LOW:
            # Check Cooldown Period (§5.2)
            time_since_off = current_time - self.last_pump_off_time
            if time_since_off < config.PUMP_COOLDOWN:
                remaining_cooldown = config.PUMP_COOLDOWN - time_since_off
                logger.info(f"Moisture low ({moisture_pct:.1f}% < {config.MOISTURE_LOW}%), but pump is in COOLDOWN phase ({remaining_cooldown:.1f}s remaining). Waiting.")
                return {
                    "raw_adc": raw_adc,
                    "moisture_pct": moisture_pct,
                    "pump_active": False,
                    "status": f"COOLDOWN_WAIT_{int(remaining_cooldown)}S"
                }

            # Start Irrigation Cycle
            logger.warning(f"Soil moisture LOW ({moisture_pct:.1f}% < {config.MOISTURE_LOW}%). Halting chassis and turning pump ON.")
            
            # MANDATORY BEHAVIOR: Stop chassis motion before starting water pump
            self.motors.stop()

            self.is_irrigating = True
            self.pump_start_time = current_time
            self.pump_start_moisture = moisture_pct
            self.pump_start_iso = datetime.datetime.now().isoformat()
            self.relay.pump_on()

            self.db.log_system_event("IRRIGATION_START", "INFO", f"Pump activated. Initial moisture: {moisture_pct:.1f}%.", self.simulate)

            return {
                "raw_adc": raw_adc,
                "moisture_pct": moisture_pct,
                "pump_active": True,
                "status": "IRRIGATION_STARTED"
            }

        return {
            "raw_adc": raw_adc,
            "moisture_pct": moisture_pct,
            "pump_active": False,
            "status": "MOISTURE_OK"
        }

    def _stop_pump(self, final_moisture: float, trigger_type: str):
        """Helper to turn off pump, log irrigation event to DB, and update cooldown timer."""
        self.relay.pump_off()
        self.is_irrigating = False
        self.last_pump_off_time = time.time()
        duration_s = round(self.last_pump_off_time - self.pump_start_time, 1)
        end_iso = datetime.datetime.now().isoformat()

        logger.info(f"Irrigation cycle stopped. Duration: {duration_s}s. Start Moisture: {self.pump_start_moisture:.1f}%, End Moisture: {final_moisture:.1f}%. Trigger: {trigger_type}")

        # Log event to database for efficiency evaluation metrics
        self.db.log_irrigation_event(
            start_t=self.pump_start_iso,
            end_t=end_iso,
            duration_s=duration_s,
            start_moist=self.pump_start_moisture,
            end_moist=final_moisture,
            trigger=trigger_type,
            simulated=self.simulate
        )

    def manual_start(self) -> bool:
        """Manually starts the irrigation pump with safety interlocks."""
        # Independent Relay Control: Water pump and grass cutter can operate concurrently
        if self.is_irrigating:
            logger.info("Pump is already active.")
            return True

        if self.motors:
            self.motors.stop()

        raw_adc, moisture_pct = self.soil_sensor.read_percentage()
        current_time = time.time()
        self.is_irrigating = True
        self.pump_start_time = current_time
        self.pump_start_moisture = moisture_pct if moisture_pct is not None else 0.0
        self.pump_start_iso = datetime.datetime.now().isoformat()
        self.relay.pump_on()

        self.db.log_system_event("IRRIGATION_MANUAL_START", "INFO", f"Pump activated manually. Moisture: {self.pump_start_moisture:.1f}%.", self.simulate)
        return True

    def manual_stop(self):
        """Manually stops the irrigation pump."""
        if self.is_irrigating:
            _, moisture_pct = self.soil_sensor.read_percentage()
            self._stop_pump(moisture_pct if moisture_pct is not None else 0.0, trigger_type="MANUAL_OVERRIDE_OFF")
        else:
            self.relay.pump_off()

    def emergency_stop(self):
        """Stops pump immediately on emergency signal."""
        if self.is_irrigating:
            self._stop_pump(0.0, trigger_type="EMERGENCY_STOP")
        else:
            self.relay.pump_off()

