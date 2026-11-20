# DES Based Secure Communication for IoT Devices

A software-only IoT security simulation. Virtual devices generate sensor readings, encrypt them with DES-CBC, authenticate the full protocol envelope with HMAC-SHA256, and send messages through MQTT or the built-in local simulation. The receiver validates the packet, verifies HMAC before decryption, rejects replayed sequence numbers, and stores accepted readings and security events in SQLite.

> **Academic use only:** DES is cryptographically obsolete. This project demonstrates the required DES mechanisms and must not protect real devices or data. Use a modern AEAD cipher such as AES-GCM for production.

## Objectives and architecture

The implementation demonstrates confidentiality (DES-CBC), integrity and message authentication (separate HMAC-SHA256 key), replay detection (per-device persistent monotonic sequences), MQTT transport at QoS 1, software device simulation, SQLite persistence and measured local crypto performance.

See [architecture](docs/architecture.md), [implementation notes](docs/implementation.md), [security analysis](docs/security_analysis.md) and [performance analysis](docs/performance_analysis.md) for diagrams and details.

## Technology

Python 3.11+, PyCryptodome, Paho MQTT, Eclipse Mosquitto, SQLite, Streamlit, Pandas, Plotly and Pytest.

## Project layout

```text
app/                 configuration, devices, crypto, MQTT, receiver, database, security, performance, dashboard
config/              environment and Mosquitto examples
docs/                architecture and security documentation
scripts/             sender, receiver, local simulation and benchmark entry points
tests/               cryptography, replay, MQTT, security and performance tests
Dockerfile           dashboard/application image
docker-compose.yml   broker, receiver and dashboard
```

## Setup on Windows (PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item config\.env.example .env
```

Edit `.env` and set stable keys. Generate each independently (one 8-byte key and one 32-byte key) with:

```powershell
python -c "import base64,secrets; print('DES_KEY_B64='+base64.b64encode(secrets.token_bytes(8)).decode()); print('HMAC_KEY_B64='+base64.b64encode(secrets.token_bytes(32)).decode())"
```

Copy the generated values into `.env`. Keep `.env` private and provision identical values to sender, receiver and dashboard. Linux/macOS use `python3 -m venv .venv`, activate with `source .venv/bin/activate`, then install the same requirements. If keys are omitted, a fresh process-local key is generated, which is suitable only for a single-process demo.

## Run without Docker

The local pipeline requires no MQTT broker:

```powershell
python -m scripts.run_simulation --devices 3 --messages 5
streamlit run app/dashboard/main.py
```

The first command simulates 5 readings from each device, encrypts/authenticates and processes them, and persists accepted data in `data/iot.db`. The dashboard opens at Streamlit's local URL. Run a measured crypto benchmark with `python -m scripts.run_benchmarks --iterations 1000 --payload-bytes 256`.

## MQTT with Mosquitto

Install Mosquitto locally or use Docker. For Docker, first create the broker password file and add the configured user (the file is intentionally not committed):

```powershell
New-Item -ItemType File -Force config\passwd | Out-Null
docker run --rm -it -v "${PWD}\config:/mosquitto/config" eclipse-mosquitto:2 mosquitto_passwd -c /mosquitto/config/passwd iot
```

Enter a password when prompted. The broker config requires authentication and applies `config/acl`. Set matching `MQTT_USERNAME=iot` and `MQTT_PASSWORD` in `.env`, then start services with `docker compose up --build`. Open `http://localhost:8501`.

To send from a host process, set `MQTT_HOST=localhost` in `.env`, run `python -m scripts.run_receiver` in one terminal and `python -m scripts.run_sender --devices 3 --interval 2` in another. Use `--count N` to stop after N published messages. Topics use `iot/devices/{device_id}/data` with QoS 1. The local demo ACL grants the shared `iot` identity access to the example topics; production systems should use per-device identities and narrowly scoped ACLs.

## Dashboard and security demonstrations

The dashboard includes overview metrics, latest readings and temperature chart, virtual device generation, eavesdropping/replay/tampering/injection/modification simulations, local crypto performance measurement, security events and active configuration. An eavesdropper sees only the envelope fields and ciphertext. Attack simulations are application-level demonstrations; they do not test MQTT broker authorization automatically.

MQTT broker authentication/ACL controls who can connect or access topics. HMAC authentication independently protects application packets. Both layers are needed for a deployment. Sensor plaintext is not logged by the receiver; failed HMAC packets are rejected before decryption.

## Tests and performance

```powershell
pytest -q
python -m scripts.run_benchmarks --iterations 1000 --payload-bytes 256
```

The benchmark reports observed average, minimum, maximum, standard deviation and throughput values for local cryptographic envelope processing. It does not claim MQTT latency; measuring that requires a running broker and network and is separate from crypto processing. Results vary by machine and must be generated rather than copied from documentation.

## Limitations and future work

DES has a small key and block size and is unsafe for modern use. CBC encryption is paired with HMAC in this assignment, but the design should migrate to AES-GCM. The default deployment uses a shared key model; production needs per-device keys, rotation and managed provisioning. MQTT TLS and live broker access-control attack automation are not configured. Dashboard attack tools exercise the local receiver pipeline. Future work can add a cipher interface with AES-GCM, broker latency telemetry, per-device identities, TLS, key rotation and richer device registration.
