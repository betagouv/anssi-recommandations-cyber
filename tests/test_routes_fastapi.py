from fastapi.testclient import TestClient
from main import app


def test_route_sante() -> None:
    """Vérifie que l'application FastAPI fonctionne"""
    client: TestClient = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
