"""Performance metric persistence and summary helpers."""
from __future__ import annotations
import time
from app.database.db_manager import Database


class MetricsRecorder:
    def __init__(self, database: Database) -> None:
        self.database = database

    def record(self, name: str, value: float, timestamp: float | None = None) -> None:
        self.database.add_metric(name, value, timestamp or time.time())

    def recent(self, limit: int = 500) -> list[dict]:
        return self.database.rows("performance_metrics", limit)
