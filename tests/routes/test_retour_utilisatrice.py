from fastapi.testclient import TestClient

from adaptateur_chiffrement import AdaptateurChiffrementDeTest

from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from adaptateurs.journal import TypeEvenement
from schemas.retour_utilisatrice import TagPositif
from schemas.type_utilisateur import TypeUtilisateur
from serveur_de_test import (
    ConstructeurAdaptateurJournal,
)


def test_route_retour_avec_retourne_succes_200(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    une_reponse_question,
    un_retour_positif,
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    adaptateur_base_de_donnees.sauvegarde_interaction(une_reponse_question)
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    payload = {
        "id_interaction": "id-interaction-test",
        "retour": {
            "type": "positif",
            "commentaire": "Très utile",
            "tags": ["complete", "facileacomprendre"],
        },
    }
    reponse = client.post("/api/retour", json=payload)

    assert reponse.status_code == 200
    assert (
        adaptateur_base_de_donnees.recupere_interaction(  # type: ignore[union-attr]
            "id-interaction-test"
        ).retour_utilisatrice
        == un_retour_positif
    )


def test_route_retour_retourne_donnees_attendues(
    un_serveur_de_test, un_adaptateur_de_chiffrement, une_reponse_question
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    adaptateur_base_de_donnees.sauvegarde_interaction(une_reponse_question)
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    payload = {
        "id_interaction": "id-interaction-test",
        "retour": {
            "type": "positif",
            "commentaire": "Très utile",
            "tags": ["complete", "facileacomprendre"],
        },
    }

    reponse = client.post("/api/retour", json=payload)
    data = reponse.json()

    assert data["commentaire"] == "Très utile"
    assert data["tags"] == [TagPositif.Complete, TagPositif.FacileAComprendre]


def test_route_retour_avec_interaction_inexistante_retourne_404(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    payload = {
        "id_interaction": "id-inconnu",
        "retour": {
            "type": "positif",
            "commentaire": "Très utile",
        },
    }

    reponse = client.post("/api/retour", json=payload)

    assert reponse.status_code == 404
    assert reponse.json() == {"detail": "Interaction non trouvée"}
    assert adaptateur_base_de_donnees.recupere_interaction("id-inconnu") is None


def test_route_retour_avec_payload_invalide_rejette_la_requete(
    un_serveur_de_test, un_adaptateur_de_chiffrement, une_reponse_question
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("23")
    adaptateur_base_de_donnees.sauvegarde_interaction(une_reponse_question)
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    payload = {
        "id": "23",
        "retour": {
            "type": "positif",
            "commentaire": "Très utile",
        },
    }
    reponse = client.post("/api/retour", json=payload)

    assert reponse.status_code == 422
    assert (
        adaptateur_base_de_donnees.recupere_interaction("23").retour_utilisatrice  # type: ignore[union-attr]
        is None
    )


def test_route_suppression_retour_avec_ID_supprime_le_retour_correspondant(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    une_reponse_question,
    un_retour_positif,
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    adaptateur_base_de_donnees.sauvegarde_interaction(une_reponse_question)
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice(
        "id-interaction-test", un_retour_positif
    )
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    reponse = client.delete("/api/retour/id-interaction-test")

    assert reponse.status_code == 200
    assert reponse.content.decode() == '"id-interaction-test"'
    assert (
        adaptateur_base_de_donnees.recupere_interaction(  # type: ignore[union-attr]
            "id-interaction-test"
        ).retour_utilisatrice
        is None
    )


def test_route_suppression_retour_avec_un_ID_de_retour_inexistant_retourne_une_erreur(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    une_reponse_question,
    un_retour_positif,
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    adaptateur_base_de_donnees.sauvegarde_interaction(une_reponse_question)
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice(
        "id-interaction-test", un_retour_positif
    )
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    reponse = client.delete("/api/retour/id-interaction-inexistant")

    assert reponse.status_code == 404
    assert (
        adaptateur_base_de_donnees.recupere_interaction("id-interaction-inexistant")
        is None
    )
    assert (
        adaptateur_base_de_donnees.recupere_interaction(  # type: ignore[union-attr]
            "id-interaction-test"
        ).retour_utilisatrice
        == un_retour_positif
    )


def test_route_retour_emet_evenement_avis_utilisateur_soumis_avec_tags(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    une_reponse_question,
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-456")
    adaptateur_base_de_donnees.sauvegarde_interaction(une_reponse_question)
    adaptateur_journal = ConstructeurAdaptateurJournal().construis()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=adaptateur_journal,
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


def test_route_suppression_retour_emet_evenement_avis_utilisateur_supprime(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    une_reponse_question,
    un_retour_positif,
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    adaptateur_base_de_donnees.sauvegarde_interaction(une_reponse_question)
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice(
        "id-interaction-test", un_retour_positif
    )
    adaptateur_journal = ConstructeurAdaptateurJournal().construis()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=adaptateur_journal,
    )

    client = TestClient(serveur)
    client.delete("/api/retour/id-interaction-test")

    adaptateur_journal.consigne_evenement.assert_called_once()
    [args, kwargs] = adaptateur_journal.consigne_evenement._mock_call_args
    assert kwargs["type"] == TypeEvenement.AVIS_UTILISATEUR_SUPPRIME
    assert kwargs["donnees"].id_interaction == "id-interaction-test"


def test_route_route_retour_identifie_le_type_d_utilisateur(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    une_reponse_question,
    un_retour_positif,
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-456")
    adaptateur_base_de_donnees.sauvegarde_interaction(une_reponse_question)
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice("id-456", un_retour_positif)
    adaptateur_chiffrement = AdaptateurChiffrementDeTest().qui_dechiffre(
        TypeUtilisateur.ANSSI
    )
    adaptateur_journal = ConstructeurAdaptateurJournal().construis()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=adaptateur_chiffrement,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=adaptateur_journal,
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
    client.post("/api/retour?type_utilisateur=EFGH", json=payload)

    [args, kwargs] = adaptateur_journal.consigne_evenement._mock_call_args
    assert kwargs["donnees"].type_utilisateur == TypeUtilisateur.ANSSI


def test_route_route_suppression_retour_identifie_le_type_d_utilisateur(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    une_reponse_question,
    un_retour_positif,
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    adaptateur_base_de_donnees.sauvegarde_interaction(une_reponse_question)
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice(
        "id-interaction-test", un_retour_positif
    )
    adaptateur_chiffrement = AdaptateurChiffrementDeTest().qui_dechiffre(
        TypeUtilisateur.ANSSI
    )
    adaptateur_journal = ConstructeurAdaptateurJournal().construis()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=adaptateur_chiffrement,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=adaptateur_journal,
    )

    client = TestClient(serveur)
    client.delete("/api/retour/id-interaction-test?type_utilisateur=IJKL")

    [args, kwargs] = adaptateur_journal.consigne_evenement._mock_call_args
    assert kwargs["donnees"].type_utilisateur == TypeUtilisateur.ANSSI
