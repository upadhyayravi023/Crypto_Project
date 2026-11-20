"""Creates authenticated encrypted protocol envelopes."""
from __future__ import annotations

import base64
from typing import Any

from .des_engine import DESEngine
from .message_auth import MessageAuthenticator


class EnvelopeCodec:
    VERSION = 1

    def __init__(self, encryption_key: bytes, authentication_key: bytes) -> None:
        self._cipher = DESEngine(encryption_key)
        self._auth = MessageAuthenticator(authentication_key)

    def encode(self, payload: dict[str, Any]) -> dict[str, Any]:
        device_id, sequence = payload.get("device_id"), payload.get("sequence")
        if not isinstance(device_id, str) or not device_id or not isinstance(sequence, int) or sequence < 1:
            raise ValueError("payload requires a device_id and positive integer sequence")
        iv, ciphertext = self._cipher.encrypt_json(payload)
        envelope: dict[str, Any] = {
            "version": self.VERSION,
            "algorithm": "DES-CBC+HMAC-SHA256",
            "device_id": device_id,
            "sequence": sequence,
            "iv": base64.b64encode(iv).decode("ascii"),
            "ciphertext": ciphertext,
        }
        envelope["hmac_sha256"] = self._auth.sign(envelope)
        return envelope

    def verify(self, envelope: dict[str, Any]) -> bool:
        return self._auth.verify(envelope)

    def decode_verified(self, envelope: dict[str, Any]) -> dict[str, Any]:
        """Decrypt only after the caller has verified the HMAC."""
        iv = base64.b64decode(envelope["iv"], validate=True)
        return self._cipher.decrypt_json(iv, envelope["ciphertext"])
