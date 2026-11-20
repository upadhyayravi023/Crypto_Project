"""FastAPI backend: MQTT receiver, authenticated dashboard API, and SQLite/Postgres storage."""
from __future__ import annotations

import hmac
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from app.communication.mqtt_subscriber import MqttSubscriber
from app.core.config import Settings
from app.crypto.envelope import EnvelopeCodec
from app.database.db_manager import Database
from app.performance.benchmark import run_benchmark
from app.receiver.message_processor import MessageProcessor
from app.security.attack_simulator import AttackSimulator
from app.devices.virtual_device import VirtualDevice


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings = Settings.from_env()
    database_url = os.getenv("DATABASE_URL")
    database = Database(database_url or settings.database_path)
    codec = EnvelopeCodec(settings.encryption_key, settings.authentication_key)
    processor = MessageProcessor(codec, database)
    subscriber = None
    if os.getenv("MQTT_ENABLED", "false").lower() in {"1", "true", "yes", "on"}:
        subscriber = MqttSubscriber(settings.broker_host, settings.broker_port, processor,
                                    settings.topic_prefix, settings.broker_username,
                                    settings.broker_password, tls=settings.broker_tls)
        subscriber.start()
    application.state.settings = settings
    application.state.database = database
    application.state.codec = codec
    application.state.processor = processor
    application.state.subscriber = subscriber
    try:
        yield
    finally:
        if subscriber:
            subscriber.close()


app = FastAPI(title="DES IoT Receiver API", version="1.0.0", lifespan=lifespan)


def require_api_token(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("IOT_API_TOKEN", "")
    supplied = authorization.removeprefix("Bearer ") if authorization else ""
    if not expected or not hmac.compare_digest(expected, supplied):
        raise HTTPException(status_code=401, detail="Invalid API token")


class DeviceRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=128)
    device_name: str = Field(default="Virtual device", max_length=128)


class AttackRequest(DeviceRequest):
    attack: str = Field(pattern="^(eavesdropping|replay|tampering|injection|modification)$")


class BenchmarkRequest(BaseModel):
    iterations: int = Field(default=100, ge=1, le=10000)
    payload_bytes: int = Field(default=256, ge=1, le=100000)


@app.get("/health")
def health() -> dict[str, Any]:
    subscriber = getattr(app.state, "subscriber", None)
    return {"ok": True, "mqtt_enabled": subscriber is not None}


@app.get("/api/readings", dependencies=[Depends(require_api_token)])
def readings(limit: int = 500) -> list[dict[str, Any]]:
    return app.state.database.rows("sensor_readings", max(1, min(limit, 1000)))


@app.get("/api/events", dependencies=[Depends(require_api_token)])
def events(limit: int = 500) -> list[dict[str, Any]]:
    return app.state.database.rows("security_events", max(1, min(limit, 1000)))


@app.get("/api/metrics", dependencies=[Depends(require_api_token)])
def metrics(limit: int = 500) -> list[dict[str, Any]]:
    return app.state.database.rows("performance_metrics", max(1, min(limit, 1000)))


@app.post("/api/simulate", dependencies=[Depends(require_api_token)])
def simulate(request: DeviceRequest) -> dict[str, Any]:
    database = app.state.database
    device = VirtualDevice(request.device_id, request.device_name)
    device.sequence = database.last_sequence(request.device_id)
    reading = device.read_sensors()
    packet = app.state.codec.encode(reading)
    accepted = app.state.processor.process(packet)
    preview = {key: value for key, value in packet.items() if key != "hmac_sha256"}
    return {"reading": accepted, "encrypted_envelope": preview}


@app.post("/api/attacks", dependencies=[Depends(require_api_token)])
def attack(request: AttackRequest) -> dict[str, Any]:
    database = app.state.database
    device = VirtualDevice(request.device_id, request.device_name)
    device.sequence = database.last_sequence(request.device_id)
    envelope = app.state.codec.encode(device.read_sensors())
    if request.attack == "replay":
        app.state.processor.process(envelope)
    return AttackSimulator(app.state.codec, app.state.processor, database).run(request.attack, envelope)


@app.post("/api/benchmark", dependencies=[Depends(require_api_token)])
def benchmark(request: BenchmarkRequest) -> dict[str, Any]:
    import time
    result = run_benchmark(app.state.codec, request.iterations, request.payload_bytes)
    for metric in ("encryption", "authenticated_decryption"):
        app.state.database.add_metric(metric, result[metric]["average_ms"], time.time())
    return result
