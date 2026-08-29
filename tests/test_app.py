from app.config import Settings
from app.database import get_db
from app.main import create_app
from fastapi.testclient import TestClient
from unittest.mock import MagicMock


def test_health_is_public_and_returns_request_id(client):
    response = client.get("/health", headers={"X-Request-ID": "health-check"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"] == "health-check"


def test_protected_route_requires_api_key(client):
    response = client.get("/users/")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"
    assert response.json()["error"]["request_id"]


def test_validation_errors_use_consistent_envelope(client):
    response = client.post(
        "/users/",
        headers={"X-API-Key": "test-secret"},
        json={"name": "", "email": "not-an-email"},
    )

    assert response.status_code == 422
    body = response.json()["error"]
    assert body["code"] == "validation_error"
    assert body["message"] == "Request validation failed"
    assert len(body["details"]) == 2


def test_api_key_can_be_disabled_for_local_development():
    settings = Settings(
        api_secret_key=None,
        ollama_host="http://ollama.invalid",
        ollama_model="test-model",
        ollama_api_key="test-key",
        allowed_models=frozenset({"test-model"}),
    )
    app = create_app(settings)
    session = MagicMock()
    session.query.return_value.offset.return_value.limit.return_value.all.return_value = []

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as local_client:
        response = local_client.get("/users/")

    assert response.status_code == 200
    assert response.json() == []
