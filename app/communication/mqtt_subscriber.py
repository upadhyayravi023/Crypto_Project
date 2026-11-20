"""Subscribe to authorized device topics and feed packets into the processor."""
from __future__ import annotations

import json
import logging
from collections.abc import Callable
from app.receiver.message_processor import MessageProcessor
from .mqtt_client import create_client

logger = logging.getLogger(__name__)


class MqttSubscriber:
    def __init__(self, host: str, port: int, processor: MessageProcessor, topic_prefix: str = "iot",
                 username: str | None = None, password: str | None = None,
                 on_reading: Callable[[dict], None] | None = None, tls: bool = False) -> None:
        self.host, self.port, self.processor = host, port, processor
        self.topic_prefix = topic_prefix.strip("/")
        self.on_reading = on_reading
        self.client = create_client("iot-receiver", username, password, tls)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, reason_code, properties=None) -> None:
        if int(reason_code) == 0:
            client.subscribe(f"{self.topic_prefix}/devices/+/data", qos=1)
        else:
            logger.error("MQTT connection failed reason=%s", reason_code)

    def _on_message(self, client, userdata, message) -> None:
        try:
            envelope = json.loads(message.payload.decode("utf-8"))
            reading = self.processor.process(envelope)
            if self.on_reading:
                self.on_reading(reading)
        except Exception:
            logger.exception("MQTT message rejected topic=%s", message.topic)

    def start(self) -> None:
        self.client.connect_async(self.host, self.port, keepalive=60)
        self.client.loop_start()

    def close(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()
