import uuid

from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from adaptateurs.horloge import Horloge
from adaptateurs.journal import AdaptateurJournalMemoire
from question.question import (
    pose_question_utilisateur,
    ConfigurationQuestion,
    ResultatInteractionEnErreur,
    QuestionUtilisateur,
)
from schemas.albert import ReponseQuestion, Paragraphe
from schemas.type_utilisateur import TypeUtilisateur
from schemas.violations import ViolationMalveillance
from serveur_de_test import ServiceAlbertMemoire
import datetime as dt


def test_pose_question_retourne_un_resultat_d_interaction_en_erreur(
    un_adaptateur_de_chiffrement,
):
    service_albert = ServiceAlbertMemoire()
    service_albert.qui_leve_une_erreur_sur_pose_question()
    reponse = pose_question_utilisateur(
        ConfigurationQuestion(
            adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
            adaptateur_base_de_donnees=AdaptateurBaseDeDonneesEnMemoire(),
            adaptateur_journal=AdaptateurJournalMemoire(),
            service_albert=service_albert,
        ),
        QuestionUtilisateur(question="une question"),
        TypeUtilisateur.EXPERT_SSI,
    )

    assert isinstance(reponse, ResultatInteractionEnErreur)
    assert reponse.message_mqc == "Erreur lors de l’appel à Albert"
    assert reponse.erreur == "Erreur sur pose_question"


def test_pose_question_retourne_une_interaction(un_adaptateur_de_chiffrement):
    service_albert = ServiceAlbertMemoire()
    reponse_question = ReponseQuestion(
        reponse="La réponse d'MQC",
        paragraphes=[],
        question="une question",
        violation=None,
    )
    service_albert.ajoute_reponse(reponse_question)

    resultat_interaction = pose_question_utilisateur(
        ConfigurationQuestion(
            adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
            adaptateur_base_de_donnees=AdaptateurBaseDeDonneesEnMemoire(),
            adaptateur_journal=AdaptateurJournalMemoire(),
            service_albert=service_albert,
        ),
        QuestionUtilisateur(question="une question"),
        TypeUtilisateur.EXPERT_SSI,
    )

    assert resultat_interaction.id_interaction is not None
    assert resultat_interaction.interaction.reponse_question == reponse_question
    assert resultat_interaction.interaction.retour_utilisatrice is None


def test_ne_conserve_pas_les_paragraphes_en_cas_de_violation(
    un_adaptateur_de_chiffrement,
):
    service_albert = ServiceAlbertMemoire()
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

    resultat_interaction = pose_question_utilisateur(
        ConfigurationQuestion(
            adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
            adaptateur_base_de_donnees=AdaptateurBaseDeDonneesEnMemoire(),
            adaptateur_journal=AdaptateurJournalMemoire(),
            service_albert=service_albert,
        ),
        QuestionUtilisateur(question="une question"),
        TypeUtilisateur.EXPERT_SSI,
    )

    assert resultat_interaction.interaction.reponse_question.paragraphes == []


def test_pose_question_une_interaction_a_une_date(un_adaptateur_de_chiffrement):
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
    reponse = pose_question_utilisateur(
        ConfigurationQuestion(
            adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
            adaptateur_base_de_donnees=adaptateur_base_de_donnees,
            adaptateur_journal=AdaptateurJournalMemoire(),
            service_albert=service_albert,
        ),
        QuestionUtilisateur(question="une question"),
        TypeUtilisateur.EXPERT_SSI,
    )

    assert adaptateur_base_de_donnees.recupere_interaction(
        uuid.UUID(reponse.id_interaction)
    ).date_creation == dt.datetime(2026, 2, 15, 3, 4, 5)


def test_cree_une_conversation(un_adaptateur_de_chiffrement):
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

    reponse = pose_question_utilisateur(
        ConfigurationQuestion(
            adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
            adaptateur_base_de_donnees=adaptateur_base_de_donnees,
            adaptateur_journal=AdaptateurJournalMemoire(),
            service_albert=service_albert,
        ),
        QuestionUtilisateur(question="une question"),
        TypeUtilisateur.EXPERT_SSI,
    )

    conversation = adaptateur_base_de_donnees.recupere_conversation(
        reponse.id_conversation
    )
    assert conversation is not None
    assert len(conversation.interactions) == 1


def test_ajoute_une_interaction_a_une_conversation(
    un_adaptateur_de_chiffrement, un_constructeur_de_conversation
):
    premiere_interaction = dt.datetime(2026, 1, 15, 3, 4, 5)
    Horloge.frise(premiere_interaction)
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    conversation = un_constructeur_de_conversation().construis()
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)
    deuxieme_interaction = dt.datetime(2026, 3, 10, 3, 4, 5)
    Horloge.frise(deuxieme_interaction)
    service_albert = ServiceAlbertMemoire()
    service_albert.ajoute_reponse(
        ReponseQuestion(
            reponse="La réponse d'MQC",
            question="une question",
            paragraphes=[],
            violation=None,
        )
    )

    reponse = pose_question_utilisateur(
        ConfigurationQuestion(
            adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
            adaptateur_base_de_donnees=adaptateur_base_de_donnees,
            adaptateur_journal=AdaptateurJournalMemoire(),
            service_albert=service_albert,
        ),
        QuestionUtilisateur(
            question="une question", conversation=conversation.id_conversation
        ),
        TypeUtilisateur.EXPERT_SSI,
    )

    conversation = adaptateur_base_de_donnees.recupere_conversation(
        reponse.id_conversation
    )
    assert len(conversation.interactions) == 2
    assert conversation.interactions[0].date_creation == deuxieme_interaction
    assert conversation.interactions[1].date_creation == premiere_interaction
