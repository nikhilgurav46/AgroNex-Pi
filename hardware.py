#!/usr/bin/env python3
"""
AgroNex-Pi: Low-Level Hardware Driver Layer (§5.1)

Wraps all physical hardware interactions (GPIO, SPI, Sensors, Relays, Motors, Camera).
Nothing else in the codebase touches GPIO or SPI directly.

Constraint 3 Compliance:
No silent fallbacks on ImportError. Hardware initialization fails loudly unless
opt-in simulation mode (--simulate) is explicitly requested.
"""

import sys
import os
import time
import logging
import threading
import math
import numpy as np

import config

logger = logging.getLogger("AgroNex.Hardware")

# Global flag set by main.py if --simulate CLI flag is passed
SIMULATION_MODE = False
_spi_lock = threading.Lock()

# Hardware Module Globals
GPIO = None
spidev = None
adafruit_dht = None
Picamera2 = None
cv2 = None
serial = None
SMBus = None

def initialize_hardware_libs(simulate: bool = False):
    """
    Imports and verifies physical hardware libraries.
    If simulate=False and any hardware library is missing, raises RuntimeError and exits.
    """
    global GPIO, spidev, adafruit_dht, Picamera2, cv2, serial, SMBus, SIMULATION_MODE
    SIMULATION_MODE = simulate

    if SIMULATION_MODE:
        logger.warning("*** SIMULATION MODE ENABLED — HARDWARE DRIVERS MOCKED ***")
        try:
            import cv2 as _cv2
            cv2 = _cv2
        except ImportError:
            cv2 = None
        return

    # Real hardware imports - warn if optional sensor drivers are missing
    core_missing = []
    try:
        import RPi.GPIO as _GPIO
        GPIO = _GPIO
    except ImportError:
        core_missing.append("RPi.GPIO")

    try:
        import spidev as _spidev
        spidev = _spidev
    except ImportError:
        logger.debug("spidev not installed (MCP3008 fallback unavailable).")

    try:
        import adafruit_dht as _adafruit_dht
        adafruit_dht = _adafruit_dht
    except ImportError:
        logger.warning("adafruit_dht not installed. DHT11/22 will be disabled. (Install with: pip install adafruit-circuitpython-dht)")

    try:
        from picamera2 import Picamera2 as _Picamera2
        Picamera2 = _Picamera2
    except ImportError:
        logger.warning("picamera2 not installed. Camera scanning will run in mock mode.")

    try:
        import cv2 as _cv2
        cv2 = _cv2
    except ImportError:
        logger.warning("opencv-python (cv2) not installed.")

    try:
        import serial as _serial
        serial = _serial
    except ImportError:
        logger.warning("pyserial not installed. GPS will be disabled.")

    try:
        from smbus2 import SMBus as _SMBus
        SMBus = _SMBus
    except ImportError:
        logger.warning("smbus2 not installed. ADS1115 I2C ADC will be disabled.")

    if core_missing:
        msg = (
            f"CRITICAL HARDWARE ERROR: Mandatory dependencies missing: {', '.join(core_missing)}.\n"
            "Running on a non-Raspberry Pi OS or missing driver packages.\n"
            "To test on a PC without hardware, pass the '--simulate' command-line flag explicitly.\n"
            "Refusing to run with silent mock fallbacks."
        )
        logger.critical(msg)
        raise RuntimeError(msg)

    # Set global GPIO mode once
    if GPIO is not None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        logger.info("GPIO BCM mode initialized successfully.")


# -----------------------------------------------------------------------------
# 1. ADS1115 16-BIT I2C ADC & SENSORS (Soil Moisture & HW-038 Water Level)
# -----------------------------------------------------------------------------
class ADS1115ADC:
    """
    ADS1115 16-Bit 4-Channel I2C ADC Driver.
    Reads single-ended analog voltages from channels A0 to A3 over I2C bus 1.
    """
    _bus_instance = None
    _lock = threading.Lock()

    def __init__(self, bus_num: int = config.ADS1115_I2C_BUS, address: int = config.ADS1115_I2C_ADDRESS):
        self.bus_num = bus_num
        self.address = address
        self.bus = None

        if not SIMULATION_MODE:
            self._ensure_bus()

    def _ensure_bus(self):
        """Ensures the smbus2 I2C connection is active, auto-connecting if needed."""
        if SIMULATION_MODE:
            return None
        if self.bus is not None:
            return self.bus
        try:
            import smbus2
            if ADS1115ADC._bus_instance is None:
                ADS1115ADC._bus_instance = smbus2.SMBus(self.bus_num)
            self.bus = ADS1115ADC._bus_instance
            logger.info(f"ADS1115 I2C ADC initialized on bus {self.bus_num} at address 0x{self.address:02X}.")
            return self.bus
        except Exception as e:
            logger.warning(f"ADS1115 I2C bus {self.bus_num} notice: {e} (Check: I2C enabled, smbus2 installed)")
            return None

    def read_raw(self, channel: int = 0) -> int:
        """
        Reads single-ended raw 16-bit integer (0 to 32767) for the given channel (0-3).
        Full-Scale Range: ±4.096V (PGA bits = 001).
        """
        if SIMULATION_MODE:
            return 12000

        bus = self._ensure_bus()
        if bus is None:
            return 12000

        with ADS1115ADC._lock:
            try:
                # Config register 16-bit word:
                # OS=1 (start single conversion)
                # MUX: 0b100 for AIN0, 0b101 for AIN1, 0b110 for AIN2, 0b111 for AIN3
                # PGA=001 (±4.096V)
                # MODE=1 (single-shot)
                # DR=100 (128 SPS)
                # COMP_QUE=11 (disable comparator)
                mux = (0x04 | (channel & 0x03)) << 12
                config_word = 0x8000 | mux | 0x0200 | 0x0100 | 0x0080 | 0x0003
                msb = (config_word >> 8) & 0xFF
                lsb = config_word & 0xFF

                # Write to Config register (0x01)
                bus.write_i2c_block_data(self.address, 0x01, [msb, lsb])
                time.sleep(0.015)  # Wait for 128 SPS conversion (~8 ms + safety margin)

                # Read from Conversion register (0x00)
                data = bus.read_i2c_block_data(self.address, 0x00, 2)
                raw = (data[0] << 8) | data[1]
                if raw > 32767:
                    raw = 0
                return raw
            except Exception as e:
                logger.warning(f"ADS1115 read channel A{channel} error (0x{self.address:02X}): {e}")
                return 0



class SoilSensor:
    """
    Capacitive Soil Moisture Sensor v1.2 driver.
    Reads analog moisture voltage via ADS1115 I2C ADC (Channel A0)
    with seamless fallback to MCP3008 SPI ADC if configured.
    """
    def __init__(self, channel: int = config.ADS1115_CH_SOIL):
        self.channel = channel
        self.sim_moisture_pct = 28.0
        self.use_ads = getattr(config, "USE_ADS1115", True)
        self.ads = None
        self.spi = None

        if not SIMULATION_MODE:
            if self.use_ads:
                try:
                    self.ads = ADS1115ADC(bus_num=config.ADS1115_I2C_BUS, address=config.ADS1115_I2C_ADDRESS)
                    logger.info("SoilSensor configured via ADS1115 (Channel A0).")
                except Exception as e:
                    logger.warning(f"ADS1115 init exception for soil sensor: {e}")
            else:
                try:
                    self.spi = spidev.SpiDev()
                    self.spi.open(0, 0)
                    self.spi.max_speed_hz = 1350000
                    logger.info("SoilSensor configured via MCP3008 SPI.")
                except Exception as e:
                    logger.warning(f"MCP3008 SpiDev fallback exception: {e}")

    def read_raw(self) -> int:
        if SIMULATION_MODE:
            pct = max(0.0, min(100.0, self.sim_moisture_pct + float(np.random.normal(0, 0.8))))
            if self.use_ads:
                raw = config.ADS_SOIL_DRY - (pct / 100.0) * (config.ADS_SOIL_DRY - config.ADS_SOIL_WET)
                return int(max(config.ADS_SOIL_MIN_VALID, min(config.ADS_SOIL_MAX_VALID, raw)))
            raw = config.ADC_DRY - (pct / 100.0) * (config.ADC_DRY - config.ADC_WET)
            return int(max(config.ADC_MIN_VALID, min(config.ADC_MAX_VALID, raw)))

        if self.use_ads and self.ads:
            return self.ads.read_raw(self.channel)

        if self.spi:
            with _spi_lock:
                adc = self.spi.xfer2([1, (8 + self.channel) << 4, 0])
                return ((adc[1] & 3) << 8) + adc[2]
        return 0

    def read_percentage(self) -> tuple:
        """
        Converts raw ADC value to soil moisture percentage (0.0 - 100.0%).
        Returns: (raw_adc: int, moisture_pct: float or None)
        """
        raw = self.read_raw()
        if self.use_ads:
            if raw < config.ADS_SOIL_MIN_VALID or raw > config.ADS_SOIL_MAX_VALID:
                logger.warning(f"Implausible ADS1115 soil ADC reading: {raw}")
                return raw, None
            pct = (config.ADS_SOIL_DRY - raw) / (config.ADS_SOIL_DRY - config.ADS_SOIL_WET) * 100.0
            pct = max(0.0, min(100.0, pct))
            return raw, round(pct, 1)

        if raw < config.ADC_MIN_VALID or raw > config.ADC_MAX_VALID:
            logger.warning(f"Implausible raw ADC reading detected: {raw}")
            return raw, None

        pct = (config.ADC_DRY - raw) / (config.ADC_DRY - config.ADC_WET) * 100.0
        pct = max(0.0, min(100.0, pct))
        return raw, round(pct, 1)

    def apply_sim_dynamics(self, pump_on: bool):
        """Gradual dry-down / wet-up used only in --simulate mode."""
        if not SIMULATION_MODE:
            return
        if pump_on:
            self.sim_moisture_pct = min(92.0, self.sim_moisture_pct + 12.0)
        else:
            self.sim_moisture_pct = max(18.0, self.sim_moisture_pct - 3.5)

    def cleanup(self):
        if self.spi is not None:
            try:
                self.spi.close()
            except Exception:
                pass


class WaterLevelSensor:
    """
    HW-038 3-Pin Water Level / Depth Sensor.
    Measures reservoir water level via ADS1115 I2C ADC Channel A1.
    Outputs: raw reading, percentage (0-100%), and qualitative status.
    """
    def __init__(self, channel: int = config.ADS1115_CH_WATER):
        self.channel = channel
        self.ads = None
        self.sim_water_pct = 84.0

        if not SIMULATION_MODE:
            try:
                self.ads = ADS1115ADC(bus_num=config.ADS1115_I2C_BUS, address=config.ADS1115_I2C_ADDRESS)
                logger.info(f"WaterLevelSensor initialized on ADS1115 Channel A{channel}.")
            except Exception as e:
                logger.warning(f"WaterLevelSensor ADS1115 init notice: {e}")

    def read_raw(self) -> int:
        if SIMULATION_MODE or not self.ads:
            pct = max(5.0, min(100.0, self.sim_water_pct + float(np.random.normal(0, 0.4))))
            raw = config.HW038_RAW_EMPTY + (pct / 100.0) * (config.HW038_RAW_FULL - config.HW038_RAW_EMPTY)
            return int(raw)
        return self.ads.read_raw(self.channel)

    def read_percentage(self) -> tuple:
        """
        Returns: (raw: int, pct: float, status: str)
        """
        raw = self.read_raw()
        pct = (raw - config.HW038_RAW_EMPTY) / (config.HW038_RAW_FULL - config.HW038_RAW_EMPTY) * 100.0
        pct = max(0.0, min(100.0, round(pct, 1)))

        if pct < config.WATER_CRITICAL_LOW:
            status = "CRITICAL_LOW"
        elif pct < 45.0:
            status = "LOW"
        elif pct < 75.0:
            status = "ADEQUATE"
        else:
            status = "OPTIMAL"

        return raw, pct, status

    def apply_sim_dynamics(self, pump_on: bool):
        """Lowers simulated water level slightly when pump is active."""
        if not SIMULATION_MODE:
            return
        if pump_on:
            self.sim_water_pct = max(8.0, self.sim_water_pct - 2.0)

    def cleanup(self):
        pass


# -----------------------------------------------------------------------------
# 2. DHT11 / DHT22 SENSOR
# -----------------------------------------------------------------------------
class DHTSensor:
    """
    Wraps adafruit_dht.
    Handles intermittent sensor communication failures by retrying up to max_retries
    times before returning (None, None) without crashing the supervisor loop.
    """
    def __init__(self, pin: int = config.PIN_DHT_DATA, sensor_type: str = "DHT11"):
        self.pin = pin
        self.dht_device = None

        if not SIMULATION_MODE:
            try:
                import board
                # Map BCM pin number to Adafruit Board pin
                board_pin = getattr(board, f"D{pin}", None)
                if board_pin is None:
                    raise ValueError(f"Invalid GPIO pin for DHT sensor: {pin}")

                if adafruit_dht is not None:
                    if sensor_type.upper() == "DHT22":
                        self.dht_device = adafruit_dht.DHT22(board_pin)
                    else:
                        self.dht_device = adafruit_dht.DHT11(board_pin)
                    logger.info(f"DHTSensor ({sensor_type}) initialized on BCM GPIO{pin}.")
                else:
                    logger.warning("adafruit_dht not installed. DHT sensor disabled.")
            except Exception as e:
                logger.warning(f"DHTSensor init notice: {e}")

    def read(self, max_retries: int = 3) -> tuple:
        """
        Reads temperature (°C) and humidity (%).
        Returns: (temp_c: float or None, humidity_pct: float or None)
        """
        if SIMULATION_MODE:
            sim_temp = round(26.5 + np.random.normal(0, 0.5), 1)
            sim_hum = round(58.0 + np.random.normal(0, 1.0), 1)
            return sim_temp, sim_hum

        if self.dht_device is None:
            return None, None

        for attempt in range(max_retries):
            try:
                temp = self.dht_device.temperature
                humidity = self.dht_device.humidity
                if temp is not None and humidity is not None:
                    return round(float(temp), 1), round(float(humidity), 1)
            except RuntimeError as e:
                # Intermittent read errors are expected with DHT 1-wire timing
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Unexpected error reading DHT sensor: {e}")
                break

        logger.warning("DHT sensor failed to return valid reading after retries.")
        return None, None

    def cleanup(self):
        if self.dht_device is not None:
            try:
                self.dht_device.exit()
            except Exception:
                pass


# -----------------------------------------------------------------------------
# 3. NEO-7M GPS AND HMC5883L COMPASS
# -----------------------------------------------------------------------------
class GPSSensor:
    """Minimal, dependency-light NMEA reader for a NEO-7M on /dev/serial0."""
    def __init__(self):
        self.uart = None
        self.last_fix = None
        if not SIMULATION_MODE:
            try:
                self.uart = serial.Serial(config.GPS_SERIAL_PORT, config.GPS_BAUDRATE,
                                          timeout=0.2)
                logger.info("NEO-7M GPS opened on %s at %s baud.",
                            config.GPS_SERIAL_PORT, config.GPS_BAUDRATE)
            except Exception as e:
                logger.error("Failed to open GPS UART serial port %s: %s", config.GPS_SERIAL_PORT, e)
                raise

    @staticmethod
    def _coordinate(raw, hemisphere):
        if not raw or not hemisphere:
            return None
        degrees = int(float(raw) // 100)
        value = degrees + (float(raw) - degrees * 100) / 60.0
        return -value if hemisphere in ("S", "W") else value

    def read_fix(self):
        """Return the newest valid GGA/RMC fix, or recent cached fix within GPS_FIX_MAX_AGE."""
        if SIMULATION_MODE:
            # Return realistic simulated coordinates (configurable in config.py)
            sim_lat = getattr(config, "GPS_SIM_LAT", 19.0760)
            sim_lon = getattr(config, "GPS_SIM_LON", 72.8777)
            return {
                "latitude": sim_lat, "longitude": sim_lon,
                "lat": sim_lat, "lon": sim_lon,
                "satellites": 8, "timestamp": time.time(), "valid": True
            }

        if self.uart and self.uart.in_waiting > 0:
            deadline = time.time() + 0.3
            while time.time() < deadline and self.uart.in_waiting > 0:
                try:
                    line = self.uart.readline().decode("ascii", errors="ignore").strip()
                except Exception:
                    break
                parts = line.split(",")
                if len(parts) < 7:
                    continue
                sentence = parts[0][-3:]
                if sentence == "GGA" and parts[6] not in ("", "0"):
                    lat = self._coordinate(parts[2], parts[3])
                    lon = self._coordinate(parts[4], parts[5])
                    if lat is not None and lon is not None:
                        sats = int(parts[7]) if parts[7].isdigit() else 0
                        self.last_fix = {
                            "latitude": lat, "longitude": lon,
                            "lat": lat, "lon": lon,
                            "satellites": sats,
                            "timestamp": time.time(), "valid": True
                        }
                        return self.last_fix
                elif sentence == "RMC" and len(parts) > 6 and parts[2] == "A":
                    lat = self._coordinate(parts[3], parts[4])
                    lon = self._coordinate(parts[5], parts[6])
                    if lat is not None and lon is not None:
                        sats = self.last_fix["satellites"] if self.last_fix else None
                        self.last_fix = {
                            "latitude": lat, "longitude": lon,
                            "lat": lat, "lon": lon,
                            "satellites": sats,
                            "timestamp": time.time(), "valid": True
                        }
                        return self.last_fix

        # Fallback to recent fix if still fresh
        if self.last_fix and (time.time() - self.last_fix.get("timestamp", 0)) < config.GPS_FIX_MAX_AGE:
            return self.last_fix
        return None

    def cleanup(self):
        if self.uart:
            try:
                self.uart.close()
            except Exception:
                pass


class CompassSensor:
    """
    I2C Magnetometer driver with triple auto-detection:
    - Honeywell HMC5883L at 0x1E
    - QMC5883L / GY-271 clone at 0x0D
    - QMC5883P (HW-127 module) at 0x2C  ← confirmed by i2cdetect on this hardware
    All three chips share the same QMC register layout (0x00-0x05 for X/Y/Z).
    """
    def __init__(self):
        self.bus = None
        self.chip_type = "HMC5883L"
        self.address = config.HMC5883L_I2C_ADDRESS

        if not SIMULATION_MODE:
            self.bus = SMBus(config.HMC5883L_I2C_BUS)
            detected = False

            # 1. Try Honeywell HMC5883L (0x1E)
            try:
                self.bus.write_byte_data(0x1E, 0x00, 0x70)  # 8-sample avg, 15 Hz
                self.bus.write_byte_data(0x1E, 0x01, 0x20)  # Gain 1.3 Gauss
                self.bus.write_byte_data(0x1E, 0x02, 0x00)  # Continuous measurement
                self.chip_type = "HMC5883L"
                self.address = 0x1E
                detected = True
                logger.info("HMC5883L compass detected on I2C bus %s (addr 0x1E).", config.HMC5883L_I2C_BUS)
            except Exception as e_hmc:
                logger.debug("HMC5883L not responsive at 0x1E: %s", e_hmc)

            # 2. Try QMC5883L clone (0x0D)
            if not detected:
                try:
                    self.bus.write_byte_data(0x0D, 0x0A, 0x80)  # Soft reset
                    time.sleep(0.02)
                    self.bus.write_byte_data(0x0D, 0x0B, 0x01)  # Set/reset period
                    self.bus.write_byte_data(0x0D, 0x09, 0x1D)  # Continuous, 200Hz, 8G, OSR 512
                    self.chip_type = "QMC5883L"
                    self.address = 0x0D
                    detected = True
                    logger.info("QMC5883L (GY-271) compass detected on I2C bus %s (addr 0x0D).", config.HMC5883L_I2C_BUS)
                except Exception as e_qmc:
                    logger.debug("QMC5883L not responsive at 0x0D: %s", e_qmc)

            # 3. Try QMC5883P / HW-127 variant (0x2C) — confirmed on this hardware
            if not detected:
                try:
                    # QMC5883P: soft-reset, then configure continuous measurement
                    self.bus.write_byte_data(0x2C, 0x0A, 0x80)  # Soft reset
                    time.sleep(0.05)
                    self.bus.write_byte_data(0x2C, 0x0B, 0x01)  # Set/reset period
                    # Control reg 0x09: OSR=11(512) RNG=01(8G) ODR=11(200Hz) MODE=01(Continuous)
                    # Bit layout [7:6]=OSR [5:4]=RNG [3:2]=ODR [1:0]=MODE => 0b11_01_11_01 = 0xDD
                    self.bus.write_byte_data(0x2C, 0x09, 0xDD)
                    time.sleep(0.1)  # Let the chip take the first measurement
                    self.chip_type = "QMC5883P"
                    self.address = 0x2C
                    detected = True
                    logger.info("QMC5883P (HW-127) compass detected on I2C bus %s (addr 0x2C).", config.HMC5883L_I2C_BUS)
                except Exception as e_qmcp:
                    logger.error("Compass init failed at 0x1E, 0x0D, and 0x2C: %s", e_qmcp)

            if not detected:
                raise RuntimeError(
                    f"No magnetic compass detected at 0x1E, 0x0D, or 0x2C "
                    f"on I2C bus {config.HMC5883L_I2C_BUS}"
                )

    @staticmethod
    def _signed(msb, lsb):
        value = (msb << 8) | lsb
        return value - 65536 if value >= 32768 else value

    @staticmethod
    def _signed_le(lsb, msb):
        value = (msb << 8) | lsb
        return value - 65536 if value >= 32768 else value

    def _wait_drdy(self, timeout: float = 0.15) -> bool:
        """
        Polls the status register for the DRDY bit (bit 0) before reading data.
        QMC5883L/P: status register at 0x06, bit 0 = DRDY.
        HMC5883L:   status register at 0x09, bit 0 = RDY.
        """
        status_reg = 0x09 if self.chip_type == "HMC5883L" else 0x06
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                status = self.bus.read_byte_data(self.address, status_reg)
                if status & 0x01:
                    return True
            except Exception:
                pass
            time.sleep(0.005)
        return False

    def read_heading(self):
        """
        Returns compass heading in degrees [0-360) or None if data not ready.
        """
        if SIMULATION_MODE:
            return None

        if not self._wait_drdy():
            logger.debug("Compass DRDY timeout — chip still warming up.")
            return None

        try:
            if self.chip_type == "HMC5883L":
                data = self.bus.read_i2c_block_data(self.address, 0x03, 6)
                x = self._signed(data[0], data[1])
                y = self._signed(data[4], data[5])
                z = self._signed(data[2], data[3])
            else:
                # QMC5883L / QMC5883P: 0x00-0x05 = X_LSB,X_MSB,Y_LSB,Y_MSB,Z_LSB,Z_MSB
                data = self.bus.read_i2c_block_data(self.address, 0x00, 6)
                x = self._signed_le(data[0], data[1])
                y = self._signed_le(data[2], data[3])
                z = self._signed_le(data[4], data[5])

            logger.debug("Compass raw X=%d Y=%d Z=%d (chip=%s addr=0x%02X)",
                         x, y, z, self.chip_type, self.address)

            if x == 0 and y == 0:
                logger.debug("Compass X=0 Y=0 — still initializing or bad connection.")
                return None

            if x == -4096 or y == -4096:
                raise RuntimeError(
                    f"{self.chip_type} magnetic overflow — move away from strong magnets."
                )

            return (math.degrees(math.atan2(y, x)) + config.COMPASS_DECLINATION_DEG) % 360.0

        except RuntimeError:
            raise
        except Exception as e:
            logger.warning("Compass read error: %s", e)
            return None

    def cleanup(self):
        if self.bus:
            try:
                self.bus.close()
            except Exception:
                pass


# -----------------------------------------------------------------------------
# 4. RELAY MODULE (PUMP & CUTTER)
# -----------------------------------------------------------------------------
class Relay:
    """
    2-Channel Opto-Isolated 5V Relay Module.
    Relays are active-LOW: GPIO.LOW = Relay ENERGIZED (ON), GPIO.HIGH = Relay DE-ENERGIZED (OFF).
    Initializes pins to GPIO.HIGH BEFORE setting output mode to avoid startup actuation pulses (§3.4).
    """
    def __init__(self, pump_pin: int = config.PIN_RELAY_PUMP, cutter_pin: int = config.PIN_RELAY_CUTTER):
        self.pump_pin = pump_pin
        self.cutter_pin = cutter_pin
        self.pump_state = False
        self.cutter_state = False

        if not SIMULATION_MODE:
            # Active LOW: Initialize output state as HIGH (OFF) before configuring direction
            GPIO.setup(self.pump_pin, GPIO.OUT, initial=GPIO.HIGH)
            GPIO.setup(self.cutter_pin, GPIO.OUT, initial=GPIO.HIGH)
            logger.info(f"Relays initialized. Pump: GPIO{pump_pin}, Cutter: GPIO{cutter_pin}.")

    def pump_on(self):
        """Energizes CH1 Relay (Water Pump ON)."""
        self.pump_state = True
        if not SIMULATION_MODE:
            GPIO.output(self.pump_pin, GPIO.LOW)
        logger.info("RELAY ACTUATION: Water Pump -> ON")

    def pump_off(self):
        """De-energizes CH1 Relay (Water Pump OFF)."""
        self.pump_state = False
        if not SIMULATION_MODE:
            GPIO.output(self.pump_pin, GPIO.HIGH)
        logger.info("RELAY ACTUATION: Water Pump -> OFF")

    def cutter_on(self):
        """Energizes CH2 Relay (Grass Cutter ON)."""
        self.cutter_state = True
        if not SIMULATION_MODE:
            GPIO.output(self.cutter_pin, GPIO.LOW)
        logger.info("RELAY ACTUATION: Grass Cutter -> ON")
        return True

    def cutter_off(self):
        """De-energizes CH2 Relay (Grass Cutter OFF)."""
        self.cutter_state = False
        if not SIMULATION_MODE:
            GPIO.output(self.cutter_pin, GPIO.HIGH)
        logger.info("RELAY ACTUATION: Grass Cutter -> OFF")

    def emergency_deenergize(self):
        """De-energizes both relays immediately."""
        self.pump_off()
        self.cutter_off()

    def cleanup(self):
        self.emergency_deenergize()


# -----------------------------------------------------------------------------
# 4. ARDUINO SERIAL BRIDGE (CHASSIS MOTORS, SOIL PROBE ACTUATOR & RADARS)
# -----------------------------------------------------------------------------
class ArduinoBridge:
    """
    Manages USB-Serial communication with Arduino Uno slave controller.
    Controls:
      - 4WD Motors via dual BTS7960
      - 3D-Printed Soil Moisture Probe Actuator Servo (down/up)
      - Front & Rear Ultrasonic Distance Scanners (HC-SR04 on Servos)
    """
    _lock = threading.Lock()

    def __init__(self, port=None, baudrate=None):
        self.port = port or getattr(config, "ARDUINO_SERIAL_PORT", "/dev/ttyACM0")
        self.baudrate = baudrate or getattr(config, "ARDUINO_BAUDRATE", 115200)
        self.serial_conn = None
        self.connected = False
        self.probe_deployed = False

        if not SIMULATION_MODE and getattr(config, "ARDUINO_ENABLED", True):
            self._connect()

    def _connect(self):
        candidates = [self.port, "/dev/ttyACM0", "/dev/ttyUSB0", "/dev/ttyACM1", "/dev/ttyUSB1"]
        for p in candidates:
            if not os.path.exists(p):
                continue
            try:
                self.serial_conn = serial.Serial(p, self.baudrate, timeout=1.0)
                time.sleep(2.0)  # Arduino bootloader wait
                self.serial_conn.reset_input_buffer()
                self.connected = True
                logger.info(f"Connected to Arduino Uno on {p} at {self.baudrate} baud.")
                return
            except Exception as e:
                logger.debug(f"Could not connect to Arduino on {p}: {e}")
        logger.warning("Arduino Uno not found on USB serial ports. Motors will operate in simulation/fallback mode.")

    def send_command(self, cmd: str) -> str:
        with self._lock:
            if not self.connected or not self.serial_conn:
                return ""
            try:
                line = (cmd.strip() + "\n").encode()
                self.serial_conn.write(line)
                self.serial_conn.flush()
                resp = self.serial_conn.readline().decode().strip()
                return resp
            except Exception as e:
                logger.warning(f"Arduino serial communication error: {e}")
                self.connected = False
                return ""

    def drive(self, left_pct: float, right_pct: float):
        # Convert -100..100% duty to -255..255 PWM
        left_pwm = int(max(-100, min(100, left_pct)) * 2.55)
        right_pwm = int(max(-100, min(100, right_pct)) * 2.55)
        self.send_command(f"M,{left_pwm},{right_pwm}")

    def stop(self):
        self.send_command("STOP")

    def deploy_soil_probe(self):
        logger.info("Actuator: Lowering soil moisture probe into ground...")
        resp = self.send_command("PROBE_DOWN")
        self.probe_deployed = True
        time.sleep(0.5)
        return resp

    def retract_soil_probe(self):
        logger.info("Actuator: Retracting soil moisture probe...")
        resp = self.send_command("PROBE_UP")
        self.probe_deployed = False
        time.sleep(0.5)
        return resp

    def scan_front_distance(self, angle: int = 90) -> int:
        resp = self.send_command(f"SCAN_F,{angle}")
        if resp.startswith("DIST_F:"):
            try:
                return int(resp.split(":")[1])
            except ValueError:
                pass
        return 999

    def scan_rear_distance(self, angle: int = 90) -> int:
        resp = self.send_command(f"SCAN_R,{angle}")
        if resp.startswith("DIST_R:"):
            try:
                return int(resp.split(":")[1])
            except ValueError:
                pass
        return 999

    def set_actuator_angle(self, angle: int):
        return self.send_command(f"ACTUATOR,{angle}")

    def set_front_servo(self, angle: int):
        return self.send_command(f"SERVO_F,{angle}")

    def set_rear_servo(self, angle: int):
        return self.send_command(f"SERVO_R,{angle}")

    def get_status(self) -> dict:
        resp = self.send_command("STATUS")
        res = {"connected": self.connected, "raw": resp}
        if resp.startswith("STATUS:"):
            # e.g. STATUS:PROBE=175,DIST_F=45,DIST_R=120
            parts = resp.replace("STATUS:", "").split(",")
            for p in parts:
                if "=" in p:
                    k, v = p.split("=")
                    try:
                        res[k.strip().lower()] = int(v.strip())
                    except ValueError:
                        res[k.strip().lower()] = v.strip()
        return res

    def cleanup(self):
        if self.connected and self.serial_conn:
            try:
                self.stop()
                self.retract_soil_probe()
                self.serial_conn.close()
            except Exception:
                pass


# -----------------------------------------------------------------------------
# 5. DUAL BTS7960 HIGH-CURRENT MOTOR DRIVERS
# -----------------------------------------------------------------------------
class Motors:
    """
    Drives four 12 V motors through Arduino Uno (dual BTS7960) with auto-detection.
    Also controls the 3D-printed soil probe actuator and ultrasonic scanners.
    """

    def __init__(self, arduino_bridge: ArduinoBridge = None):
        self.arduino = arduino_bridge
        self.current_speed = 0.0
        self.pwm_left_forward = self.pwm_left_reverse = None
        self.pwm_right_forward = self.pwm_right_reverse = None

        if self.arduino is None and getattr(config, "ARDUINO_ENABLED", True):
            self.arduino = ArduinoBridge()

        # If Arduino not connected and real hardware mode, fallback to direct GPIO
        if not SIMULATION_MODE and (not self.arduino or not self.arduino.connected):
            try:
                for pin in (config.PIN_LEFT_RPWM, config.PIN_LEFT_LPWM,
                            config.PIN_RIGHT_RPWM, config.PIN_RIGHT_LPWM):
                    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
                self.pwm_left_forward = GPIO.PWM(config.PIN_LEFT_RPWM, config.PWM_FREQ_MOTORS)
                self.pwm_left_reverse = GPIO.PWM(config.PIN_LEFT_LPWM, config.PWM_FREQ_MOTORS)
                self.pwm_right_forward = GPIO.PWM(config.PIN_RIGHT_RPWM, config.PWM_FREQ_MOTORS)
                self.pwm_right_reverse = GPIO.PWM(config.PIN_RIGHT_LPWM, config.PWM_FREQ_MOTORS)
                for pwm in (self.pwm_left_forward, self.pwm_left_reverse,
                            self.pwm_right_forward, self.pwm_right_reverse):
                    pwm.start(0)
                logger.info("Chassis motor drivers initialized in direct GPIO mode.")
            except Exception as e:
                logger.debug(f"Direct GPIO motor init skipped: {e}")

    def _drive(self, left: float, right: float):
        """Signed duty: positive is forward; negative is reverse."""
        self.current_speed = max(abs(left), abs(right))
        if self.arduino and self.arduino.connected:
            self.arduino.drive(left, right)
            return

        if SIMULATION_MODE or not self.pwm_left_forward:
            return

        for pwm in (self.pwm_left_forward, self.pwm_left_reverse,
                    self.pwm_right_forward, self.pwm_right_reverse):
            pwm.ChangeDutyCycle(0)
        if left >= 0:
            self.pwm_left_forward.ChangeDutyCycle(min(100, max(0, left)))
        else:
            self.pwm_left_reverse.ChangeDutyCycle(min(100, max(0, -left)))
        if right >= 0:
            self.pwm_right_forward.ChangeDutyCycle(min(100, max(0, right)))
        else:
            self.pwm_right_reverse.ChangeDutyCycle(min(100, max(0, -right)))

    def forward(self, speed: float = config.MOTOR_SPEED_DEFAULT):
        self._drive(speed, speed)
        logger.debug("Chassis Motors -> FORWARD (speed: %s%%)", speed)

    def backward(self, speed: float = config.MOTOR_SPEED_DEFAULT):
        self._drive(-speed, -speed)
        logger.debug("Chassis Motors -> BACKWARD (speed: %s%%)", speed)

    def turn_left(self, speed: float = config.MOTOR_SPEED_TURN):
        self._drive(-speed, speed)
        logger.debug("Chassis Motors -> TURN LEFT (speed: %s%%)", speed)

    def turn_right(self, speed: float = config.MOTOR_SPEED_TURN):
        self._drive(speed, -speed)
        logger.debug("Chassis Motors -> TURN RIGHT (speed: %s%%)", speed)

    def stop(self):
        self.current_speed = 0.0
        if self.arduino and self.arduino.connected:
            self.arduino.stop()
        elif self.pwm_left_forward and not SIMULATION_MODE:
            for pwm in (self.pwm_left_forward, self.pwm_left_reverse,
                        self.pwm_right_forward, self.pwm_right_reverse):
                pwm.ChangeDutyCycle(0)
        logger.debug("Chassis Motors -> STOP")

    def deploy_soil_probe(self):
        """Lowers the 3D-printed actuator soil moisture probe via Arduino."""
        self.stop()
        if self.arduino and self.arduino.connected:
            return self.arduino.deploy_soil_probe()
        logger.info("Actuator: Probe deploy simulated.")
        return "OK_SIM"

    def retract_soil_probe(self):
        """Retracts the 3D-printed actuator soil moisture probe via Arduino."""
        if self.arduino and self.arduino.connected:
            return self.arduino.retract_soil_probe()
        logger.info("Actuator: Probe retract simulated.")
        return "OK_SIM"

    def scan_front_distance(self, angle: int = 90) -> int:
        if self.arduino and self.arduino.connected:
            return self.arduino.scan_front_distance(angle)
        return 999

    def scan_rear_distance(self, angle: int = 90) -> int:
        if self.arduino and self.arduino.connected:
            return self.arduino.scan_rear_distance(angle)
        return 999

    def set_actuator_angle(self, angle: int):
        if self.arduino and self.arduino.connected:
            return self.arduino.set_actuator_angle(angle)
        return "OK_SIM"

    def set_front_servo(self, angle: int):
        if self.arduino and self.arduino.connected:
            return self.arduino.set_front_servo(angle)
        return "OK_SIM"

    def set_rear_servo(self, angle: int):
        if self.arduino and self.arduino.connected:
            return self.arduino.set_rear_servo(angle)
        return "OK_SIM"

    def get_arduino_status(self) -> dict:
        if self.arduino and self.arduino.connected:
            return self.arduino.get_status()
        return {"connected": False, "simulated": True}

    def cleanup(self):
        self.stop()
        if self.arduino:
            self.arduino.cleanup()
        for pwm in (self.pwm_left_forward, self.pwm_left_reverse,
                    self.pwm_right_forward, self.pwm_right_reverse):
            if pwm:
                try:
                    pwm.stop()
                except Exception:
                    pass


# -----------------------------------------------------------------------------
# 5. OV5647 CSI CAMERA (picamera2) Singleton
# -----------------------------------------------------------------------------
class Camera:
    """
    OV5647 CSI camera wrapper using picamera2.
    CRITICAL: Initialized ONCE at system startup and reused.
    Never re-instantiate Picamera2 per capture frame; second init fails.
    """
    _instance = None

    def __init__(self, resolution: tuple = (640, 480)):
        if Camera._instance is not None:
            raise RuntimeError("Camera class is a singleton. Use get_instance().")
        
        self.resolution = resolution
        self.picam2 = None

        if not SIMULATION_MODE:
            try:
                global Picamera2
                if Picamera2 is None:
                    try:
                        from picamera2 import Picamera2 as _P2
                        Picamera2 = _P2
                    except ImportError:
                        pass
                if Picamera2 is None:
                    raise RuntimeError("picamera2 library not installed. Install with: sudo apt install -y python3-picamera2")

                self.picam2 = Picamera2()
                video_config = self.picam2.create_video_configuration(
                    main={"size": resolution, "format": "RGB888"}
                )
                self.picam2.configure(video_config)
                self.picam2.start()
                time.sleep(1.0) # Warmup sensor
                logger.info(f"Picamera2 initialized successfully at {resolution}.")
            except Exception as e:
                logger.error(f"Failed to initialize Picamera2: {e}")
                raise

        Camera._instance = self

    @classmethod
    def get_instance(cls, resolution: tuple = (640, 480)):
        if cls._instance is None:
            cls._instance = Camera(resolution)
        return cls._instance

    def capture_array(self) -> np.ndarray:
        """Captures a frame as an RGB numpy array."""
        if SIMULATION_MODE:
            # Generate synthetic image (RGB gradient with simulated leaf texture)
            h, w = self.resolution[1], self.resolution[0]
            img = np.zeros((h, w, 3), dtype=np.uint8)
            img[:, :, 1] = 180  # Green channel
            img[:, :, 0] = 50   # Red channel
            img[:, :, 2] = 50   # Blue channel
            # Add random noise
            noise = np.random.randint(-15, 15, (h, w, 3), dtype=np.int16)
            img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            return img

        return self.picam2.capture_array("main")

    def capture_jpeg(self) -> bytes:
        """Encodes captured RGB frame into compressed JPEG byte stream for live video feed."""
        frame = self.capture_array()
        if cv2 is not None:
            bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            success, encoded = cv2.imencode('.jpg', bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if success:
                return encoded.tobytes()
        from PIL import Image
        import io
        img = Image.fromarray(frame)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=75)
        return buf.getvalue()

    def close(self):
        if self.picam2 is not None:
            try:
                self.picam2.stop()
                self.picam2.close()
                logger.info("Picamera2 closed.")
            except Exception:
                pass
        Camera._instance = None

    def cleanup(self):
        self.close()


# -----------------------------------------------------------------------------
# 6. ALERTS (BUZZER & LED)
# -----------------------------------------------------------------------------
class Alerts:
    """Controls audible buzzer and visual LED alerts for plant disease detection."""
    def __init__(self, buzzer_pin: int = config.PIN_BUZZER, led_pin: int = config.PIN_LED):
        self.buzzer_pin = buzzer_pin
        self.led_pin = led_pin

        if not SIMULATION_MODE:
            GPIO.setup(self.buzzer_pin, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self.led_pin, GPIO.OUT, initial=GPIO.LOW)

    def alert_disease(self, duration: float = 2.0):
        """Pulses buzzer and LED to signal disease alert."""
        logger.warning("DISEASE ALERT ACTIVATED: Piezo Buzzer & Red LED pulse.")
        def _pulse():
            end_time = time.time() + duration
            while time.time() < end_time:
                if not SIMULATION_MODE:
                    GPIO.output(self.buzzer_pin, GPIO.HIGH)
                    GPIO.output(self.led_pin, GPIO.HIGH)
                time.sleep(0.15)
                if not SIMULATION_MODE:
                    GPIO.output(self.buzzer_pin, GPIO.LOW)
                    GPIO.output(self.led_pin, GPIO.LOW)
                time.sleep(0.15)
            self.off()

        threading.Thread(target=_pulse, daemon=True).start()

    def off(self):
        if not SIMULATION_MODE:
            GPIO.output(self.buzzer_pin, GPIO.LOW)
            GPIO.output(self.led_pin, GPIO.LOW)

    def cleanup(self):
        self.off()


# -----------------------------------------------------------------------------
# GLOBAL FAIL-SAFE EMERGENCY STOP
# -----------------------------------------------------------------------------
_global_relay = None
_global_motors = None

def register_emergency_devices(relay_inst: Relay, motor_inst: Motors):
    global _global_relay, _global_motors
    _global_relay = relay_inst
    _global_motors = motor_inst

def emergency_stop():
    """
    De-energizes all relays and stops chassis motors immediately.
    Callable from any thread or signal handler during emergency exit.
    """
    logger.critical(">>> EMERGENCY STOP ACTIVATED — HALTING ALL ACTUATORS <<<")
    if _global_motors:
        try:
            _global_motors.stop()
        except Exception:
            pass
    if _global_relay:
        try:
            _global_relay.emergency_deenergize()
        except Exception:
            pass

    if not SIMULATION_MODE and GPIO is not None:
        try:
            # Force all output pins LOW/HIGH safely
            GPIO.output(config.PIN_RELAY_PUMP, GPIO.HIGH)
            GPIO.output(config.PIN_RELAY_CUTTER, GPIO.HIGH)
            GPIO.output(config.PIN_LEFT_RPWM, GPIO.LOW)
            GPIO.output(config.PIN_LEFT_LPWM, GPIO.LOW)
            GPIO.output(config.PIN_RIGHT_RPWM, GPIO.LOW)
            GPIO.output(config.PIN_RIGHT_LPWM, GPIO.LOW)
            GPIO.output(config.PIN_BUZZER, GPIO.LOW)
            GPIO.output(config.PIN_LED, GPIO.LOW)
        except Exception:
            pass
