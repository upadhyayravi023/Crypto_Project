"""Environment based application configuration."""
from __future__ import annotations

import base64
import os
import secrets
from dataclasses import dataclass
from pathlib import Path


def _key_from_env(name: str, length: int) -> bytes:
    value = os.getenv(name)
    if value:
        try:
            key = base64.b64decode(value, validate=True)
        except Exception as exc:
            raise ValueError(f"{name} must be valid base64") from exc
        if len(key) != length:
            raise ValueError(f"{name} must decode to exactly {length} bytes")
        return key
    return secrets.token_bytes(length)


@dataclass(frozen=True)
class Settings:
    """Runtime settings. For a real deployment, provision stable keys via env."""

    broker_host: str = "localhost"
    broker_port: int = 1883
    broker_username: str | None = None
    broker_password: str | None = None
    broker_tls: bool = False
    topic_prefix: str = "iot"
    database_path: Path = Path("data/iot.db")
    encryption_key: bytes = b""
    authentication_key: bytes = b""

    @classmethod
    def from_env(cls) -> "Settings":
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        return cls(
            broker_host=os.getenv("MQTT_HOST", "localhost"),
            broker_port=int(os.getenv("MQTT_PORT", "1883")),
            broker_username=os.getenv("MQTT_USERNAME") or None,
            broker_password=os.getenv("MQTT_PASSWORD") or None,
            broker_tls=os.getenv("MQTT_TLS", "false").strip().lower() in {"1", "true", "yes", "on"},
            topic_prefix=os.getenv("MQTT_TOPIC_PREFIX", "iot").strip("/"),
            database_path=Path(os.getenv("DATABASE_PATH", "data/iot.db")),
            encryption_key=_key_from_env("DES_KEY_B64", 8),
            authentication_key=_key_from_env("HMAC_KEY_B64", 32),
        )
