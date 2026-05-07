import uuid

from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from question.question import supprime_retour_utilisatrice
from schemas.retour_utilisatrice import RetourPositif


def test_supprime_retour_utilisatrice(
    un_constructeur_de_reponse_question,
    un_constructeur_de_conversation,
    un_constructeur_d_interaction,
):
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    interaction = (
        un_constructeur_d_interaction()
        .avec_un_retour_utilisatrice(RetourPositif())
        .construis()
    )
    conversation = (
        un_constructeur_de_conversation(un_constructeur_de_reponse_question())
        .avec_interaction(interaction)
        .construis()
    )
    adaptateur_base_de_donnees.sauvegarde_conversation(conversation)

    supprime_retour_utilisatrice(interaction.id, adaptateur_base_de_donnees)

    assert (
        adaptateur_base_de_donnees.recupere_interaction(
            interaction.id
        ).retour_utilisatrice
        is None
    )


def test_retourne_none_si_la_conversation_n_est_pas_trouvee():
    adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
    id_interaction_inconnue = uuid.uuid4()

    suppression = supprime_retour_utilisatrice(
        id_interaction_inconnue, adaptateur_base_de_donnees
    )

    assert suppression is None
