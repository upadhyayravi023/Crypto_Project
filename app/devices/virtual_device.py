"""A virtual sensor device with an independent monotonic sequence counter."""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field


@dataclass
class VirtualDevice:
    device_id: str
    name: str
    sequence: int = 0
    active: bool = True
    _rng: random.Random = field(default_factory=random.Random, repr=False)

    def read_sensors(self) -> dict[str, object]:
        if not self.active:
            raise RuntimeError(f"Device {self.device_id} is stopped")
        self.sequence += 1
        return {
            "device_id": self.device_id,
            "device_name": self.name,
            "temperature": round(self._rng.uniform(18.0, 35.0), 1),
            "humidity": round(self._rng.uniform(25.0, 85.0), 1),
            "battery": self._rng.randint(20, 100),
            "timestamp": time.time(),
            "sequence": self.sequence,
            "status": "online",
        }
