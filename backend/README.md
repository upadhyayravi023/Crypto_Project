# FastAPI backend on Render

Create a Render **Web Service** from the repository, branch `main`, with the repository root as the Root Directory.

- Build command: `pip install -r backend/requirements.txt`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

Create a Render Postgres database in the same region and set `DATABASE_URL` to its internal connection string. Add these environment variables to the backend service:

| Variable | Value |
| --- | --- |
| `DES_KEY_B64` | Base64 for exactly 8 random bytes |
| `HMAC_KEY_B64` | Base64 for 32 random bytes |
| `MQTT_ENABLED` | `true` |
| `MQTT_HOST` | MQTT broker hostname |
| `MQTT_PORT` | `8883` for a TLS broker |
| `MQTT_TLS` | `true` |
| `MQTT_USERNAME` | Broker username |
| `MQTT_PASSWORD` | Broker password |
| `MQTT_TOPIC_PREFIX` | `iot` |

The local terminal demonstration does not require MQTT credentials. The Render backend accepts data from the frontend through `/api/*` endpoints and receives broker messages when MQTT is enabled. For this public academic demo, both apps use the hardcoded demo token `DES-IOT-DEMO-ONLY-2026`; anyone who can read the repository can call these API endpoints. Do not use this setup for real or private data.

The same resources can be provisioned from the repository-root `render.yaml` Blueprint. For exact key provisioning and free-tier limits, see [`docs/deployment_render.md`](../docs/deployment_render.md).
