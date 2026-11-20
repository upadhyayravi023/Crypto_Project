"""SQLite persistence for sensor readings, replay state and security events."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any


class Database:
    def __init__(self, path: str | Path = "data/iot.db") -> None:
        raw_path = str(path)
        self.database_url = raw_path if raw_path.startswith(("postgres://", "postgresql://")) else os.getenv("DATABASE_URL")
        self.path = Path("data/iot.db") if self.database_url else Path(path)
        if not self.database_url and str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self):
        if self.database_url:
            import psycopg
            from psycopg.rows import dict_row
            return psycopg.connect(self.database_url, row_factory=dict_row)
        connection = sqlite3.connect(str(self.path), timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _execute(self, connection, statement: str, parameters: tuple = ()):
        if self.database_url:
            statement = statement.replace("?", "%s")
        return connection.execute(statement, parameters)

    def _initialize(self) -> None:
        identity = "BIGSERIAL PRIMARY KEY" if self.database_url else "INTEGER PRIMARY KEY"
        real = "DOUBLE PRECISION" if self.database_url else "REAL"
        statements = [
            f"CREATE TABLE IF NOT EXISTS sensor_readings (id {identity}, device_id TEXT NOT NULL, sequence INTEGER NOT NULL, timestamp {real} NOT NULL, temperature {real}, humidity {real}, battery INTEGER, status TEXT, UNIQUE(device_id, sequence))",
            "CREATE TABLE IF NOT EXISTS replay_state (device_id TEXT PRIMARY KEY, last_sequence INTEGER NOT NULL)",
            f"CREATE TABLE IF NOT EXISTS security_events (id {identity}, timestamp {real} NOT NULL, device_id TEXT, event_type TEXT NOT NULL, severity TEXT NOT NULL, description TEXT NOT NULL, sequence INTEGER)",
            f"CREATE TABLE IF NOT EXISTS performance_metrics (id {identity}, timestamp {real} NOT NULL, metric TEXT NOT NULL, value {real} NOT NULL)",
        ]
        with self.connect() as db:
            for statement in statements:
                self._execute(db, statement)

    def last_sequence(self, device_id: str) -> int:
        with self.connect() as db:
            row = self._execute(db, "SELECT last_sequence FROM replay_state WHERE device_id=?", (device_id,)).fetchone()
            return int(row[0]) if row else 0

    def accept_sequence(self, device_id: str, sequence: int) -> bool:
        """Atomically persist only strictly increasing authenticated sequence numbers."""
        with self.connect() as db:
            row = self._execute(db, "SELECT last_sequence FROM replay_state WHERE device_id=?", (device_id,)).fetchone()
            if row and sequence <= int(row[0]):
                return False
            self._execute(db, "INSERT INTO replay_state(device_id,last_sequence) VALUES(?,?) "
                       "ON CONFLICT(device_id) DO UPDATE SET last_sequence=excluded.last_sequence",
                       (device_id, sequence))
            return True

    def add_reading(self, reading: dict[str, Any]) -> None:
        with self.connect() as db:
            self._execute(db, "INSERT INTO sensor_readings(device_id,sequence,timestamp,temperature,humidity,battery,status) "
                       "VALUES(?,?,?,?,?,?,?)",
                       (reading["device_id"], reading["sequence"], reading["timestamp"], reading.get("temperature"),
                        reading.get("humidity"), reading.get("battery"), reading.get("status", "online")))

    def add_event(self, event_type: str, description: str, device_id: str | None = None,
                  sequence: int | None = None, severity: str = "warning", timestamp: float | None = None) -> None:
        import time
        with self.connect() as db:
            self._execute(db, "INSERT INTO security_events(timestamp,device_id,event_type,severity,description,sequence) "
                       "VALUES(?,?,?,?,?,?)", (timestamp or time.time(), device_id, event_type, severity, description, sequence))

    def add_metric(self, metric: str, value: float, timestamp: float) -> None:
        with self.connect() as db:
            self._execute(db, "INSERT INTO performance_metrics(timestamp,metric,value) VALUES(?,?,?)", (timestamp, metric, value))

    def rows(self, table: str, limit: int = 500) -> list[dict[str, Any]]:
        if table not in {"sensor_readings", "security_events", "performance_metrics"}:
            raise ValueError("unsupported table")
        with self.connect() as db:
            rows = self._execute(db, f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in rows]
