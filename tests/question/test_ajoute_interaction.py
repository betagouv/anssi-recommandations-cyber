from question.question import (
    ajoute_interaction,
    DemandeInteractionUtilisateur,
)
from schemas.type_utilisateur import TypeUtilisateur


def test_retourne_none_si_la_conversation_n_existe_pas(une_configuration_complete):
    la_configuration = une_configuration_complete()

    resultat_interaction = ajoute_interaction(
        la_configuration,
        question_utilisateur=DemandeInteractionUtilisateur(
            question="une question ?", conversation="id-conversation-inconnu"
        ),
        type_utilisateur=TypeUtilisateur.ANSSI,
    )

    assert resultat_interaction.message_mqc == "La conversation demandée n'existe pas"
