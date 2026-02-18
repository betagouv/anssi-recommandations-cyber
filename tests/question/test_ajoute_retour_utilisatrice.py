import pytest

from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from question.question import ajoute_retour_utilisatrice
from schemas.retour_utilisatrice import (
    TagPositif,
    TagNegatif,
    DonneesCreationRetourUtilisateur,
    RetourPositif,
)


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
