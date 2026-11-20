"""HTTP client for the separately hosted receiver API."""
from __future__ import annotations

import requests


class BackendClient:
    def __init__(self, base_url: str, api_token: str, timeout: float = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {"Authorization": f"Bearer {api_token}"}

    def health(self) -> dict:
        response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def rows(self, kind: str, limit: int = 500) -> list[dict]:
        endpoints = {"sensor_readings": "readings", "security_events": "events", "performance_metrics": "metrics"}
        if kind not in endpoints:
            raise ValueError("unsupported data type")
        response = requests.get(f"{self.base_url}/api/{endpoints[kind]}", params={"limit": limit},
                                headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def simulate(self, device_id: str, device_name: str) -> dict:
        response = requests.post(f"{self.base_url}/api/simulate", json={"device_id": device_id, "device_name": device_name},
                                 headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def attack(self, name: str, device_id: str) -> dict:
        response = requests.post(f"{self.base_url}/api/attacks", json={"attack": name, "device_id": device_id,
                                 "device_name": "Attack test"}, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def benchmark(self, iterations: int, payload_bytes: int) -> dict:
        response = requests.post(f"{self.base_url}/api/benchmark", json={"iterations": iterations,
                                 "payload_bytes": payload_bytes}, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
