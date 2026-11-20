"""Small repository facade over the SQLite database service."""
from __future__ import annotations
from typing import Any
from app.database.db_manager import Database


class SensorRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def add(self, reading: dict[str, Any]) -> None:
        self.database.add_reading(reading)

    def latest(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.database.rows("sensor_readings", limit)


class SecurityEventRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def record(self, event_type: str, description: str, device_id: str | None = None,
               sequence: int | None = None, severity: str = "warning") -> None:
        self.database.add_event(event_type, description, device_id, sequence, severity)

    def latest(self, limit: int = 100) -> list[dict[str, Any]]:
        return self.database.rows("security_events", limit)
