"""Register and control a group of virtual devices."""
from __future__ import annotations
from app.devices.virtual_device import VirtualDevice


class DeviceManager:
    def __init__(self) -> None:
        self._devices: dict[str, VirtualDevice] = {}

    def register(self, device: VirtualDevice) -> None:
        if device.device_id in self._devices:
            raise ValueError(f"device already registered: {device.device_id}")
        self._devices[device.device_id] = device

    def get(self, device_id: str) -> VirtualDevice:
        try:
            return self._devices[device_id]
        except KeyError as exc:
            raise KeyError(f"unknown device: {device_id}") from exc

    def set_active(self, device_id: str, active: bool) -> None:
        self.get(device_id).active = active

    def all(self) -> tuple[VirtualDevice, ...]:
        return tuple(self._devices.values())
