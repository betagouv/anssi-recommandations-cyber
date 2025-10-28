from fastapi.testclient import TestClient

from adaptateurs.chiffrement import fabrique_adaptateur_chiffrement
from configuration import Mode
from serveur import fabrique_serveur

from serveur_de_test import (
    ConstructeurServeur,
    ConstructeurServiceAlbert,
)


def test_route_prompt_retourne_le_prompt_systeme_en_developpement() -> None:
    service_albert = (
        ConstructeurServiceAlbert()
        .avec_prompt_systeme("Tu es une fougère.")
        .construit()
    )
    serveur = (
        ConstructeurServeur(mode=Mode.DEVELOPPEMENT)
        .avec_service_albert(service_albert)
        .construit()
    )

    client = TestClient(serveur)
    r = client.get("/api/prompt")

    assert r.status_code == 200
    assert r.json() == "Tu es une fougère."


def test_route_prompt_n_est_pas_exposee_en_production() -> None:
    serveur = fabrique_serveur(Mode.PRODUCTION, fabrique_adaptateur_chiffrement())
    client: TestClient = TestClient(serveur)

    response = client.get("/api/prompt")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
