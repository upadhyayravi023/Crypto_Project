"""Key provisioning helpers; secrets are never logged or serialized by this class."""
from __future__ import annotations

import base64
import secrets


class KeyManager:
    @staticmethod
    def generate() -> tuple[bytes, bytes]:
        return secrets.token_bytes(8), secrets.token_bytes(32)

    @staticmethod
    def to_env_value(key: bytes) -> str:
        return base64.b64encode(key).decode("ascii")
