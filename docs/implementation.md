# Implementation notes

`app.crypto` owns encryption, authentication, key provisioning and envelope encoding. `app.devices` models independent software-only devices. `app.communication` transports encrypted envelopes with MQTT QoS 1. `app.receiver` validates, authenticates, applies replay checks and persists accepted readings. `app.database` owns SQLite schema and operations. `app.security` provides local attack demonstrations. `app.performance` measures local crypto processing. The Streamlit dashboard composes these services.

The standalone simulation is useful without Docker or a broker. The MQTT publisher and subscriber use the same configured keys; provision identical keys to all participants. A configured allowlist can be passed to `MessageProcessor` for device registration enforcement.
