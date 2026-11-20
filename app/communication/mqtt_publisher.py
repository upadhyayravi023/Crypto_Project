"""Publish serialized encrypted envelopes."""
from __future__ import annotations

import json
from app.crypto.envelope import EnvelopeCodec
from .mqtt_client import create_client


class MqttPublisher:
    def __init__(self, host: str, port: int, codec: EnvelopeCodec, topic_prefix: str = "iot",
                 username: str | None = None, password: str | None = None) -> None:
        self.host, self.port, self.codec, self.topic_prefix = host, port, codec, topic_prefix.strip("/")
        self.client = create_client("iot-publisher", username, password)

    def connect(self) -> None:
        self.client.connect(self.host, self.port, keepalive=60)
        self.client.loop_start()

    def publish(self, reading: dict[str, object]) -> dict[str, object]:
        envelope = self.codec.encode(reading)
        topic = f"{self.topic_prefix}/devices/{reading['device_id']}/data"
        result = self.client.publish(topic, json.dumps(envelope, separators=(",", ":")), qos=1)
        result.wait_for_publish()
        return envelope

    def close(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()
