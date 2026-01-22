from fastapi.testclient import TestClient

from configuration import Mode
from serveur_de_test import (
    ConstructeurServiceAlbert,
)


def test_route_prompt_retourne_le_prompt_systeme_en_developpement(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
) -> None:
    service_albert = (
        ConstructeurServiceAlbert()
        .avec_prompt_systeme("Tu es une fougère.")
        .construis()
    )
    serveur = un_serveur_de_test(
        mode=Mode.DEVELOPPEMENT,
        service_albert=service_albert,
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
    )

    client = TestClient(serveur)
    r = client.get("/api/prompt")

    assert r.status_code == 200
    assert r.json() == "Tu es une fougère."


def test_route_prompt_n_est_pas_exposee_en_production(
    un_serveur_de_test, un_adaptateur_de_chiffrement
) -> None:
    serveur = un_serveur_de_test(
        mode=Mode.PRODUCTION, adaptateur_chiffrement=un_adaptateur_de_chiffrement()
    )
    client: TestClient = TestClient(serveur)

    reponse = client.get("/api/prompt")

    assert reponse.status_code == 404
    assert reponse.json() == {"detail": "Not Found"}
