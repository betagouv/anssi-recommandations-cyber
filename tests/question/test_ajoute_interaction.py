from question.question import (
    ajoute_interaction,
    DemandeInteractionUtilisateur,
)
from schemas.type_utilisateur import TypeUtilisateur


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
