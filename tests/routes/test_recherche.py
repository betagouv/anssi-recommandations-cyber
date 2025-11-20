from fastapi.testclient import TestClient

from schemas.client_albert import Paragraphe

from serveur_de_test import (
    ConstructeurServiceAlbert,
    ConstructeurServeur,
)


def test_route_recherche_repond_correctement() -> None:
    service_albert = ConstructeurServiceAlbert().construis()
    serveur = ConstructeurServeur().avec_service_albert(service_albert).construis()
    client: TestClient = TestClient(serveur)

    reponse = client.post("/api/recherche", json={"question": "Ma question test"})

    assert reponse.status_code == 200
    service_albert.recherche_paragraphes.assert_called_once()


def test_route_recherche_donnees_correctes() -> None:
    paragraphes: list[Paragraphe] = []
    service_albert = (
        ConstructeurServiceAlbert()
        .qui_retourne_les_paragraphes(paragraphes)
        .construis()
    )
    serveur = ConstructeurServeur().avec_service_albert(service_albert).construis()
    client: TestClient = TestClient(serveur)

    reponse = client.post("/api/recherche", json={"question": "Ma question test"})
    resultat = reponse.json()

    assert isinstance(resultat, list)
    assert len(resultat) == len(paragraphes)
    service_albert.recherche_paragraphes.assert_called_once()


def test_route_recherche_retourne_la_bonne_structure_d_objet() -> None:
    paragraphes = [
        Paragraphe(
            contenu="Contenu du paragraphe 1",
            url="https://cyber.gouv.fr/sites/default/files/2021/10/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
            score_similarite=0.75,
            numero_page=29,
            nom_document="anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
        ),
    ]

    service_albert = (
        ConstructeurServiceAlbert()
        .qui_retourne_les_paragraphes(paragraphes)
        .construis()
    )
    serveur = ConstructeurServeur().avec_service_albert(service_albert).construis()

    client: TestClient = TestClient(serveur)
    reponse = client.post("/api/recherche", json={"question": "Ma question test"})

    resultat = reponse.json()
    assert resultat == [
        {
            "contenu": "Contenu du paragraphe 1",
            "url": "https://cyber.gouv.fr/sites/default/files/2021/10/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
            "score_similarite": 0.75,
            "numero_page": 29,
            "nom_document": "anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
        }
    ]

    service_albert.recherche_paragraphes.assert_called_once()
