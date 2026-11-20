"""Typed records exchanged by persistence and application services."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SensorReading:
    device_id: str
    sequence: int
    timestamp: float
    temperature: float
    humidity: float
    battery: int
    status: str = "online"


@dataclass(frozen=True)
class SecurityEvent:
    timestamp: float
    event_type: str
    severity: str
    description: str
    device_id: str | None = None
    sequence: int | None = None
