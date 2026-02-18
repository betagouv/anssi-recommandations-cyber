import datetime as dt
import uuid

import pytest
from typing import cast

from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from adaptateurs.horloge import Horloge
from adaptateurs.journal import AdaptateurJournalMemoire, TypeEvenement
from question.question import (
    cree_conversation,
    ConfigurationQuestion,
    ResultatConversationEnErreur,
    DemandeConversationUtilisateur,
    ResultatConversation,
)
from schemas.albert import ReponseQuestion, Paragraphe
from schemas.type_utilisateur import TypeUtilisateur
from schemas.violations import (
    ViolationMalveillance,
    ViolationIdentite,
    ViolationThematique, ViolationMeconnaissance,
)
from serveur_de_test import ServiceAlbertMemoire


def test_cree_conversation_retourne_un_resultat_de_conversation_en_erreur(
    une_configuration_complete,
):
    la_configuration, service_albert, _, _, _ = une_configuration_complete()
    service_albert.qui_leve_une_erreur_sur_pose_question()
    resultat_conversation = cree_conversation(
        la_configuration,
        DemandeConversationUtilisateur(question="une question"),
        TypeUtilisateur.EXPERT_SSI,
    )

    assert isinstance(resultat_conversation, ResultatConversationEnErreur)
    assert resultat_conversation.message_mqc == "Erreur lors de l’appel à Albert"
    assert resultat_conversation.erreur == "Erreur sur pose_question"


def test_cree_conversation_retourne_une_conversation(une_configuration_complete):
    la_configuration, service_albert, _, _, _ = une_configuration_complete()
    reponse_question = ReponseQuestion(
        reponse="La réponse d'MQC",
        paragraphes=[],
        question="une question",
        violation=None,
    )
    service_albert.ajoute_reponse(reponse_question)

    resultat_interaction = cree_conversation(
        la_configuration,
        DemandeConversationUtilisateur(question="une question"),
        TypeUtilisateur.EXPERT_SSI,
    )

    assert resultat_interaction.id_interaction is not None
    assert resultat_interaction.interaction.reponse_question == reponse_question
    assert resultat_interaction.interaction.retour_utilisatrice is None


def test_ne_conserve_pas_les_paragraphes_en_cas_de_violation(
    une_configuration_complete,
):
    la_configuration, service_albert, _, _, _ = une_configuration_complete()
    reponse_question = ReponseQuestion(
        reponse="La réponse d'MQC",
        paragraphes=[
            Paragraphe(
                numero_page=1,
                url="https://example.com",
                contenu="un paragraphe",
                score_similarite=0.9,
                nom_document="un document",
            )
        ],
        question="une question",
        violation=ViolationMalveillance(),
    )
    service_albert.ajoute_reponse(reponse_question)

    resultat_interaction = cree_conversation(
        la_configuration,
        DemandeConversationUtilisateur(question="une question"),
        TypeUtilisateur.EXPERT_SSI,
    )

    assert resultat_interaction.interaction.reponse_question.paragraphes == []


def test_cree_conversation_une_interaction_a_une_date(un_adaptateur_de_chiffrement):
    Horloge.frise(dt.datetime(2026, 2, 15, 3, 4, 5))
    service_albert = ServiceAlbertMemoire()
    service_albert.ajoute_reponse(
        ReponseQuestion(
            reponse="La réponse d'MQC",
            question="une question",
            paragraphes=[],
            violation=None,
        )
    )
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    reponse = cree_conversation(
        ConfigurationQuestion(
            adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
            adaptateur_base_de_donnees=adaptateur_base_de_donnees,
            adaptateur_journal=AdaptateurJournalMemoire(),
            service_albert=service_albert,
        ),
        DemandeConversationUtilisateur(question="une question"),
        TypeUtilisateur.EXPERT_SSI,
    )

    assert adaptateur_base_de_donnees.recupere_interaction(
        uuid.UUID(reponse.id_interaction)
    ).date_creation == dt.datetime(2026, 2, 15, 3, 4, 5)


def test_cree_une_conversation(une_configuration_complete):
    Horloge.frise(dt.datetime(2026, 2, 15, 3, 4, 5))
    la_configuration, service_albert, adaptateur_base_de_donnees, _, _ = (
        une_configuration_complete()
    )
    service_albert.ajoute_reponse(
        ReponseQuestion(
            reponse="La réponse d'MQC",
            question="une question",
            paragraphes=[],
            violation=None,
        )
    )

    reponse = cree_conversation(
        la_configuration,
        DemandeConversationUtilisateur(question="une question"),
        TypeUtilisateur.EXPERT_SSI,
    )

    conversation = adaptateur_base_de_donnees.recupere_conversation(
        reponse.id_conversation
    )
    assert conversation is not None
    assert len(conversation.interactions) == 1


def test_cree_conversation_emet_un_evenement_journal_conversation_creee(
    une_configuration_complete, un_constructeur_de_paragraphe
) -> None:
    configuration, service_albert, _, adaptateur_journal, _ = (
        une_configuration_complete()
    )
    service_albert.ajoute_reponse(
        ReponseQuestion(
            reponse=" Je suis Albert, pour vous servir ",
            question="une question",
            paragraphes=[
                un_constructeur_de_paragraphe().avec_contenu("un contenu").construis()
            ],
            violation=None,
        )
    )

    conversation = cast(
        ResultatConversation,
        cree_conversation(
            configuration=configuration,
            question_utilisateur=DemandeConversationUtilisateur(
                question="une question"
            ),
            type_utilisateur=TypeUtilisateur.EXPERT_SSI,
        ),
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["type"] == TypeEvenement.CONVERSATION_CREEE
    assert (
        evenements[0]["donnees"].id_conversation
        == f"hache_{conversation.id_conversation}"
    )
    assert (
        evenements[0]["donnees"].id_interaction
        == f"hache_{conversation.interaction.id}"
    )
    assert evenements[0]["donnees"].longueur_question == 12
    assert evenements[0]["donnees"].longueur_reponse == 32
    assert evenements[0]["donnees"].longueur_paragraphes == 10
    assert evenements[0]["donnees"].type_utilisateur == TypeUtilisateur.EXPERT_SSI


def test_cree_conversation_emet_un_evenement_donnant_la_longueur_totale_des_paragraphes(
    une_configuration_complete, un_constructeur_de_paragraphe
):
    configuration, service_albert, _, adaptateur_journal, _ = (
        une_configuration_complete()
    )
    service_albert.ajoute_reponse(
        ReponseQuestion(
            reponse="La réponse d'MQC",
            question="une question",
            paragraphes=[
                un_constructeur_de_paragraphe().avec_contenu("Contenu A").construis(),
                un_constructeur_de_paragraphe().avec_contenu("Contenu B").construis(),
            ],
            violation=None,
        )
    )

    cree_conversation(
        configuration=configuration,
        question_utilisateur=DemandeConversationUtilisateur(question="une question"),
        type_utilisateur=TypeUtilisateur.EXPERT_SSI,
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["donnees"].longueur_paragraphes == 18


@pytest.mark.parametrize(
    "violation", [ViolationIdentite(), ViolationMalveillance(), ViolationThematique(), ViolationMeconnaissance()]
)
def test_cree_conversation_emet_un_evenement_journal_indiquant_la_detection_d_une_question_illegale(
    violation, une_configuration_complete
) -> None:
    configuration, service_albert, _, adaptateur_journal, _ = (
        une_configuration_complete()
    )
    service_albert.ajoute_reponse(
        ReponseQuestion(
            reponse="",
            question="une question",
            paragraphes=[],
            violation=violation,
        )
    )

    cree_conversation(
        configuration=configuration,
        question_utilisateur=DemandeConversationUtilisateur(question="une question"),
        type_utilisateur=TypeUtilisateur.EXPERT_SSI,
    )

    evenements = adaptateur_journal.les_evenements()
    assert len(evenements) == 2
    assert evenements[1]["type"] == TypeEvenement.VIOLATION_DETECTEE
    assert evenements[1]["donnees"].type_violation == violation.__class__.__name__
