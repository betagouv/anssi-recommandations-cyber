from fastapi.testclient import TestClient

from configuration import Mode
from schemas.albert import Paragraphe
from serveur_de_test import (
    ConstructeurServiceAlbert,
)


def test_route_recherche_repond_correctement(
    un_serveur_de_test, un_adaptateur_de_chiffrement
) -> None:
    service_albert = ConstructeurServiceAlbert().construis()
    serveur = un_serveur_de_test(
        mode=Mode.DEVELOPPEMENT,
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        service_albert=service_albert,
    )
    client: TestClient = TestClient(serveur)

    reponse = client.post("/api/recherche", json={"question": "Ma question test"})

    assert reponse.status_code == 200
    service_albert.recherche_paragraphes.assert_called_once()


def test_route_recherche_donnees_correctes(
    un_serveur_de_test, un_adaptateur_de_chiffrement
) -> None:
    paragraphes: list[Paragraphe] = []
    service_albert = (
        ConstructeurServiceAlbert()
        .qui_retourne_les_paragraphes(paragraphes)
        .construis()
    )
    serveur = un_serveur_de_test(
        mode=Mode.DEVELOPPEMENT,
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        service_albert=service_albert,
    )
    client: TestClient = TestClient(serveur)

    reponse = client.post("/api/recherche", json={"question": "Ma question test"})
    resultat = reponse.json()

    assert isinstance(resultat, list)
    assert len(resultat) == len(paragraphes)
    service_albert.recherche_paragraphes.assert_called_once()


def test_route_recherche_retourne_la_bonne_structure_d_objet(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
) -> None:
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
    serveur = un_serveur_de_test(
        mode=Mode.DEVELOPPEMENT,
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        service_albert=service_albert,
    )

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
