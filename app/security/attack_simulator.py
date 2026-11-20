"""Application-level attack simulations against authenticated envelopes."""
from __future__ import annotations

import copy
import time
from typing import Any

from app.crypto.envelope import EnvelopeCodec
from app.database.db_manager import Database
from app.receiver.message_processor import MessageProcessor, MessageRejected


class AttackSimulator:
    def __init__(self, codec: EnvelopeCodec, processor: MessageProcessor, database: Database) -> None:
        self.codec, self.processor, self.database = codec, processor, database

    def run(self, attack: str, valid_envelope: dict[str, Any]) -> dict[str, Any]:
        start = time.perf_counter()
        packet = copy.deepcopy(valid_envelope)
        if attack == "replay":
            # A packet must already have been accepted to be a replay.
            try:
                self.processor.process(packet)
            except MessageRejected:
                pass
            expected = "receiver rejects an already accepted sequence"
        elif attack in {"tampering", "injection", "modification"}:
            if attack == "tampering":
                packet["ciphertext"] = ("A" if packet["ciphertext"][0] != "A" else "B") + packet["ciphertext"][1:]
            elif attack == "modification":
                packet["sequence"] += 9
            else:
                packet["hmac_sha256"] = "0" * 64
            expected = "receiver rejects the packet before decryption"
        elif attack == "eavesdropping":
            expected = "interceptor sees ciphertext and metadata, not plaintext"
        else:
            raise ValueError(f"unsupported attack: {attack}")
        rejected, detected = False, False
        try:
            if attack != "eavesdropping":
                self.processor.process(packet)
        except MessageRejected:
            rejected, detected = True, True
        elapsed_ms = (time.perf_counter() - start) * 1000
        outcome = "intercepted_encrypted_payload" if attack == "eavesdropping" else ("rejected" if rejected else "accepted")
        result = {"attack": attack, "execution_ms": elapsed_ms, "target_device": valid_envelope.get("device_id"),
                  "payload": packet, "expected_outcome": expected, "actual_outcome": outcome, "detected": detected}
        self.database.add_event(f"attack_{attack}", f"Attack simulation result: {outcome}", result["target_device"],
                                packet.get("sequence"), "info" if detected or attack == "eavesdropping" else "error")
        return result
