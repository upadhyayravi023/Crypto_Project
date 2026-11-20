"""Validates, authenticates, replay checks and decrypts incoming envelopes."""
from __future__ import annotations

import base64
import logging
import time
from typing import Any

from app.crypto.envelope import EnvelopeCodec
from app.database.db_manager import Database
from .replay_protection import ReplayProtection

logger = logging.getLogger(__name__)


class MessageRejected(ValueError):
    """An incoming message did not meet protocol or security requirements."""


class MessageProcessor:
    REQUIRED = {"version", "algorithm", "device_id", "sequence", "iv", "ciphertext", "hmac_sha256"}

    def __init__(self, codec: EnvelopeCodec, database: Database, authorized_devices: set[str] | None = None) -> None:
        self.codec = codec
        self.database = database
        self.replay = ReplayProtection(database)
        self.authorized_devices = authorized_devices

    def process(self, envelope: dict[str, Any]) -> dict[str, Any]:
        device_id = envelope.get("device_id") if isinstance(envelope, dict) else None
        sequence = envelope.get("sequence") if isinstance(envelope, dict) else None
        if not isinstance(envelope, dict) or not self.REQUIRED.issubset(envelope):
            raise self._reject("malformed_message", "Message schema is invalid", device_id, sequence)
        if (envelope["version"] != EnvelopeCodec.VERSION or envelope["algorithm"] != "DES-CBC+HMAC-SHA256"
                or not isinstance(device_id, str) or not device_id
                or not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1
                or not isinstance(envelope["iv"], str) or not isinstance(envelope["ciphertext"], str)):
            raise self._reject("malformed_message", "Message metadata is invalid", device_id, sequence)
        try:
            iv = base64.b64decode(envelope["iv"], validate=True)
            if len(iv) != 8:
                raise ValueError("invalid IV length")
        except (ValueError, TypeError):
            raise self._reject("malformed_message", "Message IV is invalid", device_id, sequence)
        if self.authorized_devices is not None and device_id not in self.authorized_devices:
            raise self._reject("unauthorized_device", "Device is not registered", device_id, sequence)
        if not self.codec.verify(envelope):
            raise self._reject("authentication_failure", "Message authentication failed", device_id, sequence)
        try:
            reading = self.codec.decode_verified(envelope)
        except (ValueError, KeyError, TypeError) as exc:
            raise self._reject("decryption_failure", "Authenticated message could not be decoded", device_id, sequence) from exc
        if reading.get("device_id") != device_id or reading.get("sequence") != sequence:
            raise self._reject("metadata_mismatch", "Authenticated metadata does not match payload", device_id, sequence)
        if not self.replay.accept(device_id, sequence):
            last = self.database.last_sequence(device_id)
            raise self._reject("replay_detected", f"Replay or stale message rejected; last accepted sequence={last}", device_id, sequence)
        try:
            self.database.add_reading(reading)
        except Exception as exc:
            logger.exception("Could not persist authenticated sensor reading")
            raise self._reject("storage_failure", "Reading could not be stored", device_id, sequence) from exc
        self.database.add_event("message_accepted", "Authenticated sensor message accepted", device_id, sequence, "info")
        return reading

    def _reject(self, event: str, description: str, device_id: Any, sequence: Any) -> MessageRejected:
        logger.warning("Rejected message event=%s device_id=%s sequence=%s", event, device_id, sequence)
        self.database.add_event(event, description, device_id if isinstance(device_id, str) else None,
                                sequence if isinstance(sequence, int) else None, "warning", time.time())
        return MessageRejected(description)
