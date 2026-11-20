"""Run a local sender-to-receiver simulation without MQTT or hardware."""
from __future__ import annotations
import argparse
import json
from app.core.config import Settings
from app.crypto.envelope import EnvelopeCodec
from app.database.db_manager import Database
from app.devices.sensor_simulator import SensorSimulator
from app.receiver.message_processor import MessageProcessor

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--devices", type=int, default=3)
    parser.add_argument("--messages", type=int, default=3, help="readings per device")
    parser.add_argument("--database", default=None)
    args = parser.parse_args()
    settings = Settings.from_env()
    db = Database(args.database or settings.database_path)
    codec = EnvelopeCodec(settings.encryption_key, settings.authentication_key)
    processor = MessageProcessor(codec, db)
    simulator = SensorSimulator(args.devices)
    for device in simulator.devices:
        device.sequence = db.last_sequence(device.device_id)
    for _ in range(args.messages):
        for reading in simulator.readings():
            print(json.dumps(processor.process(codec.encode(reading))))

if __name__ == "__main__":
    main()
