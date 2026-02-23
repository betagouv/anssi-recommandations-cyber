import datetime as dt

import pytest
from typing import cast

from adaptateurs.horloge import Horloge
from adaptateurs.journal import TypeEvenement
from client_albert_de_test import ClientAlbertMemoire
from question.question import (
    ajoute_interaction,
    DemandeInteractionUtilisateur,
    ResultatConversation,
    cree_conversation,
    DemandeConversationUtilisateur,
)
from schemas.type_utilisateur import TypeUtilisateur
from schemas.violations import (
    ViolationIdentite,
    ViolationMalveillance,
    ViolationThematique,
    ViolationMeconnaissance,
)
from services.service_albert import Prompts


def test_retourne_none_si_la_conversation_n_existe_pas(une_configuration_complete):
    la_configuration, _, _, _, _ = une_configuration_complete()

    resultat_interaction = ajoute_interaction(
        la_configuration,
        question_utilisateur=DemandeInteractionUtilisateur(
            question="une question ?", conversation="id-conversation-inconnu"
        ),
        type_utilisateur=TypeUtilisateur.ANSSI,
    )

    assert resultat_interaction.message_mqc == "La conversation demandée n'existe pas"


def test_ajoute_l_interaction_a_la_conversation(
    une_configuration_complete,
    un_constructeur_de_conversation,
    un_constructeur_d_interaction,
    un_constructeur_de_reponse_question,
):
    la_configuration, service_albert, _, _, _ = une_configuration_complete()
    une_conversation = un_constructeur_de_conversation().construis()
    une_interaction = (
        un_constructeur_d_interaction().avec_question("une question ? ").construis()
    )
    une_conversation.ajoute_interaction(une_interaction)
    la_configuration.adaptateur_base_de_donnees.sauvegarde_conversation(
        une_conversation
    )
    reponse_question = (
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("la réponse")
        .avec_une_question("une autre question ?")
        .construis()
    )
    service_albert.ajoute_reponse(reponse_question)

    resultat_interaction = ajoute_interaction(
        la_configuration,
        question_utilisateur=DemandeInteractionUtilisateur(
            question="une autre question ?",
            conversation=une_conversation.id_conversation,
        ),
        type_utilisateur=TypeUtilisateur.ANSSI,
    )

    assert resultat_interaction.reponse_question == reponse_question


def test_ajoute_une_interaction_a_une_conversation(
    une_configuration_complete,
    un_adaptateur_de_chiffrement,
    un_constructeur_de_conversation,
    un_constructeur_de_reponse_question,
):
    premiere_interaction = dt.datetime(2026, 1, 15, 3, 4, 5)
    Horloge.frise(premiere_interaction)
    la_configuration, service_albert, adaptateur_base_de_donnees, _, _ = (
        une_configuration_complete()
    )
    conversation = un_constructeur_de_conversation().construis()
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)
    deuxieme_interaction = dt.datetime(2026, 3, 10, 3, 4, 5)
    Horloge.frise(deuxieme_interaction)
    service_albert.ajoute_reponse(
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("La réponse d'MQC")
        .avec_une_question("une question")
        .construis()
    )

    reponse = ajoute_interaction(
        la_configuration,
        question_utilisateur=DemandeInteractionUtilisateur(
            question="une question", conversation=conversation.id_conversation
        ),
        type_utilisateur=TypeUtilisateur.EXPERT_SSI,
    )

    conversation_recuperee = adaptateur_base_de_donnees.recupere_conversation(
        reponse.id_conversation
    )
    assert len(conversation_recuperee.interactions) == 2
    assert conversation_recuperee.interactions[0].date_creation == deuxieme_interaction
    assert conversation_recuperee.interactions[1].date_creation == premiere_interaction


def test_interroge_albert_en_mode_conversationnel(
    un_service_albert_avec_un_client_memoire,
    une_configuration_complete,
    un_adaptateur_de_chiffrement,
    un_constructeur_de_conversation,
    un_constructeur_de_reponse_question,
):
    client_albert_memoire = ClientAlbertMemoire()
    service_albert = un_service_albert_avec_un_client_memoire(
        client_albert_memoire,
        Prompts(
            prompt_systeme=(
                "Vous êtes Alberito, un fan d'Albert. Utilisez ces documents:\n\n{chunks}"
            ),
            prompt_reclassement="Prompt de reclassement :\n\n{QUESTION}\n\n, fin prompt",
        ),
    )
    la_configuration, service_albert, adaptateur_base_de_donnees, _, _ = (
        une_configuration_complete(service_albert)
    )
    conversation = un_constructeur_de_conversation(
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("La réponse à la première question")
        .avec_une_question("La première question")
    ).construis()
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)

    ajoute_interaction(
        la_configuration,
        question_utilisateur=DemandeInteractionUtilisateur(
            question="Une seconde question", conversation=conversation.id_conversation
        ),
        type_utilisateur=TypeUtilisateur.EXPERT_SSI,
    )

    messages_recus = client_albert_memoire.messages_recus
    assert messages_recus == [
        {
            "role": "system",
            "content": "Vous êtes Alberito, un fan d'Albert. Utilisez ces documents:\n\n",
        },
        {
            "role": "user",
            "content": "Question :\nLa première question",
        },
        {
            "role": "assistant",
            "content": "La réponse à la première question",
        },
        {
            "role": "user",
            "content": "Question :\nUne seconde question",
        },
    ]


def test_ajoute_interaction_emet_un_evenement_journal_interaction_ajoutee(
    une_configuration_complete,
    un_constructeur_de_paragraphe,
    un_constructeur_de_reponse_question,
    un_constructeur_de_conversation,
) -> None:
    configuration, service_albert, adaptateur_base_de_donnees, adaptateur_journal, _ = (
        une_configuration_complete()
    )
    service_albert.ajoute_reponse(
        (
            un_constructeur_de_reponse_question()
            .donnant_en_reponse(" Je suis Albert, pour vous servir ")
            .avec_une_question("Une seconde question")
            .avec_les_paragraphes(
                [un_constructeur_de_paragraphe().avec_contenu("un contenu").construis()]
            )
            .construis()
        )
    )
    conversation = un_constructeur_de_conversation(
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("La réponse à la première question")
        .avec_une_question("La première question")
    ).construis()
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)

    interaction = cast(
        ResultatConversation,
        ajoute_interaction(
            configuration,
            question_utilisateur=DemandeInteractionUtilisateur(
                question="Une seconde question",
                conversation=conversation.id_conversation,
            ),
            type_utilisateur=TypeUtilisateur.EXPERT_SSI,
        ),
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["type"] == TypeEvenement.INTERACTION_AJOUTEE
    assert (
        evenements[0]["donnees"].id_conversation
        == f"hache_{conversation.id_conversation}"
    )
    assert (
        evenements[0]["donnees"].id_interaction == f"hache_{interaction.id_interaction}"
    )
    assert evenements[0]["donnees"].longueur_question == 20
    assert evenements[0]["donnees"].longueur_reponse == 32
    assert evenements[0]["donnees"].longueur_paragraphes == 10
    assert evenements[0]["donnees"].type_utilisateur == TypeUtilisateur.EXPERT_SSI


def test_ajoute_interaction_emet_un_evenement_donnant_la_longueur_totale_des_paragraphes(
    une_configuration_complete,
    un_constructeur_de_paragraphe,
    un_constructeur_de_reponse_question,
    un_constructeur_de_conversation,
):
    configuration, service_albert, adaptateur_base_de_donnees, adaptateur_journal, _ = (
        une_configuration_complete()
    )

    question = (
        un_constructeur_de_reponse_question()
        .donnant_en_reponse(" Je suis Albert, pour vous servir ")
        .avec_une_question("Une seconde question")
        .avec_les_paragraphes(
            [
                un_constructeur_de_paragraphe().avec_contenu("Contenu A").construis(),
                un_constructeur_de_paragraphe().avec_contenu("Contenu B").construis(),
            ]
        )
        .construis()
    )
    service_albert.ajoute_reponse(question)
    conversation = un_constructeur_de_conversation(
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("La réponse à la première question")
        .avec_une_question("La première question")
    ).construis()
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)

    (
        ResultatConversation,
        ajoute_interaction(
            configuration,
            question_utilisateur=DemandeInteractionUtilisateur(
                question="Une seconde question",
                conversation=conversation.id_conversation,
            ),
            type_utilisateur=TypeUtilisateur.EXPERT_SSI,
        ),
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["donnees"].longueur_paragraphes == 18


@pytest.mark.parametrize(
    "violation",
    [
        ViolationIdentite(),
        ViolationMalveillance(),
        ViolationThematique(),
        ViolationMeconnaissance(),
    ],
)
def test_ajoute_interaction_emet_un_evenement_journal_indiquant_la_detection_d_une_question_illegale(
    violation,
    une_configuration_complete,
    un_constructeur_de_conversation,
    un_constructeur_de_reponse_question,
) -> None:
    configuration, service_albert, adaptateur_base_de_donnees, adaptateur_journal, _ = (
        une_configuration_complete()
    )
    service_albert.ajoute_reponse(
        (
            un_constructeur_de_reponse_question()
            .donnant_en_reponse(" Je suis Albert, pour vous servir ")
            .avec_une_question("Une seconde question")
            .avec_une_violation(violation)
            .construis()
        )
    )
    conversation = un_constructeur_de_conversation(
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("La réponse à la première question")
        .avec_une_question("La première question")
    ).construis()
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)

    ajoute_interaction(
        configuration,
        question_utilisateur=DemandeInteractionUtilisateur(
            question="Une seconde question", conversation=conversation.id_conversation
        ),
        type_utilisateur=TypeUtilisateur.EXPERT_SSI,
    )

    evenements = adaptateur_journal.les_evenements()
    assert len(evenements) == 2
    assert evenements[1]["type"] == TypeEvenement.VIOLATION_DETECTEE
    assert evenements[1]["donnees"].type_violation == violation.__class__.__name__


def test_ajoute_interaction_emet_un_evenement_journal_avec_la_question_et_les_sources_en_mode_alpha_test(
    une_configuration_complete,
    un_constructeur_de_conversation,
    un_constructeur_de_reponse_question,
    un_constructeur_de_paragraphe,
    monkeypatch,
) -> None:
    configuration, service_albert, adaptateur_base_de_donnees, adaptateur_journal, _ = (
        une_configuration_complete()
    )
    service_albert.ajoute_reponse(
        (
            un_constructeur_de_reponse_question()
            .donnant_en_reponse(" Je suis Albert, pour vous servir ")
            .avec_une_question("Une seconde question")
            .avec_les_paragraphes(
                [
                    un_constructeur_de_paragraphe()
                    .a_la_page(12)
                    .dans_le_document("document_1.pdf")
                    .construis(),
                    un_constructeur_de_paragraphe()
                    .a_la_page(42)
                    .dans_le_document("document_2.pdf")
                    .construis(),
                ]
            )
            .construis()
        )
    )
    conversation = un_constructeur_de_conversation(
        un_constructeur_de_reponse_question()
        .donnant_en_reponse("La réponse à la première question")
        .avec_une_question("La première question")
    ).construis()
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)
    monkeypatch.setenv("ALPHA_TEST", "True")

    ajoute_interaction(
        configuration,
        question_utilisateur=DemandeInteractionUtilisateur(
            question="Une seconde question", conversation=conversation.id_conversation
        ),
        type_utilisateur=TypeUtilisateur.EXPERT_SSI,
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["donnees"].question == "Une seconde question"
    assert len(evenements[0]["donnees"].sources) == 2
    assert evenements[0]["donnees"].sources[0].nom_document == "document_1.pdf"
    assert evenements[0]["donnees"].sources[0].numero_page == 12
    assert evenements[0]["donnees"].sources[1].nom_document == "document_2.pdf"
    assert evenements[0]["donnees"].sources[1].numero_page == 42


def test_cree_conversation_emet_un_evenement_journal_avec_la_question_et_les_sources_en_mode_alpha_test(
    une_configuration_complete,
    un_constructeur_de_reponse_question,
    un_constructeur_de_paragraphe,
    monkeypatch,
) -> None:
    configuration, service_albert, adaptateur_base_de_donnees, adaptateur_journal, _ = (
        une_configuration_complete()
    )
    service_albert.ajoute_reponse(
        (
            un_constructeur_de_reponse_question()
            .donnant_en_reponse(" Je suis Albert, pour vous servir ")
            .avec_une_question("Une seconde question")
            .avec_les_paragraphes(
                [
                    un_constructeur_de_paragraphe()
                    .a_la_page(12)
                    .dans_le_document("document_1.pdf")
                    .construis(),
                    un_constructeur_de_paragraphe()
                    .a_la_page(42)
                    .dans_le_document("document_2.pdf")
                    .construis(),
                ]
            )
            .construis()
        )
    )
    monkeypatch.setenv("ALPHA_TEST", "True")

    cree_conversation(
        configuration,
        question_utilisateur=DemandeConversationUtilisateur(
            question="Une seconde question"
        ),
        type_utilisateur=TypeUtilisateur.EXPERT_SSI,
    )

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["donnees"].question == "Une seconde question"
    assert len(evenements[0]["donnees"].sources) == 2
    assert evenements[0]["donnees"].sources[0].nom_document == "document_1.pdf"
    assert evenements[0]["donnees"].sources[0].numero_page == 12
    assert evenements[0]["donnees"].sources[1].nom_document == "document_2.pdf"
    assert evenements[0]["donnees"].sources[1].numero_page == 42
