"""Application security event recording facade."""
from app.database.repositories import SecurityEventRepository


class SecurityMonitor:
    def __init__(self, events: SecurityEventRepository) -> None:
        self.events = events

    def record_rejection(self, event_type: str, description: str, device_id: str | None = None,
                         sequence: int | None = None) -> None:
        self.events.record(event_type, description, device_id, sequence, "warning")

    def record_attack(self, name: str, description: str, device_id: str | None = None,
                      sequence: int | None = None, detected: bool = True) -> None:
        self.events.record(f"attack_{name}", description, device_id, sequence, "info" if detected else "error")
