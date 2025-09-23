from fastapi.testclient import TestClient

from configuration import Mode
from serveur import fabrique_serveur


def test_route_sante_est_exposee_en_developpement():
    serveur = fabrique_serveur(Mode.DEVELOPPEMENT)
    client: TestClient = TestClient(serveur)

    response = client.get("/sante")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_route_sante_n_est_pas_exposee_en_production():
    serveur = fabrique_serveur(Mode.PRODUCTION)
    client: TestClient = TestClient(serveur)

    response = client.get("/sante")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
