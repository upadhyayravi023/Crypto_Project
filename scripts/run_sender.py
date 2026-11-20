"""Publish simulated encrypted readings to MQTT."""
from __future__ import annotations
import argparse
import time
from app.core.config import Settings
from app.crypto.envelope import EnvelopeCodec
from app.communication.mqtt_publisher import MqttPublisher
from app.devices.sensor_simulator import SensorSimulator

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--devices", type=int, default=3)
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--count", type=int, default=0, help="0 runs until interrupted")
    args = parser.parse_args()
    cfg = Settings.from_env()
    publisher = MqttPublisher(cfg.broker_host, cfg.broker_port, EnvelopeCodec(cfg.encryption_key, cfg.authentication_key), cfg.topic_prefix, cfg.broker_username, cfg.broker_password, cfg.broker_tls)
    devices = SensorSimulator(args.devices)
    sent = 0
    publisher.connect()
    try:
        while args.count == 0 or sent < args.count:
            for reading in devices.readings():
                publisher.publish(reading)
                sent += 1
                if args.count and sent >= args.count:
                    break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    finally:
        publisher.close()

if __name__ == "__main__":
    main()
