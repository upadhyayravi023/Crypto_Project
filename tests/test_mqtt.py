from app.communication.mqtt_client import create_client

def test_mqtt_dependency_error_or_client_available():
    try:
        client = create_client("test-client")
    except RuntimeError as exc:
        assert "optional dependencies" in str(exc)
    else:
        assert client is not None
