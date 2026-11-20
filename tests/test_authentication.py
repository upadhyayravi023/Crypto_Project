from app.crypto.envelope import EnvelopeCodec

def test_authentication_covers_metadata_and_ciphertext():
    codec = EnvelopeCodec(b"12345678", b"a" * 32)
    packet = codec.encode({"device_id": "dev1", "sequence": 1, "temperature": 20})
    assert codec.verify(packet)
    packet["sequence"] = 2
    assert not codec.verify(packet)
