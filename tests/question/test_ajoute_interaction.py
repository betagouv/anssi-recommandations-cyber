import datetime as dt

from adaptateurs.horloge import Horloge
from client_albert_de_test import ClientAlbertMemoire
from question.question import (
    ajoute_interaction,
    DemandeInteractionUtilisateur,
)
from schemas.type_utilisateur import TypeUtilisateur
from services.service_albert import Prompts


def test_retourne_none_si_la_conversation_n_existe_pas(une_configuration_complete):
    la_configuration, _, _, _ = une_configuration_complete()

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
    la_configuration, service_albert, _, _ = une_configuration_complete()
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
    la_configuration, service_albert, adaptateur_base_de_donnees, _ = (
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
    la_configuration, service_albert, adaptateur_base_de_donnees, _ = (
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
