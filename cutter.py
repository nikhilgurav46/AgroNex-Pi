#!/usr/bin/env python3
"""
AgroNex-Pi: Grass Trimmer / Cutter Scheduler & Controller (§5.3)

Schedules periodic grass trimming operations:
- Interval: CUTTER_INTERVAL (Default 3600 seconds = 1 hour)
- Duration: CUTTER_DURATION (Default 30 seconds)

CURRENT BUDGET & SAFETY INTERLOCK:
Simultaneous operation of chassis drive motors and the high-current 12V grass cutting motor
can cause severe voltage sags on the Li-ion battery pack and brown out the Pi.
MITIGATION:
The cutter module requires chassis motors to be STOPPED before energizing Relay CH2.
The cutter will refuse to start if CUTTER_ENABLED is set to False in config.py (indoor safety mode).
"""

import time
import logging

import config
from hardware import Relay, Motors
from database import DatabaseManager

logger = logging.getLogger("AgroNex.Cutter")


class CutterController:
    def __init__(self, relay: Relay, motors: Motors, db: DatabaseManager, simulate: bool = False):
        self.relay = relay
        self.motors = motors
        self.db = db
        self.simulate = simulate

        self.last_cutter_run = time.time()  # Timestamp of last cutter completion
        self.is_cutting = False
        self.cutter_start_time = 0.0

    def evaluate_and_control(self) -> dict:
        """
        Evaluates grass trimming schedule and executes timed trim run.
        Returns cutter status dictionary.
        """
        if not config.CUTTER_ENABLED:
            return {"cutter_active": False, "status": "CUTTER_DISABLED_IN_CONFIG"}

        current_time = time.time()

        # Step 1: Handle active cutting cycle
        if self.is_cutting:
            duration = current_time - self.cutter_start_time
            if duration >= config.CUTTER_DURATION:
                logger.info(f"Grass trimming cycle completed ({duration:.1f}s). De-energizing cutter relay.")
                self._stop_cutter(trigger="SCHEDULED_COMPLETE")
                return {"cutter_active": False, "status": "TRIM_CYCLE_COMPLETE"}

            # Re-enforce chassis motor halt during cutting cycle
            self.motors.stop()
            return {"cutter_active": True, "status": f"CUTTING_ACTIVE_{int(duration)}S"}

        # Step 2: Check schedule for next cutting run
        time_since_last = current_time - self.last_cutter_run
        if time_since_last >= config.CUTTER_INTERVAL:
            logger.warning(f"Cutter interval elapsed ({time_since_last:.0f}s >= {config.CUTTER_INTERVAL}s). Starting grass trimming run.")
            
            # MANDATORY CURRENT MANAGEMENT: Halt chassis motors before starting cutter motor
            self.motors.stop()

            success = self.relay.cutter_on()
            if success:
                self.is_cutting = True
                self.cutter_start_time = current_time
                self.db.log_system_event("CUTTER_START", "INFO", f"Grass cutter activated for {config.CUTTER_DURATION}s.", self.simulate)
                return {"cutter_active": True, "status": "TRIM_CYCLE_STARTED"}
            else:
                return {"cutter_active": False, "status": "CUTTER_RELAY_REJECTED"}

        remaining_time = config.CUTTER_INTERVAL - time_since_last
        return {"cutter_active": False, "status": f"IDLE_NEXT_TRIM_IN_{int(remaining_time)}S"}

    def manual_start(self) -> bool:
        """Manually triggers a grass trimming cycle from the dashboard API."""
        if not config.CUTTER_ENABLED:
            logger.warning("Manual cutter start REJECTED: CUTTER_ENABLED is False.")
            return False

        # Independent Relay Control: Water pump and grass cutter can operate concurrently
        if self.is_cutting:
            logger.info("Cutter is already running.")
            return True

        self.motors.stop()
        success = self.relay.cutter_on()
        if success:
            self.is_cutting = True
            self.cutter_start_time = time.time()
            self.db.log_system_event("CUTTER_MANUAL_START", "INFO", "Grass cutter activated manually.", self.simulate)
            return True
        return False

    def manual_stop(self):
        """Manually turns off grass cutter."""
        if self.is_cutting:
            self._stop_cutter(trigger="MANUAL_STOP")

    def _stop_cutter(self, trigger: str):
        self.relay.cutter_off()
        self.is_cutting = False
        duration = round(time.time() - self.cutter_start_time, 1) if self.cutter_start_time > 0 else 0.0
        self.last_cutter_run = time.time()
        self.db.log_system_event("CUTTER_STOP", "INFO", f"Grass cutter stopped. Duration: {duration}s. Reason: {trigger}.", self.simulate)

    def emergency_stop(self):
        """Hard-stops cutter immediately."""
        self.relay.cutter_off()
        self.is_cutting = False
