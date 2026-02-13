import uuid
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from adaptateurs.journal import (
    TypeEvenement,
    AdaptateurJournalMemoire,
)
from configuration import Mode
from schemas.albert import ReponseQuestion
from schemas.api import QuestionRequete
from conversation.conversation import Interaction, Conversation
from schemas.type_utilisateur import TypeUtilisateur
from schemas.violations import (
    ViolationIdentite,
    ViolationMalveillance,
    ViolationThematique,
)
from serveur_de_test import ServiceAlbertMemoire


def test_route_pose_question_repond_correctement(
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
    r = client.post("/api/pose_question", json={"question": "Qui es-tu"})

    assert r.status_code == 200
    assert service_albert.question_recue == "Qui es-tu"

    serveur.dependency_overrides.clear()


def test_route_pose_question_retourne_donnees_correctes(
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
    r = client_http.post("/api/pose_question", json=requete_question.__dict__)

    response_data = r.json()
    assert response_data["interaction_id"]
    assert response_data == {
        "interaction_id": response_data["interaction_id"],
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
        "conversation_id": response_data["conversation_id"],
    }
    assert (
        adaptateur_base_de_donnees.recupere_interaction(
            uuid.UUID(response_data["interaction_id"])
        )
        is not None
    )


@pytest.mark.parametrize("mode", [Mode.DEVELOPPEMENT, Mode.PRODUCTION])
def test_route_pose_question_emet_un_evenement_journal_indiquant_la_creation_d_une_interaction(
    mode, un_serveur_de_test, un_adaptateur_de_chiffrement
) -> None:
    valeur_hachee = "haché"
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    adaptateur_journal = AdaptateurJournalMemoire()
    service_albert = ServiceAlbertMemoire()
    adaptateur_chiffrement = un_adaptateur_de_chiffrement(hachage=valeur_hachee)
    serveur = un_serveur_de_test(
        mode=mode,
        adaptateur_chiffrement=adaptateur_chiffrement,
        adaptateur_journal=adaptateur_journal,
        service_albert=service_albert,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client: TestClient = TestClient(serveur)
    client.post(
        "/api/pose_question",
        json={"question": "Qui es-tu ?"},
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["type"] == TypeEvenement.INTERACTION_CREEE
    assert evenements[0]["donnees"].id_interaction == valeur_hachee
    assert isinstance(UUID(adaptateur_chiffrement.valeur_recue_pour_le_hache), UUID)


def test_route_pose_question_emet_un_evenement_donnant_les_informations_sur_l_interaction_creee(
    un_serveur_de_test, un_adaptateur_de_chiffrement
) -> None:
    question_posee = " Qui es-tu ? "
    valeur_hachee = "haché"
    reponse = ReponseQuestion(
        reponse=" Je suis Albert, pour vous servir ",
        paragraphes=[],
        question=question_posee,
        violation=None,
    )
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    adaptateur_journal = AdaptateurJournalMemoire()
    service_albert = ServiceAlbertMemoire()
    service_albert.ajoute_reponse(reponse)
    adaptateur_chiffrement = un_adaptateur_de_chiffrement(hachage=valeur_hachee)
    serveur = un_serveur_de_test(
        mode=Mode.PRODUCTION,
        adaptateur_chiffrement=adaptateur_chiffrement,
        adaptateur_journal=adaptateur_journal,
        service_albert=service_albert,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    client.post(
        "/api/pose_question",
        json={"question": question_posee},
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["donnees"].longueur_question == 11
    assert evenements[0]["donnees"].longueur_reponse == 32


def test_route_pose_question_emet_un_evenement_donnant_la_longueur_totale_des_paragraphes_sur_l_interaction_creee(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
    un_constructeur_de_paragraphe,
    un_constructeur_de_reponse_question,
):
    question_posee = QuestionRequete(question=" Qui es-tu ? ")
    reponse = (
        un_constructeur_de_reponse_question()
        .donnant_en_reponse(" Je suis Albert, pour vous servir ")
        .avec_les_paragraphes(
            [
                un_constructeur_de_paragraphe().avec_contenu("Contenu A").construis(),
                un_constructeur_de_paragraphe().avec_contenu("Contenu B").construis(),
            ]
        )
        .a_partir_d_une_requete(question_posee)
        .construis()
    )
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire("id-interaction-test")
    adaptateur_chiffrement = un_adaptateur_de_chiffrement(hachage="haché")
    adaptateur_journal = AdaptateurJournalMemoire()
    service_albert = ServiceAlbertMemoire()
    service_albert.ajoute_reponse(reponse)
    serveur = un_serveur_de_test(
        mode=Mode.PRODUCTION,
        adaptateur_chiffrement=adaptateur_chiffrement,
        adaptateur_journal=adaptateur_journal,
        service_albert=service_albert,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    client.post(
        "/api/pose_question",
        json=question_posee.__dict__,
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["donnees"].longueur_paragraphes == 18


@pytest.mark.parametrize(
    "violation", [ViolationIdentite(), ViolationMalveillance(), ViolationThematique()]
)
def test_route_pose_question_emet_un_evenement_journal_indiquant_la_detection_d_une_question_illegale(
    violation, un_serveur_de_test, un_adaptateur_de_chiffrement
) -> None:
    valeur_hachee = "haché"
    reponse = ReponseQuestion(
        reponse="", paragraphes=[], question="Q?", violation=violation
    )

    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    adaptateur_chiffrement = un_adaptateur_de_chiffrement(hachage=valeur_hachee)
    adaptateur_journal = AdaptateurJournalMemoire()
    service_albert = ServiceAlbertMemoire()
    service_albert.ajoute_reponse(reponse)
    serveur = un_serveur_de_test(
        adaptateur_chiffrement=adaptateur_chiffrement,
        adaptateur_journal=adaptateur_journal,
        service_albert=service_albert,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client: TestClient = TestClient(serveur)
    client.post(
        "/api/pose_question",
        json={"question": "Qui es-tu ?"},
    )

    evenements = adaptateur_journal.les_evenements()
    assert len(evenements) == 2
    assert evenements[1]["type"] == TypeEvenement.VIOLATION_DETECTEE
    assert evenements[1]["donnees"].id_interaction == valeur_hachee
    assert evenements[1]["donnees"].type_violation == violation.__class__.__name__
    assert evenements[1]["donnees"].model_dump_json()
    assert isinstance(UUID(adaptateur_chiffrement.valeur_recue_pour_le_hache), UUID)


def test_route_pose_question_rejette_question_trop_longue(
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

    reponse = client.post("/api/pose_question", json={"question": question_trop_longue})

    assert reponse.status_code == 422
    assert "5000" in reponse.json()["detail"][0]["msg"]
    assert service_albert.question_recue is None

    serveur.dependency_overrides.clear()


@pytest.mark.parametrize(
    "type_utilisateur",
    [TypeUtilisateur.ANSSI, TypeUtilisateur.LAMBDA, TypeUtilisateur.EXPERT_SSI],
)
def test_route_pose_question_identifie_le_type_d_utilisateur(
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
        "/api/pose_question?type_utilisateur=ABCD", json={"question": "Une question"}
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["donnees"].type_utilisateur == type_utilisateur


def test_route_pose_question_identifie_comme_inconnu_le_type_d_utilisateur(
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
        "/api/pose_question?type_utilisateur=ABCD", json={"question": "Une question"}
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["donnees"].type_utilisateur == TypeUtilisateur.INCONNU


def test_route_pose_question_identifie_comme_inconnu_le_type_d_utilisateur_si_le_dechiffrement_echoue(
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
        "/api/pose_question?type_utilisateur=ABCD", json={"question": "Une question"}
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["donnees"].type_utilisateur == TypeUtilisateur.INCONNU


def test_route_pose_question_avec_un_id_de_conversation(
    un_serveur_de_test, un_adaptateur_de_chiffrement
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    interaction = Interaction(
        id=uuid.uuid4(),
        reponse_question=ReponseQuestion(
            reponse="réponse 1", question="question 1", paragraphes=[], violation=None
        ),
    )
    une_conversation = Conversation(interaction)
    adaptateur_base_de_donnees.sauvegarde_conversation(une_conversation)
    adaptateur_chiffrement = un_adaptateur_de_chiffrement()
    adaptateur_journal = AdaptateurJournalMemoire()
    service_albert = ServiceAlbertMemoire()
    service_albert.ajoute_reponse(
        ReponseQuestion(
            reponse="réponse 2", question="question 2", paragraphes=[], violation=None
        )
    )

    serveur = un_serveur_de_test(
        adaptateur_chiffrement=adaptateur_chiffrement,
        adaptateur_journal=adaptateur_journal,
        service_albert=service_albert,
        adaptateur_base_de_donnees=adaptateur_base_de_donnees,
    )

    client = TestClient(serveur)
    reponse = client.post(
        "/api/pose_question?type_utilisateur=ABCD",
        json={
            "question": "Une question",
            "conversation_id": str(une_conversation.id_conversation),
        },
    )

    reponse_recuperee = reponse.json()
    assert reponse_recuperee["conversation_id"] == str(une_conversation.id_conversation)
    assert reponse_recuperee["interaction_id"] is not None
    assert reponse_recuperee["reponse"] == "réponse 2"
