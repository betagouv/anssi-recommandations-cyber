import uuid

import pytest
from fastapi.testclient import TestClient

from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from adaptateurs.journal import (
    AdaptateurJournalMemoire,
)
from schemas.api import QuestionRequete
from schemas.type_utilisateur import TypeUtilisateur
from serveur_de_test import ServiceAlbertMemoire


def test_route_initie_conversation_repond_correctement(
    un_serveur_de_test, un_adaptateur_de_chiffrement
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    service_albert = ServiceAlbertMemoire()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        service_albert=service_albert,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client: TestClient = TestClient(serveur)
    r = client.post("/api/conversation", json={"question": "Qui es-tu"})

    assert r.status_code == 200
    assert service_albert.question_recue == "Qui es-tu"

    serveur.dependency_overrides.clear()


def test_route_initie_conversation_retourne_donnees_correctes(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    un_constructeur_de_reponse_question,
    un_constructeur_de_paragraphe,
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    service_albert = ServiceAlbertMemoire()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        service_albert=service_albert,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )
    requete_question = QuestionRequete(question="Qui es-tu")
    reponse = (
        un_constructeur_de_reponse_question()
        .a_partir_d_une_requete(requete_question)
        .donnant_en_reponse("Réponse de test d'Albert")
        .avec_les_paragraphes(
            [
                un_constructeur_de_paragraphe()
                .avec_contenu("Contenu du paragraphe 1")
                .ayant_comme_score(0.75)
                .a_la_page(29)
                .dans_le_document(
                    "anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf"
                )
                .construis(),
                un_constructeur_de_paragraphe()
                .avec_contenu("Contenu du paragraphe 2")
                .ayant_comme_score(0.72)
                .a_la_page(15)
                .dans_le_document("guide_hygiene_informatique_anssi.pdf")
                .construis(),
            ]
        )
        .construis()
    )
    service_albert.ajoute_reponse(reponse)

    client_http = TestClient(serveur)
    r = client_http.post("/api/conversation", json=requete_question.__dict__)

    response_data = r.json()
    assert response_data["id_interaction"]
    assert response_data == {
        "id_interaction": response_data["id_interaction"],
        "question": "Qui es-tu",
        "reponse": "Réponse de test d'Albert",
        "paragraphes": [
            {
                "score_similarite": 0.75,
                "numero_page": 29,
                "url": "http://mondocument.local/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                "nom_document": "anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                "contenu": "Contenu du paragraphe 1",
            },
            {
                "score_similarite": 0.72,
                "numero_page": 15,
                "url": "http://mondocument.local/guide_hygiene_informatique_anssi.pdf",
                "nom_document": "guide_hygiene_informatique_anssi.pdf",
                "contenu": "Contenu du paragraphe 2",
            },
        ],
        "id_conversation": response_data["id_conversation"],
    }
    assert (
        adaptateur_base_de_donnees.recupere_conversation(
            uuid.UUID(response_data["id_conversation"])
        )
        is not None
    )


def test_route_initie_conversation_rejette_question_trop_longue(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
) -> None:
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    service_albert = ServiceAlbertMemoire()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
        service_albert=service_albert,
    )

    client = TestClient(serveur)
    question_trop_longue = "?" * 5001

    reponse = client.post("/api/conversation", json={"question": question_trop_longue})

    assert reponse.status_code == 422
    assert "5000" in reponse.json()["detail"][0]["msg"]
    assert service_albert.question_recue is None

    serveur.dependency_overrides.clear()


@pytest.mark.parametrize(
    "type_utilisateur",
    [
        TypeUtilisateur.ANSSI,
        TypeUtilisateur.LAMBDA,
        TypeUtilisateur.EXPERT_SSI,
        TypeUtilisateur.EVALUATION,
    ],
)
def test_route_initie_conversation_identifie_le_type_d_utilisateur(
    type_utilisateur, un_serveur_de_test, un_adaptateur_de_chiffrement
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    adaptateur_chiffrement = un_adaptateur_de_chiffrement(dechiffre=type_utilisateur)
    adaptateur_journal = AdaptateurJournalMemoire()
    service_albert = ServiceAlbertMemoire()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=adaptateur_chiffrement,
        adaptateur_journal=adaptateur_journal,
        service_albert=service_albert,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    client.post(
        "/api/conversation?type_utilisateur=ABCD", json={"question": "Une question"}
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["donnees"].type_utilisateur == type_utilisateur


def test_route_initie_conversation_identifie_comme_inconnu_le_type_d_utilisateur(
    un_serveur_de_test, un_adaptateur_de_chiffrement
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    adaptateur_chiffrement = un_adaptateur_de_chiffrement(
        dechiffre="une chaine inconnue"
    )
    adaptateur_journal = AdaptateurJournalMemoire()
    service_albert = ServiceAlbertMemoire()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=adaptateur_chiffrement,
        adaptateur_journal=adaptateur_journal,
        service_albert=service_albert,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    client.post(
        "/api/conversation?type_utilisateur=ABCD", json={"question": "Une question"}
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["donnees"].type_utilisateur == TypeUtilisateur.INCONNU


def test_route_initie_conversation_identifie_comme_inconnu_le_type_d_utilisateur_si_le_dechiffrement_echoue(
    un_serveur_de_test, un_adaptateur_de_chiffrement
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    adaptateur_chiffrement = un_adaptateur_de_chiffrement(leve_une_erreur=True)
    adaptateur_journal = AdaptateurJournalMemoire()
    service_albert = ServiceAlbertMemoire()
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=adaptateur_chiffrement,
        adaptateur_journal=adaptateur_journal,
        service_albert=service_albert,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    client.post(
        "/api/conversation?type_utilisateur=ABCD", json={"question": "Une question"}
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["donnees"].type_utilisateur == TypeUtilisateur.INCONNU
