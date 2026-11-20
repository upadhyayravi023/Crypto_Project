"""SQLite persistence for sensor readings, replay state and security events."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class Database:
    def __init__(self, path: str | Path = "data/iot.db") -> None:
        self.path = Path(path)
        if str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.path), timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY, device_id TEXT NOT NULL, sequence INTEGER NOT NULL,
                    timestamp REAL NOT NULL, temperature REAL, humidity REAL, battery INTEGER,
                    status TEXT, UNIQUE(device_id, sequence)
                );
                CREATE TABLE IF NOT EXISTS replay_state (
                    device_id TEXT PRIMARY KEY, last_sequence INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY, timestamp REAL NOT NULL, device_id TEXT,
                    event_type TEXT NOT NULL, severity TEXT NOT NULL, description TEXT NOT NULL,
                    sequence INTEGER
                );
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY, timestamp REAL NOT NULL, metric TEXT NOT NULL, value REAL NOT NULL
                );
            """)

    def last_sequence(self, device_id: str) -> int:
        with self.connect() as db:
            row = db.execute("SELECT last_sequence FROM replay_state WHERE device_id=?", (device_id,)).fetchone()
            return int(row[0]) if row else 0

    def accept_sequence(self, device_id: str, sequence: int) -> bool:
        """Atomically persist only strictly increasing authenticated sequence numbers."""
        with self.connect() as db:
            row = db.execute("SELECT last_sequence FROM replay_state WHERE device_id=?", (device_id,)).fetchone()
            if row and sequence <= int(row[0]):
                return False
            db.execute("INSERT INTO replay_state(device_id,last_sequence) VALUES(?,?) "
                       "ON CONFLICT(device_id) DO UPDATE SET last_sequence=excluded.last_sequence",
                       (device_id, sequence))
            return True

    def add_reading(self, reading: dict[str, Any]) -> None:
        with self.connect() as db:
            db.execute("INSERT INTO sensor_readings(device_id,sequence,timestamp,temperature,humidity,battery,status) "
                       "VALUES(?,?,?,?,?,?,?)",
                       (reading["device_id"], reading["sequence"], reading["timestamp"], reading.get("temperature"),
                        reading.get("humidity"), reading.get("battery"), reading.get("status", "online")))

    def add_event(self, event_type: str, description: str, device_id: str | None = None,
                  sequence: int | None = None, severity: str = "warning", timestamp: float | None = None) -> None:
        import time
        with self.connect() as db:
            db.execute("INSERT INTO security_events(timestamp,device_id,event_type,severity,description,sequence) "
                       "VALUES(?,?,?,?,?,?)", (timestamp or time.time(), device_id, event_type, severity, description, sequence))

    def add_metric(self, metric: str, value: float, timestamp: float) -> None:
        with self.connect() as db:
            db.execute("INSERT INTO performance_metrics(timestamp,metric,value) VALUES(?,?,?)", (timestamp, metric, value))

    def rows(self, table: str, limit: int = 500) -> list[dict[str, Any]]:
        if table not in {"sensor_readings", "security_events", "performance_metrics"}:
            raise ValueError("unsupported table")
        with self.connect() as db:
            return [dict(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,))]
