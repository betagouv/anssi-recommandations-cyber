from typing import Dict, Optional
from uuid import UUID

from schemas.retour_utilisatrice import RetourUtilisatrice, Interaction
from .adaptateur_base_de_donnees import AdaptateurBaseDeDonnees


class AdaptateurBaseDeDonneesEnMemoire(AdaptateurBaseDeDonnees):
    def __init__(self, id_interaction: str | None = None) -> None:
        self.id_interaction = id_interaction
        self._interactions: Dict[UUID, Interaction] = {}

    def sauvegarde_interaction(self, interaction: Interaction) -> None:
        self._interactions[interaction.id] = interaction
        return None

    def ajoute_retour_utilisatrice(
        self, interaction: Interaction
    ) -> Optional[RetourUtilisatrice]:
        self._interactions[interaction.id] = interaction
        return interaction.retour_utilisatrice

    def supprime_retour_utilisatrice(self, identifiant_interaction: UUID) -> None:
        interaction = self.recupere_interaction(identifiant_interaction)

        if not interaction:
            return None

        interaction_mise_a_jour = Interaction(
            reponse_question=interaction.reponse_question,
            retour_utilisatrice=None,
            id=interaction.id,
        )
        self._interactions[identifiant_interaction] = interaction_mise_a_jour
        return None

    def recupere_interaction(
        self, identifiant_interaction: UUID
    ) -> Optional[Interaction]:
        return self._interactions.get(identifiant_interaction)

    def ferme_connexion(self) -> None:
        self._interactions.clear()
