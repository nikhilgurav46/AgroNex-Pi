#!/usr/bin/env python3
"""GPS + compass waypoint navigation for AgroNex-Pi.

There are no wheel encoders. The NEO-7M supplies global position and the
HMC5883L supplies heading. The rover moves only in short, stop-and-recheck
bursts; missing GPS/compass data or an empty mission always leaves it stopped.
This is not obstacle avoidance: a human safety observer remains required.
"""

import logging
import math
import time

import config
from hardware import Motors, GPSSensor, CompassSensor

logger = logging.getLogger("AgroNex.Navigation")


def _distance_and_bearing(lat1, lon1, lat2, lon2):
    """Return great-circle distance (m) and initial bearing (degrees)."""
    radius = 6_371_000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    distance = radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return distance, (math.degrees(math.atan2(y, x)) + 360) % 360


class NavigationController:
    def __init__(self, motors: Motors, gps: GPSSensor, compass: CompassSensor):
        self.motors = motors
        self.gps = gps
        self.compass = compass
        self.is_navigating = False
        self.waypoints = list(config.NAV_WAYPOINTS)
        self.waypoint_index = 0
        self.last_status = "Mission not configured"

    def execute_waypoint_step(self):
        """Perform one safe GPS/heading-guided control slice and then stop."""
        self.motors.stop()
        if self.waypoint_index >= len(self.waypoints):
            self.last_status = "No active waypoint"
            return {"active": False, "reason": self.last_status}
        fix = self.gps.read_fix()
        if not fix or time.time() - fix["timestamp"] > config.GPS_FIX_MAX_AGE:
            self.last_status = "Waiting for valid, recent GPS fix"
            logger.warning(self.last_status)
            return {"active": False, "reason": self.last_status}

        heading = self.compass.read_heading()
        target_lat, target_lon = self.waypoints[self.waypoint_index]
        distance, bearing = _distance_and_bearing(
            fix["latitude"], fix["longitude"], target_lat, target_lon
        )
        if distance <= config.NAV_WAYPOINT_REACHED_M:
            self.waypoint_index += 1
            self.last_status = f"Waypoint reached ({distance:.1f} m)"
            return {"active": False, "reached": True, "distance_m": distance}

        error = (bearing - heading + 540) % 360 - 180
        self.is_navigating = True
        try:
            if abs(error) > config.NAV_HEADING_TOLERANCE_DEG:
                (self.motors.turn_right if error > 0 else self.motors.turn_left)(config.MOTOR_SPEED_TURN)
                time.sleep(config.NAV_TURN_SLICE)
                action = "turn"
            else:
                self.motors.forward(config.MOTOR_SPEED_DEFAULT)
                time.sleep(config.NAV_DRIVE_SLICE)
                action = "forward"
        finally:
            self.motors.stop()
            self.is_navigating = False

        self.last_status = f"{action}: {distance:.1f} m, heading error {error:.1f}°"
        logger.info("GPS navigation: %s", self.last_status)
        return {"active": True, "action": action, "distance_m": round(distance, 1),
                "bearing": round(bearing, 1), "heading": round(heading, 1),
                "heading_error": round(error, 1)}

    def set_waypoints(self, waypoints: list):
        """Replaces the waypoint mission list and resets index to 0."""
        self.waypoints = [(float(pt[0]), float(pt[1])) for pt in waypoints]
        self.waypoint_index = 0
        self.last_status = f"Mission updated: {len(self.waypoints)} waypoints"
        logger.info(self.last_status)

    def add_waypoint(self, lat: float, lon: float):
        """Appends a new target coordinate to the mission."""
        self.waypoints.append((float(lat), float(lon)))
        logger.info("Added waypoint: (%s, %s). Total: %d", lat, lon, len(self.waypoints))

    def clear_waypoints(self):
        """Clears all waypoints and halts navigation."""
        self.stop()
        self.waypoints.clear()
        self.waypoint_index = 0
        self.last_status = "Mission cleared"
        logger.info(self.last_status)

    def get_mission(self) -> dict:
        """Returns current mission status and remaining waypoints."""
        current_target = self.waypoints[self.waypoint_index] if self.waypoint_index < len(self.waypoints) else None
        return {
            "waypoints": self.waypoints,
            "current_index": self.waypoint_index,
            "total": len(self.waypoints),
            "current_target": current_target,
            "last_status": self.last_status,
            "is_navigating": self.is_navigating
        }

    def turn_to_heading(self, target_heading: float, max_attempts: int = 15):
        """
        Pivots the robot until the current compass heading matches target_heading
        within NAV_HEADING_TOLERANCE_DEG.
        """
        if not self.compass or not self.motors:
            logger.warning("Compass or Motors not available for heading steering.")
            return False
        target_heading = (float(target_heading) % 360 + 360) % 360
        self.is_navigating = True
        logger.info(f"Steering robot to compass heading: {target_heading:.1f}°")
        try:
            for attempt in range(max_attempts):
                current = self.compass.read_heading()
                if current is None:
                    logger.warning("Compass read returned None during steering.")
                    break
                error = (target_heading - current + 540) % 360 - 180
                logger.debug(f"Steering attempt {attempt+1}: current={current:.1f}°, target={target_heading:.1f}°, error={error:.1f}°")
                if abs(error) <= config.NAV_HEADING_TOLERANCE_DEG:
                    self.motors.stop()
                    self.last_status = f"Aligned to {target_heading:.1f}° (current: {current:.1f}°)"
                    logger.info(self.last_status)
                    return True
                if error > 0:
                    self.motors.turn_right(config.MOTOR_SPEED_TURN)
                else:
                    self.motors.turn_left(config.MOTOR_SPEED_TURN)
                time.sleep(config.NAV_TURN_SLICE)
                self.motors.stop()
                time.sleep(0.1)
        finally:
            self.motors.stop()
            self.is_navigating = False
        return False

    def stop(self):
        self.is_navigating = False
        self.motors.stop()
        logger.info("Navigation Controller -> STOPPED")
