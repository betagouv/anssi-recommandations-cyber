from fastapi.testclient import TestClient

from adaptateurs.journal import TypeEvenement
from schemas.retour_utilisatrice import RetourPositif, TagPositif
from serveur_de_test import (
    ConstructeurAdaptateurBaseDeDonnees,
    ConstructeurAdaptateurJournal,
    ConstructeurServeur,
)


def test_route_retour_avec_mock_retourne_succes_200() -> None:
    retour = RetourPositif(
        commentaire="Très utile !",
        tags=[TagPositif.Complete, TagPositif.FacileAComprendre],
    )
    adaptateur_base_de_donnees = (
        ConstructeurAdaptateurBaseDeDonnees().avec_retour(retour).construis()
    )
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construis()
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
        ConstructeurAdaptateurBaseDeDonnees().avec_retour(retour).construis()
    )
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construis()
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
        ConstructeurAdaptateurBaseDeDonnees().avec_retour(None).construis()
    )
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construis()
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
    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construis()
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construis()
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
        ConstructeurAdaptateurBaseDeDonnees().avec_retour(retour).construis()
    )
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construis()
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
        ConstructeurAdaptateurBaseDeDonnees().avec_retour(retour).construis()
    )
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construis()
    )

    client = TestClient(serveur)
    reponse = client.delete("/api/retour/id-interaction-inexistant")

    assert reponse.status_code == 404
    adaptateur_base_de_donnees.supprime_retour_utilisatrice.assert_called_once()
    [args, _] = adaptateur_base_de_donnees.supprime_retour_utilisatrice._mock_call_args
    assert args[0] == "id-interaction-inexistant"


def test_route_retour_emet_evenement_avis_utilisateur_soumis_avec_tags() -> None:
    retour = RetourPositif(commentaire="Excellent !", tags=[TagPositif.Complete])
    adaptateur_base_de_donnees = (
        ConstructeurAdaptateurBaseDeDonnees().avec_retour(retour).construis()
    )
    adaptateur_journal = ConstructeurAdaptateurJournal().construis()
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .avec_adaptateur_journal(adaptateur_journal)
        .construis()
    )

    client = TestClient(serveur)
    payload = {
        "id_interaction": "id-456",
        "retour": {
            "type": "positif",
            "commentaire": "Excellent !",
            "tags": ["complete"],
        },
    }
    client.post("/api/retour", json=payload)

    adaptateur_journal.consigne_evenement.assert_called_once()
    [args, kwargs] = adaptateur_journal.consigne_evenement._mock_call_args
    assert kwargs["type"] == TypeEvenement.AVIS_UTILISATEUR_SOUMIS
    assert kwargs["donnees"].id_interaction == "id-456"
    assert kwargs["donnees"].type_retour == "positif"
    assert kwargs["donnees"].tags == [TagPositif.Complete]
    assert kwargs["donnees"].model_dump_json()


def test_route_suppression_retour_emet_evenement_avis_utilisateur_supprime() -> None:
    retour = RetourPositif(commentaire="Très utile !")
    adaptateur_base_de_donnees = (
        ConstructeurAdaptateurBaseDeDonnees().avec_retour(retour).construis()
    )
    adaptateur_journal = ConstructeurAdaptateurJournal().construis()
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .avec_adaptateur_journal(adaptateur_journal)
        .construis()
    )

    client = TestClient(serveur)
    client.delete("/api/retour/id-interaction-test")

    adaptateur_journal.consigne_evenement.assert_called_once()
    [args, kwargs] = adaptateur_journal.consigne_evenement._mock_call_args
    assert kwargs["type"] == TypeEvenement.AVIS_UTILISATEUR_SUPPRIME
    assert kwargs["donnees"].id_interaction == "id-interaction-test"
