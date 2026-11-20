"""Generate readings from a collection of virtual devices."""
from __future__ import annotations

from collections.abc import Iterator
from .virtual_device import VirtualDevice


class SensorSimulator:
    def __init__(self, device_count: int = 3) -> None:
        if device_count < 1:
            raise ValueError("device_count must be at least 1")
        self.devices = [VirtualDevice(f"IOT_DEVICE_{i:03d}", f"Virtual device {i}") for i in range(1, device_count + 1)]

    def readings(self) -> Iterator[dict[str, object]]:
        for device in self.devices:
            if device.active:
                yield device.read_sensors()

    def set_active(self, device_id: str, active: bool) -> None:
        for device in self.devices:
            if device.device_id == device_id:
                device.active = active
                return
        raise KeyError(device_id)
