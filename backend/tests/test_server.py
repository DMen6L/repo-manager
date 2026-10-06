from fastapi.testclient import TestClient

from backend.server import app

client = TestClient(app)


def test_root_endpoint() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_healthz_endpoint() -> None:
    response = client.get("/healthz")

    assert response.status_code == 201
    assert response.json() == {"status": "ok"}


def test_list_cases_endpoint() -> None:
    response = client.get("/cases")

    assert response.status_code == 200
    assert response.json() == {"cases": ["basic_project"]}


def test_get_case_endpoint() -> None:
    response = client.get("/cases/basic_project")

    assert response.status_code == 200
    body = response.json()

    assert body["name"] == "basic_project"
    assert [file["path"] for file in body["files"]] == [
        "main.py",
        "models.py",
        "services.py",
    ]


def test_case_summary_endpoint() -> None:
    response = client.get("/cases/basic_project/summary")

    assert response.status_code == 200
    assert response.json() == {
        "name": "basic_project",
        "python_files": 3,
        "modules": ["main", "models", "services"],
    }


def test_missing_case_returns_not_found() -> None:
    response = client.get("/cases/missing_project")

    assert response.status_code == 404
