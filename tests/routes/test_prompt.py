from fastapi.testclient import TestClient

from adaptateurs.chiffrement import fabrique_adaptateur_chiffrement
from configuration import Mode

from serveur_de_test import (
    ConstructeurServeur,
    ConstructeurServiceAlbert,
)


def test_route_prompt_retourne_le_prompt_systeme_en_developpement(
    adaptateur_chiffrement,
) -> None:
    service_albert = (
        ConstructeurServiceAlbert()
        .avec_prompt_systeme("Tu es une fougère.")
        .construis()
    )
    serveur = (
        ConstructeurServeur(
            mode=Mode.DEVELOPPEMENT, adaptateur_chiffrement=adaptateur_chiffrement
        )
        .avec_service_albert(service_albert)
        .construis()
    )

    client = TestClient(serveur)
    r = client.get("/api/prompt")

    assert r.status_code == 200
    assert r.json() == "Tu es une fougère."


def test_route_prompt_n_est_pas_exposee_en_production() -> None:
    serveur = ConstructeurServeur(
        mode=Mode.PRODUCTION, adaptateur_chiffrement=fabrique_adaptateur_chiffrement()
    ).construis()
    client: TestClient = TestClient(serveur)

    reponse = client.get("/api/prompt")

    assert reponse.status_code == 404
    assert reponse.json() == {"detail": "Not Found"}
