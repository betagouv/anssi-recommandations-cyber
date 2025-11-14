from fastapi.testclient import TestClient

from configuration import Mode
from serveur import fabrique_serveur

from adaptateurs.chiffrement import fabrique_adaptateur_chiffrement


def test_route_sante_est_exposee_en_developpement() -> None:
    serveur = fabrique_serveur(Mode.DEVELOPPEMENT, fabrique_adaptateur_chiffrement())
    client: TestClient = TestClient(serveur)

    reponse = client.get("/api/sante")

    assert reponse.status_code == 200
    assert reponse.json() == {"status": "ok"}


def test_route_sante_n_est_pas_exposee_en_production() -> None:
    serveur = fabrique_serveur(Mode.PRODUCTION, fabrique_adaptateur_chiffrement())
    client: TestClient = TestClient(serveur)

    reponse = client.get("/api/sante")

    assert reponse.status_code == 404
    assert reponse.json() == {"detail": "Not Found"}
