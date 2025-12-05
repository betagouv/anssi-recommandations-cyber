from fastapi.testclient import TestClient

from serveur_de_test import (
    ConstructeurServiceAlbert,
    ConstructeurServeur,
)


def test_route_reclassement_repond_correctement() -> None:
    service_albert = ConstructeurServiceAlbert().construis()
    serveur = ConstructeurServeur().avec_service_albert(service_albert).construis()
    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/reclasse",
        json={
            "prompt": "Ma question test",
            "input": ["texte1", "texte2"],
            "model": "modele-test",
        },
    )

    assert reponse.status_code == 200
    service_albert.reclasse.assert_called_once()


def test_route_reclassement_repond_correctement_avec_une_reponse_triee():
    reponse = {"paragraphes_tries": ["texte2", "texte1"]}

    service_albert = (
        ConstructeurServiceAlbert().qui_reclasse_les_paragraphes(reponse).construis()
    )
    serveur = ConstructeurServeur().avec_service_albert(service_albert).construis()

    client: TestClient = TestClient(serveur)

    reponse = client.post(
        "/api/reclasse",
        json={
            "prompt": "Ma question test",
            "input": ["texte1", "texte2"],
            "model": "modele-test",
        },
    )

    assert reponse.status_code == 200
    assert reponse.json() == {"paragraphes_tries": ["texte2", "texte1"]}
