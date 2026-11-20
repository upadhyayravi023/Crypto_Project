"""Run the MQTT receiver service."""
from app.core.config import Settings
from app.core.logging_config import configure_logging
from app.crypto.envelope import EnvelopeCodec
from app.database.db_manager import Database
from app.receiver.message_processor import MessageProcessor
from app.communication.mqtt_subscriber import MqttSubscriber

def main() -> None:
    configure_logging()
    cfg = Settings.from_env()
    processor = MessageProcessor(EnvelopeCodec(cfg.encryption_key, cfg.authentication_key), Database(cfg.database_path))
    subscriber = MqttSubscriber(cfg.broker_host, cfg.broker_port, processor, cfg.topic_prefix, cfg.broker_username, cfg.broker_password, tls=cfg.broker_tls)
    subscriber.start()
    try:
        import threading
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        subscriber.close()

if __name__ == "__main__":
    main()
