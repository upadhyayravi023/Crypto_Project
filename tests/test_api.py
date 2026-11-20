import base64

from fastapi.testclient import TestClient


def test_backend_api_auth_and_sensor_pipeline(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "api.db"))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DES_KEY_B64", base64.b64encode(b"12345678").decode())
    monkeypatch.setenv("HMAC_KEY_B64", base64.b64encode(b"a" * 32).decode())
    monkeypatch.setenv("IOT_API_TOKEN", "test-token")
    monkeypatch.setenv("MQTT_ENABLED", "false")

    from app.api.main import app

    with TestClient(app) as client:
        assert client.get("/health").json()["ok"] is True
        assert client.get("/api/readings").status_code == 401
        headers = {"Authorization": "Bearer test-token"}
        response = client.post("/api/simulate", headers=headers,
                               json={"device_id": "api-device", "device_name": "API sensor"})
        assert response.status_code == 200
        assert response.json()["reading"]["device_id"] == "api-device"
        readings = client.get("/api/readings", headers=headers).json()
        assert len(readings) == 1
        assert readings[0]["sequence"] == 1
