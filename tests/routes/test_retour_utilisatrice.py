import uuid

from adaptateur_chiffrement import AdaptateurChiffrementDeTest
from fastapi.testclient import TestClient
from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from adaptateurs.journal import TypeEvenement, AdaptateurJournalMemoire
from schemas.retour_utilisatrice import TagPositif
from schemas.type_utilisateur import TypeUtilisateur


def test_route_retour_avec_retourne_succes_200(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    une_interaction,
    un_retour_positif,
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    adaptateur_base_de_donnees.sauvegarde_interaction(une_interaction)
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    payload = {
        "id_interaction": str(une_interaction.id),
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
            une_interaction.id
        ).retour_utilisatrice
        == un_retour_positif
    )


def test_route_retour_retourne_donnees_attendues(
    un_serveur_de_test, un_adaptateur_de_chiffrement, une_interaction
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    adaptateur_base_de_donnees.sauvegarde_interaction(une_interaction)
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    payload = {
        "id_interaction": str(une_interaction.id),
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
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    payload = {
        "id_interaction": str(uuid.uuid4()),
        "retour": {
            "type": "positif",
            "commentaire": "Très utile",
        },
    }

    reponse = client.post("/api/retour", json=payload)

    assert reponse.status_code == 404
    assert reponse.json() == {"detail": "Interaction non trouvée"}


def test_route_retour_avec_payload_invalide_rejette_la_requete(
    un_serveur_de_test, un_adaptateur_de_chiffrement, une_interaction
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    adaptateur_base_de_donnees.sauvegarde_interaction(une_interaction)
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
    interaction_recuperee = adaptateur_base_de_donnees.recupere_interaction(
        une_interaction.id
    )

    assert reponse.status_code == 422
    assert interaction_recuperee is not None
    assert interaction_recuperee.retour_utilisatrice is None


def test_route_suppression_retour_avec_ID_supprime_le_retour_correspondant(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    une_interaction,
    un_retour_positif,
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    adaptateur_base_de_donnees.sauvegarde_interaction(une_interaction)
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice(
        une_interaction.id, un_retour_positif
    )
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    reponse = client.delete(f"/api/retour/{une_interaction.id}")

    assert reponse.status_code == 200
    assert reponse.content.decode() == f'"{une_interaction.id}"'
    assert (
        adaptateur_base_de_donnees.recupere_interaction(  # type: ignore[union-attr]
            une_interaction.id
        ).retour_utilisatrice
        is None
    )


def test_route_suppression_retour_avec_un_ID_de_retour_inexistant_retourne_une_erreur(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    une_interaction,
    un_retour_positif,
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    adaptateur_base_de_donnees.sauvegarde_interaction(une_interaction)
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice(
        une_interaction.id, un_retour_positif
    )
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    id_inexistant = str(uuid.uuid4())
    reponse = client.delete(f"/api/retour/{id_inexistant}")

    assert reponse.status_code == 404
    assert (
        adaptateur_base_de_donnees.recupere_interaction(uuid.UUID(id_inexistant))
        is None
    )
    assert (
        adaptateur_base_de_donnees.recupere_interaction(  # type: ignore[union-attr]
            une_interaction.id
        ).retour_utilisatrice
        == un_retour_positif
    )


def test_route_retour_emet_evenement_avis_utilisateur_soumis_avec_tags(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    une_interaction,
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    adaptateur_base_de_donnees.sauvegarde_interaction(une_interaction)
    adaptateur_journal = AdaptateurJournalMemoire()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=adaptateur_journal,
    )

    client = TestClient(serveur)
    payload = {
        "id_interaction": str(une_interaction.id),
        "retour": {
            "type": "positif",
            "commentaire": "Excellent !",
            "tags": ["complete"],
        },
    }
    client.post("/api/retour", json=payload)

    evenements = adaptateur_journal.les_evenements()
    assert len(evenements) == 1
    assert evenements[0]["type"] == TypeEvenement.AVIS_UTILISATEUR_SOUMIS
    assert evenements[0]["donnees"].id_interaction == str(une_interaction.id)
    assert evenements[0]["donnees"].type_retour == "positif"
    assert evenements[0]["donnees"].tags == [TagPositif.Complete]
    assert evenements[0]["donnees"].model_dump_json()


def test_route_suppression_retour_emet_evenement_avis_utilisateur_supprime(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    une_interaction,
    un_retour_positif,
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    adaptateur_base_de_donnees.sauvegarde_interaction(une_interaction)
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice(
        une_interaction.id, un_retour_positif
    )
    adaptateur_journal = AdaptateurJournalMemoire()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=adaptateur_journal,
    )

    client = TestClient(serveur)
    client.delete(f"/api/retour/{une_interaction.id}")

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["type"] == TypeEvenement.AVIS_UTILISATEUR_SUPPRIME
    assert evenements[0]["donnees"].id_interaction == str(une_interaction.id)


def test_route_route_retour_identifie_le_type_d_utilisateur(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    une_interaction,
    un_retour_positif,
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    adaptateur_base_de_donnees.sauvegarde_interaction(une_interaction)
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice(
        une_interaction.id, un_retour_positif
    )
    adaptateur_chiffrement = AdaptateurChiffrementDeTest().qui_dechiffre(
        TypeUtilisateur.ANSSI
    )
    adaptateur_journal = AdaptateurJournalMemoire()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=adaptateur_chiffrement,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=adaptateur_journal,
    )

    client = TestClient(serveur)
    payload = {
        "id_interaction": str(une_interaction.id),
        "retour": {
            "type": "positif",
            "commentaire": "Excellent !",
            "tags": ["complete"],
        },
    }
    client.post("/api/retour?type_utilisateur=EFGH", json=payload)

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["donnees"].type_utilisateur == TypeUtilisateur.ANSSI


def test_route_route_suppression_retour_identifie_le_type_d_utilisateur(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    une_interaction,
    un_retour_positif,
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    adaptateur_base_de_donnees.sauvegarde_interaction(une_interaction)
    adaptateur_base_de_donnees.ajoute_retour_utilisatrice(
        une_interaction.id, un_retour_positif
    )
    adaptateur_chiffrement = AdaptateurChiffrementDeTest().qui_dechiffre(
        TypeUtilisateur.ANSSI
    )
    adaptateur_journal = AdaptateurJournalMemoire()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=adaptateur_chiffrement,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        adaptateur_journal=adaptateur_journal,
    )

    client = TestClient(serveur)
    client.delete(f"/api/retour/{une_interaction.id}?type_utilisateur=IJKL")

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["donnees"].type_utilisateur == TypeUtilisateur.ANSSI
