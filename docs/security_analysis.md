# Security analysis

DES is a 56-bit effective-key block cipher. CBC chains each plaintext block with the preceding ciphertext block and requires an unpredictable fresh 8-byte IV. PKCS7 padding fills the final block. This project authenticates protocol metadata and ciphertext with HMAC-SHA256 using a separate key and constant-time comparison. The receiver verifies HMAC before decryption. Per-device monotonically increasing sequence numbers are persisted so QoS 1 duplicates and stale packets are rejected after restarts.

MQTT transports the encrypted application envelope; broker credentials and topic ACLs are a separate access-control layer. The example Mosquitto setup enables username/password authentication and an ACL. DES is obsolete and unsuitable for real security. CBC plus a separate HMAC is an academic construction; AES-GCM is recommended for production, with managed keys, rotation, TLS, and device-specific credentials.
