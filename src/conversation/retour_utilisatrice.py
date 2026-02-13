import uuid
from uuid import UUID

from adaptateurs import AdaptateurBaseDeDonnees
from schemas.retour_utilisatrice import (
    DonneesCreationRetourUtilisateur,
    RetourUtilisatrice,
    TagNegatif,
    TagPositif,
)


def ajoute_retour_utilisatrice(
    donnees_ajout_retour: DonneesCreationRetourUtilisateur,
    adaptateur_base_de_donnees: AdaptateurBaseDeDonnees,
) -> RetourUtilisatrice | None:
    if donnees_ajout_retour.id_conversation is not None:
        id_conversation = donnees_ajout_retour.id_conversation

        conversation = adaptateur_base_de_donnees.recupere_conversation(
            id_conversation=uuid.UUID(id_conversation)
        )

        interaction = list(
            filter(
                lambda i: str(i.id) == donnees_ajout_retour.id_interaction,
                conversation.interactions,
            )
        )[0]
        retour = donnees_ajout_retour.retour
        if len(conversation.interactions) < 2:
            retour.tags = [
                t
                for t in retour.tags
                if t != TagNegatif.Conversation and t != TagPositif.Conversation
            ]  # type: ignore[assignment]
    else:
        interaction = adaptateur_base_de_donnees.recupere_interaction(
            uuid.UUID(donnees_ajout_retour.id_interaction)
        )
        retour = donnees_ajout_retour.retour

    if not interaction:
        return None

    interaction.retour_utilisatrice = retour
    adaptateur_base_de_donnees.sauvegarde_interaction(interaction)
    return interaction.retour_utilisatrice


def supprime_retour_utilisatrice(
    identifiant_interaction: UUID, adaptateur_base_de_donnees: AdaptateurBaseDeDonnees
) -> None:
    interaction = adaptateur_base_de_donnees.recupere_interaction(
        identifiant_interaction
    )

    if not interaction:
        return None

    interaction.retour_utilisatrice = None
    adaptateur_base_de_donnees.sauvegarde_interaction(interaction)
    return None
