from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings


def test_health_check_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "environment" in data


def test_settings_singleton():
    settings_1 = get_settings()
    settings_2 = get_settings()
    assert settings_1 is settings_2
    assert settings_1.app_name == "Online Coding Judge API"
    assert isinstance(settings_1.cors_origins, list)
