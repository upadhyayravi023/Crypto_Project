"""DES-CBC encryption. DES is obsolete and included only for the assignment."""
from __future__ import annotations

import base64
import json
import secrets
from typing import Any

from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad


class CryptoError(ValueError):
    """Raised for malformed ciphertext or invalid encryption keys."""


class DESEngine:
    BLOCK_SIZE = DES.block_size

    def __init__(self, key: bytes) -> None:
        if len(key) != 8:
            raise CryptoError("DES key must be exactly 8 bytes")
        self._key = bytes(key)

    def encrypt(self, plaintext: bytes) -> tuple[bytes, str]:
        iv = secrets.token_bytes(self.BLOCK_SIZE)
        ciphertext = DES.new(self._key, DES.MODE_CBC, iv).encrypt(pad(plaintext, self.BLOCK_SIZE))
        return iv, base64.b64encode(ciphertext).decode("ascii")

    def decrypt(self, iv: bytes, ciphertext_b64: str) -> bytes:
        if len(iv) != self.BLOCK_SIZE:
            raise CryptoError("IV must be exactly 8 bytes")
        try:
            ciphertext = base64.b64decode(ciphertext_b64, validate=True)
            if not ciphertext or len(ciphertext) % self.BLOCK_SIZE:
                raise CryptoError("Ciphertext has invalid length")
            return unpad(DES.new(self._key, DES.MODE_CBC, iv).decrypt(ciphertext), self.BLOCK_SIZE)
        except CryptoError:
            raise
        except (ValueError, TypeError) as exc:
            raise CryptoError("Ciphertext is invalid or padding is malformed") from exc

    def encrypt_json(self, payload: dict[str, Any]) -> tuple[bytes, str]:
        return self.encrypt(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())

    def decrypt_json(self, iv: bytes, ciphertext_b64: str) -> dict[str, Any]:
        try:
            result = json.loads(self.decrypt(iv, ciphertext_b64))
            if not isinstance(result, dict):
                raise CryptoError("Decrypted JSON must be an object")
            return result
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise CryptoError("Decrypted plaintext is not valid JSON") from exc
