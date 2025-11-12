from fastapi.testclient import TestClient

from schemas.retour_utilisatrice import RetourPositif, TagPositif
from serveur_de_test import (
    ConstructeurAdaptateurBaseDeDonnees,
    ConstructeurServeur,
)


def test_route_retour_avec_mock_retourne_succes_200() -> None:
    retour = RetourPositif(
        commentaire="Très utile !",
        tags=[TagPositif.Complete, TagPositif.FacileAComprendre],
    )
    adaptateur_base_de_donnees = (
        ConstructeurAdaptateurBaseDeDonnees().avec_retour(retour).construit()
    )
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construit()
    )

    client = TestClient(serveur)
    payload = {
        "id_interaction": "id-123",
        "retour": {
            "type": "positif",
            "commentaire": "Très utile",
            "tags": ["complete", "facileacomprendre"],
        },
    }
    reponse = client.post("/api/retour", json=payload)

    assert reponse.status_code == 200
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice.assert_called_once()


def test_route_retour_avec_mock_retourne_donnees_attendues() -> None:
    retour = RetourPositif(
        commentaire="Très utile !",
        tags=[TagPositif.Complete, TagPositif.FacileAComprendre],
    )
    adaptateur_base_de_donnees = (
        ConstructeurAdaptateurBaseDeDonnees().avec_retour(retour).construit()
    )
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construit()
    )

    client = TestClient(serveur)
    payload = {
        "id_interaction": "id-123",
        "retour": {
            "type": "positif",
            "commentaire": "Très utile !",
            "tags": ["complete", "facileacomprendre"],
        },
    }

    reponse = client.post("/api/retour", json=payload)
    data = reponse.json()

    assert data["commentaire"] == "Très utile !"
    assert data["tags"] == [TagPositif.Complete, TagPositif.FacileAComprendre]
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice.assert_called_once()


def test_route_retour_avec_interaction_inexistante_retourne_404() -> None:
    adaptateur_base_de_donnees = (
        ConstructeurAdaptateurBaseDeDonnees().avec_retour(None).construit()
    )
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construit()
    )

    client = TestClient(serveur)
    payload = {
        "id_interaction": "id-123",
        "retour": {
            "type": "positif",
            "commentaire": "Très utile",
        },
    }

    reponse = client.post("/api/retour", json=payload)

    assert reponse.status_code == 404
    assert reponse.json() == {"detail": "Interaction non trouvée"}
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice.assert_called_once()


def test_route_retour_avec_payload_invalide_rejette_la_requete() -> None:
    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construit()
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construit()
    )

    client = TestClient(serveur)
    payload = {
        "id": 23,
        "retour": {
            "type": "positif",
            "commentaire": "Très utile",
        },
    }
    reponse = client.post("/api/retour", json=payload)

    assert reponse.status_code == 422
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice.assert_not_called()


def test_route_suppression_retour_avec_ID_supprime_le_retour_correspondant() -> None:
    retour = RetourPositif(
        commentaire="Très utile !",
        tags=[TagPositif.Complete, TagPositif.FacileAComprendre],
    )
    adaptateur_base_de_donnees = (
        ConstructeurAdaptateurBaseDeDonnees().avec_retour(retour).construit()
    )
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construit()
    )

    client = TestClient(serveur)
    reponse = client.delete("/api/retour/id-interaction-test")

    assert reponse.status_code == 200
    assert reponse.content.decode() == '"id-interaction-test"'
    adaptateur_base_de_donnees.supprime_retour_utilisatrice.assert_called_once()
    [args, _] = adaptateur_base_de_donnees.supprime_retour_utilisatrice._mock_call_args
    assert args[0] == "id-interaction-test"


def test_route_suppression_retour_avec_un_ID_de_retour_inexistant_retourne_une_erreur() -> (
    None
):
    retour = RetourPositif(
        commentaire="Très utile !",
        tags=[TagPositif.Complete, TagPositif.FacileAComprendre],
    )
    adaptateur_base_de_donnees = (
        ConstructeurAdaptateurBaseDeDonnees().avec_retour(retour).construit()
    )
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construit()
    )

    client = TestClient(serveur)
    reponse = client.delete("/api/retour/id-interaction-inexistant")

    assert reponse.status_code == 404
    adaptateur_base_de_donnees.supprime_retour_utilisatrice.assert_called_once()
    [args, _] = adaptateur_base_de_donnees.supprime_retour_utilisatrice._mock_call_args
    assert args[0] == "id-interaction-inexistant"
