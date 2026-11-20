"""Streamlit monitoring and local security demonstration dashboard."""
from __future__ import annotations
import sys
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import pandas as pd
import streamlit as st
from app.core.config import Settings
from app.crypto.envelope import EnvelopeCodec
from app.database.db_manager import Database
from app.devices.virtual_device import VirtualDevice
from app.performance.benchmark import run_benchmark
from app.receiver.message_processor import MessageProcessor, MessageRejected
from app.security.attack_simulator import AttackSimulator
from app.dashboard.backend_client import BackendClient

@st.cache_resource
def services():
    api_url = os.getenv("IOT_API_URL", "").strip()
    if api_url:
        return BackendClient(api_url, os.getenv("IOT_API_TOKEN", "")), None, None, None
    settings = Settings.from_env()
    db = Database(settings.database_path)
    codec = EnvelopeCodec(settings.encryption_key, settings.authentication_key)
    return None, db, codec, MessageProcessor(codec, db)

st.set_page_config(page_title="DES IoT Security", page_icon="🔐", layout="wide")
st.title("DES Based Secure Communication for IoT")
st.caption("Virtual device monitoring, message authentication, replay protection, and performance measurements.")
backend, db, codec, processor = services()
try:
    readings = backend.rows("sensor_readings") if backend else db.rows("sensor_readings")
    events = backend.rows("security_events") if backend else db.rows("security_events")
except Exception as exc:
    readings, events = [], []
    st.error(f"Backend is not responding: {exc}")
a, b, c, d = st.columns(4)
a.metric("Stored readings", len(readings))
b.metric("Security events", len(events))
c.metric("Known devices", len({row["device_id"] for row in readings}))
d.metric("Rejected / attack events", sum(1 for row in events if row["severity"] in {"warning", "error"}))
overview, devices, attacks, performance, logs, config = st.tabs(["Overview", "Virtual devices", "Attack simulation", "Performance", "Security events", "Configuration"])
with overview:
    if readings:
        df = pd.DataFrame(readings).sort_values("timestamp")
        st.subheader("Latest authenticated readings")
        st.dataframe(df.tail(50), use_container_width=True, hide_index=True)
        st.line_chart(df.pivot_table(index="timestamp", columns="device_id", values="temperature", aggfunc="last"))
    else:
        st.info("No readings yet. Generate a reading in Virtual devices.")
with devices:
    device_id = st.text_input("Device ID", "IOT_DEVICE_001")
    device_name = st.text_input("Device name", "Virtual device 1")
    if st.button("Generate and securely receive a reading"):
        try:
            if backend:
                response = backend.simulate(device_id, device_name)
                preview = response["encrypted_envelope"]
            else:
                device = VirtualDevice(device_id, device_name)
                device.sequence = db.last_sequence(device_id)
                packet = codec.encode(device.read_sensors())
                processor.process(packet)
                preview = {k: v for k, v in packet.items() if k != "hmac_sha256"}
            st.success("Message authenticated, decrypted, and stored.")
            st.json(preview)
        except Exception as exc:
            st.error(str(exc))
        st.rerun()
with attacks:
    st.write("Simulations run against the local message processor. Eavesdropping displays the encrypted envelope only.")
    target = st.text_input("Target device", "ATTACK_TEST_DEVICE")
    attack_type = st.selectbox("Attack", ["eavesdropping", "replay", "tampering", "injection", "modification"])
    if st.button("Run simulation"):
        try:
            if backend:
                result = backend.attack(attack_type, target)
            else:
                device = VirtualDevice(target, "Attack test")
                device.sequence = db.last_sequence(target)
                envelope = codec.encode(device.read_sensors())
                if attack_type == "replay":
                    processor.process(envelope)
                result = AttackSimulator(codec, processor, db).run(attack_type, envelope)
            st.write(f"Expected: {result['expected_outcome']}")
            st.write(f"Actual: {result['actual_outcome']} · Detected: {result['detected']}")
            if attack_type == "eavesdropping":
                packet = result.get("payload", result.get("encrypted_envelope", {}))
                st.json({k: v for k, v in packet.items() if k != "hmac_sha256"})
            st.rerun()
        except Exception as exc:
            st.error(str(exc))
with performance:
    iterations = st.number_input("Iterations", min_value=1, max_value=10000, value=100)
    size = st.number_input("Payload data bytes", min_value=1, max_value=100000, value=256)
    if st.button("Run benchmark"):
        try:
            if backend:
                result = backend.benchmark(int(iterations), int(size))
            else:
                result = run_benchmark(codec, int(iterations), int(size))
                import time
                for name in ("encryption", "authenticated_decryption"):
                    db.add_metric(name, result[name]["average_ms"], time.time())
            st.json(result)
        except Exception as exc:
            st.error(str(exc))
    metrics = backend.rows("performance_metrics") if backend else db.rows("performance_metrics")
    if metrics:
        st.dataframe(pd.DataFrame(metrics), use_container_width=True, hide_index=True)
with logs:
    events = backend.rows("security_events") if backend else db.rows("security_events")
    if events:
        st.dataframe(pd.DataFrame(events), use_container_width=True, hide_index=True)
    else:
        st.info("No security events recorded.")
with config:
    settings = Settings.from_env()
    if backend:
        st.write({"Backend API": os.getenv("IOT_API_URL"), "Backend health": backend.health(),
                  "MQTT": "Receiver managed by backend", "Encryption": "DES-CBC with PKCS7",
                  "Authentication": "HMAC-SHA256"})
    else:
        st.write({"MQTT host": settings.broker_host, "MQTT port": settings.broker_port,
                  "MQTT TLS": settings.broker_tls, "Topic prefix": settings.topic_prefix,
                  "Database": str(settings.database_path), "Encryption": "DES-CBC with PKCS7",
                  "Authentication": "HMAC-SHA256"})
    st.warning("DES is cryptographically obsolete and is used only because this is an academic requirement. Use AES-GCM in production.")
