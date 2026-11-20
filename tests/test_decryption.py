import pytest
from app.crypto.des_engine import DESEngine, CryptoError

def test_invalid_iv_rejected():
    with pytest.raises(CryptoError):
        DESEngine(b"12345678").decrypt(b"bad", "YWJj")
