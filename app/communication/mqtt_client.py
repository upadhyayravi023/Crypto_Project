"""Paho MQTT client factory with credential support."""
from __future__ import annotations

from typing import Any


def create_client(client_id: str, username: str | None = None, password: str | None = None) -> Any:
    try:
        import paho.mqtt.client as mqtt
    except ImportError as exc:
        raise RuntimeError("Install the 'mqtt' optional dependencies to use MQTT") from exc
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    if username:
        client.username_pw_set(username, password)
    return client
