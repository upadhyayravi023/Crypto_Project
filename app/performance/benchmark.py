"""Reproducible local cryptographic microbenchmarks."""
from __future__ import annotations

import statistics
import time
from typing import Any
from app.crypto.envelope import EnvelopeCodec


def run_benchmark(codec: EnvelopeCodec, iterations: int = 100, payload_bytes: int = 256) -> dict[str, Any]:
    if iterations < 1 or payload_bytes < 1:
        raise ValueError("iterations and payload_bytes must be positive")
    payload = {"device_id": "BENCHMARK", "sequence": 1, "timestamp": time.time(), "data": "x" * payload_bytes}
    enc, dec = [], []
    for seq in range(1, iterations + 1):
        payload["sequence"] = seq
        started = time.perf_counter_ns()
        envelope = codec.encode(payload)
        enc.append((time.perf_counter_ns() - started) / 1e6)
        started = time.perf_counter_ns()
        if not codec.verify(envelope):
            raise RuntimeError("benchmark envelope failed authentication")
        codec.decode_verified(envelope)
        dec.append((time.perf_counter_ns() - started) / 1e6)
    def summary(values):
        return {"average_ms": statistics.mean(values), "minimum_ms": min(values), "maximum_ms": max(values),
                "stddev_ms": statistics.stdev(values) if len(values) > 1 else 0.0}
    return {"iterations": iterations, "payload_bytes": payload_bytes,
            "encryption": summary(enc), "authenticated_decryption": summary(dec),
            "throughput_messages_per_second": 1000 / (statistics.mean(enc) + statistics.mean(dec))}
