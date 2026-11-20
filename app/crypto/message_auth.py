"""HMAC-SHA256 signing and verification for encrypted envelopes."""
from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


class MessageAuthenticator:
    def __init__(self, key: bytes) -> None:
        if len(key) < 32:
            raise ValueError("HMAC key must be at least 32 bytes")
        self._key = bytes(key)

    @staticmethod
    def canonical_bytes(envelope: dict[str, Any]) -> bytes:
        signed = {k: v for k, v in envelope.items() if k != "hmac_sha256"}
        return json.dumps(signed, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def sign(self, envelope: dict[str, Any]) -> str:
        return hmac.new(self._key, self.canonical_bytes(envelope), hashlib.sha256).hexdigest()

    def verify(self, envelope: dict[str, Any]) -> bool:
        supplied = envelope.get("hmac_sha256")
        if not isinstance(supplied, str):
            return False
        return hmac.compare_digest(self.sign(envelope), supplied)
