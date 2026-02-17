import datetime as dt
import uuid

import pytest

from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from adaptateurs.horloge import Horloge
from adaptateurs.journal import AdaptateurJournalMemoire
from question.question import (
    cree_conversation,
    ConfigurationQuestion,
    ResultatConversationEnErreur,
    DemandeConversationUtilisateur,
    ajoute_retour_utilisatrice,
)
from schemas.albert import ReponseQuestion, Paragraphe
from schemas.retour_utilisatrice import (
    DonneesCreationRetourUtilisateur,
    RetourPositif,
    TagPositif,
    TagNegatif,
)
from schemas.type_utilisateur import TypeUtilisateur
from schemas.violations import ViolationMalveillance
from serveur_de_test import ServiceAlbertMemoire


def test_cree_conversation_retourne_un_resultat_de_conversation_en_erreur(
    une_configuration_complete,
):
    la_configuration, service_albert, _, _ = une_configuration_complete()
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
    la_configuration, service_albert, _, _ = une_configuration_complete()
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
    la_configuration, service_albert, _, _ = une_configuration_complete()
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
    la_configuration, service_albert, adaptateur_base_de_donnees, _ = (
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


@pytest.mark.parametrize("tag", [TagPositif.Conversation, TagNegatif.Conversation])
def test_peut_ajouter_un_tag_conversation_a_partir_de_la_seconde_interaction(
    tag,
    un_constructeur_de_conversation,
    un_constructeur_de_reponse_question,
    un_constructeur_d_interaction,
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    conversation = un_constructeur_de_conversation(
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("La réponse à la première question")
        .avec_une_question("La première question")
    ).construis()
    interaction = un_constructeur_d_interaction().construis()
    conversation.ajoute_interaction(interaction)
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)

    ajoute_retour_utilisatrice(
        DonneesCreationRetourUtilisateur(
            id_interaction=str(interaction.id),
            retour=RetourPositif(commentaire="Très utile", tags=[tag]),
            id_conversation=str(conversation.id_conversation),
        ),
        adaptateur_base_de_donnees,
    )

    assert interaction.retour_utilisatrice.tags[0] == tag


@pytest.mark.parametrize("tag", [TagPositif.Conversation, TagNegatif.Conversation])
def test_ne_peut_pas_ajouter_un_tag_conversation_avant_la_deuxieme_interaction(
    tag,
    un_constructeur_de_conversation,
    un_constructeur_de_reponse_question,
    un_constructeur_d_interaction,
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    conversation = un_constructeur_de_conversation(
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("La réponse à la première question")
        .avec_une_question("La première question")
    ).construis()

    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)

    ajoute_retour_utilisatrice(
        DonneesCreationRetourUtilisateur(
            id_interaction=str(conversation.interactions[0].id),
            retour=RetourPositif(commentaire="Très utile", tags=[tag]),
            id_conversation=str(conversation.id_conversation),
        ),
        adaptateur_base_de_donnees,
    )

    assert len(conversation.interactions[0].retour_utilisatrice.tags) == 0
