import pytest
from app.crypto.envelope import EnvelopeCodec
from app.database.db_manager import Database
from app.receiver.message_processor import MessageProcessor, MessageRejected

def test_modified_packet_fails_authentication(tmp_path):
    codec = EnvelopeCodec(b"12345678", b"a" * 32)
    db = Database(tmp_path / "test.db")
    packet = codec.encode({"device_id": "dev1", "sequence": 1, "timestamp": 1.0})
    packet["ciphertext"] = "A" + packet["ciphertext"][1:]
    with pytest.raises(MessageRejected, match="authentication"):
        MessageProcessor(codec, db).process(packet)

def test_unregistered_device_rejected(tmp_path):
    codec = EnvelopeCodec(b"12345678", b"a" * 32)
    packet = codec.encode({"device_id": "intruder", "sequence": 1, "timestamp": 1.0})
    with pytest.raises(MessageRejected, match="not registered"):
        MessageProcessor(codec, Database(tmp_path / "test.db"), set()).process(packet)
