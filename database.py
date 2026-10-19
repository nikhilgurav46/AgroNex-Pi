#!/usr/bin/env python3
"""
AgroNex-Pi: Database Manager (§5.6)

Handles SQLite storage using WAL (Write-Ahead Logging) mode.
Guarantees thread-safe access and autoincrements primary key IDs.
"""

import os
import sqlite3
import datetime
import logging
import threading

import config

logger = logging.getLogger("AgroNex.Database")
_db_lock = threading.Lock()

class DatabaseManager:
    def __init__(self, db_path: str = config.DB_PATH):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes tables, indexes, and enables WAL mode."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with _db_lock, self.get_connection() as conn:
            cursor = conn.cursor()
            # Enable WAL mode for high concurrency
            cursor.execute("PRAGMA journal_mode=WAL;")

            # 1. Sensor Telemetry Log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    soil_moisture REAL,
                    temperature REAL,
                    humidity REAL,
                    pump_state INTEGER NOT NULL,
                    cutter_state INTEGER NOT NULL,
                    simulated INTEGER DEFAULT 0
                );
            """)

            # 2. Irrigation Events Log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS irrigation_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    duration_s REAL NOT NULL,
                    moisture_start REAL,
                    moisture_end REAL,
                    trigger_type TEXT NOT NULL,
                    simulated INTEGER DEFAULT 0
                );
            """)

            # 3. Disease Classification Log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS disease_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    label TEXT NOT NULL,
                    common_name TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    image_path TEXT NOT NULL,
                    quality_flag TEXT NOT NULL,
                    simulated INTEGER DEFAULT 0
                );
            """)

            # 4. System Events & Audit Log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    simulated INTEGER DEFAULT 0
                );
            """)

            # 5. Verified User Authentication Table (§5.8)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT DEFAULT 'farmer',
                    is_verified INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL
                );
            """)

            # Performance Indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensor_time ON sensor_log(timestamp);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_disease_time ON disease_log(timestamp);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_time ON system_events(timestamp);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")

            # Seed default verified admin user
            admin_check = cursor.execute("SELECT id FROM users WHERE username = 'admin';").fetchone()
            if not admin_check:
                import hashlib
                default_pw_hash = hashlib.sha256("agronex2026".encode("utf-8")).hexdigest()
                now_str = datetime.datetime.now().isoformat()
                cursor.execute("""
                    INSERT INTO users (username, password_hash, full_name, role, is_verified, created_at)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, ("admin", default_pw_hash, "AgroNex Farm Admin", "admin", 1, now_str))

            conn.commit()
            logger.info(f"Database initialized at '{self.db_path}' with WAL mode.")

    def log_sensor_data(self, soil_pct: float, temp: float, hum: float, pump: bool, cutter: bool, simulated: bool = False):
        now = datetime.datetime.now().isoformat()
        with _db_lock, self.get_connection() as conn:
            conn.execute("""
                INSERT INTO sensor_log (timestamp, soil_moisture, temperature, humidity, pump_state, cutter_state, simulated)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (now, soil_pct, temp, hum, int(pump), int(cutter), int(simulated)))
            conn.commit()

    def log_irrigation_event(self, start_t: str, end_t: str, duration: float = 0.0, start_moist: float = 0.0, end_moist: float = 0.0, trigger: str = "", simulated: bool = False, duration_s: float = None):
        dur = duration_s if duration_s is not None else duration
        with _db_lock, self.get_connection() as conn:
            conn.execute("""
                INSERT INTO irrigation_events (start_time, end_time, duration_s, moisture_start, moisture_end, trigger_type, simulated)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (start_t, end_t, dur, start_moist, end_moist, trigger, int(simulated)))
            conn.commit()

    def log_disease_scan(self, label: str, common_name: str, confidence: float, image_path: str, quality_flag: str, simulated: bool = False):
        now = datetime.datetime.now().isoformat()
        with _db_lock, self.get_connection() as conn:
            conn.execute("""
                INSERT INTO disease_log (timestamp, label, common_name, confidence, image_path, quality_flag, simulated)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (now, label, common_name, confidence, image_path, quality_flag, int(simulated)))
            conn.commit()

    def log_system_event(self, event_type: str, severity: str, message: str, simulated: bool = False):
        now = datetime.datetime.now().isoformat()
        with _db_lock, self.get_connection() as conn:
            conn.execute("""
                INSERT INTO system_events (timestamp, event_type, severity, message, simulated)
                VALUES (?, ?, ?, ?, ?);
            """, (now, event_type, severity, message, int(simulated)))
            conn.commit()

    def get_latest_sensor_reading(self) -> dict:
        with _db_lock, self.get_connection() as conn:
            row = conn.execute("SELECT * FROM sensor_log ORDER BY id DESC LIMIT 1;").fetchone()
            if row:
                return dict(row)
            return {
                "soil_moisture": None,
                "temperature": None,
                "humidity": None,
                "pump_state": 0,
                "cutter_state": 0,
                "timestamp": datetime.datetime.now().isoformat()
            }

    def get_sensor_history(self, limit: int = 50) -> list:
        with _db_lock, self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM sensor_log ORDER BY id DESC LIMIT ?;", (limit,)).fetchall()
            return [dict(r) for r in reversed(rows)]

    def get_irrigation_history(self, limit: int = 20) -> list:
        with _db_lock, self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM irrigation_events ORDER BY id DESC LIMIT ?;", (limit,)).fetchall()
            return [dict(r) for r in rows]

    def get_disease_history(self, limit: int = 20) -> list:
        with _db_lock, self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM disease_log ORDER BY id DESC LIMIT ?;", (limit,)).fetchall()
            return [dict(r) for r in rows]

    # -------------------------------------------------------------------------
    # Verified User Management (§5.8)
    # -------------------------------------------------------------------------
    def register_user(self, username: str, password: str, full_name: str, verification_key: str, role: str = "farmer") -> tuple:
        """Registers a verified user. Requires matching verification key."""
        username = username.strip().lower()
        full_name = full_name.strip()
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters."
        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters."
        if verification_key.strip() != config.FARMER_VERIFICATION_KEY:
            return False, "Invalid Farmer Verification Key. Please obtain the key from the farm administrator."

        import hashlib
        pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        now_str = datetime.datetime.now().isoformat()

        try:
            with _db_lock, self.get_connection() as conn:
                existing = conn.execute("SELECT id FROM users WHERE username = ?;", (username,)).fetchone()
                if existing:
                    return False, "Username is already registered."
                conn.execute("""
                    INSERT INTO users (username, password_hash, full_name, role, is_verified, created_at)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (username, pw_hash, full_name or username, role, 1, now_str))
                conn.commit()
            return True, "User registered successfully."
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return False, f"Registration failed: {str(e)}"

    def authenticate_user(self, username: str, password: str) -> tuple:
        """Authenticates user against hashed password."""
        username = username.strip().lower()
        if not username or not password:
            return False, "Username and password required.", None

        import hashlib
        pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

        try:
            with _db_lock, self.get_connection() as conn:
                user = conn.execute("SELECT id, username, full_name, role, is_verified, created_at FROM users WHERE username = ? AND password_hash = ?;", (username, pw_hash)).fetchone()
                if user:
                    user_dict = dict(user)
                    return True, "Login successful.", user_dict
                return False, "Invalid username or password.", None
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return False, f"Authentication error: {str(e)}", None

    def get_user_by_username(self, username: str) -> dict:
        """Retrieves user public profile."""
        username = username.strip().lower()
        try:
            with _db_lock, self.get_connection() as conn:
                row = conn.execute("SELECT id, username, full_name, role, is_verified, created_at FROM users WHERE username = ?;", (username,)).fetchone()
                return dict(row) if row else None
        except Exception:
            return None
