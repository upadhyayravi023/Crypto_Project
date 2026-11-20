from app.crypto.des_engine import DESEngine

def test_des_round_trip_and_fresh_iv():
    engine = DESEngine(b"12345678")
    iv1, ciphertext1 = engine.encrypt(b"sensor data")
    iv2, ciphertext2 = engine.encrypt(b"sensor data")
    assert len(iv1) == len(iv2) == 8
    assert (iv1, ciphertext1) != (iv2, ciphertext2)
    assert engine.decrypt(iv1, ciphertext1) == b"sensor data"

def test_reject_bad_key_and_ciphertext():
    import pytest
    from app.crypto.des_engine import CryptoError
    with pytest.raises(CryptoError):
        DESEngine(b"short")
    with pytest.raises(CryptoError):
        DESEngine(b"12345678").decrypt(b"12345678", "bad!")
