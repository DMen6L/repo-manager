from fastapi.testclient import TestClient

from backend.server import app

client = TestClient(app)


def test_root_endpoint() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_healthz_endpoint() -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_count_endpoint() -> None:
    response = client.get("/count")

    assert response.status_code == 200
    assert response.json() == {"": ""}
