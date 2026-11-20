from app.crypto.envelope import EnvelopeCodec
from app.database.db_manager import Database
from app.receiver.message_processor import MessageProcessor, MessageRejected
import pytest

def test_replay_state_survives_processor_restart(tmp_path):
    db = Database(tmp_path / "test.db")
    codec = EnvelopeCodec(b"12345678", b"a" * 32)
    packet = codec.encode({"device_id": "dev1", "sequence": 1, "timestamp": 1.0})
    MessageProcessor(codec, db).process(packet)
    with pytest.raises(MessageRejected, match="Replay"):
        MessageProcessor(codec, db).process(packet)
