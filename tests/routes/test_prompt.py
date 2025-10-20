from fastapi.testclient import TestClient
from unittest.mock import Mock

from services.albert import ServiceAlbert, fabrique_service_albert
from configuration import Mode
from serveur import fabrique_serveur


def test_route_prompt_retourne_le_prompt_systeme_en_developpement() -> None:
    mock_client: Mock = Mock(spec=ServiceAlbert)
    mock_client.PROMPT_SYSTEME = "Tu es une fougère."

    serveur = fabrique_serveur(Mode.DEVELOPPEMENT)
    serveur.dependency_overrides[fabrique_service_albert] = lambda: mock_client

    client = TestClient(serveur)
    r = client.get("/api/prompt")

    assert r.status_code == 200
    assert r.json() == "Tu es une fougère."


def test_route_prompt_n_est_pas_exposee_en_production() -> None:
    serveur = fabrique_serveur(Mode.PRODUCTION)
    client: TestClient = TestClient(serveur)

    response = client.get("/api/prompt")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
