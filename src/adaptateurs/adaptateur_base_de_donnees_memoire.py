from uuid import UUID

from typing import Dict, Optional

from schemas.retour_utilisatrice import Interaction
from .adaptateur_base_de_donnees import AdaptateurBaseDeDonnees


class AdaptateurBaseDeDonneesEnMemoire(AdaptateurBaseDeDonnees):
    def __init__(self, id_interaction: str | None = None) -> None:
        self.id_interaction = id_interaction
        self._interactions: Dict[UUID, Interaction] = {}

    def sauvegarde_interaction(self, interaction: Interaction) -> None:
        self._interactions[interaction.id] = interaction
        return None

    def recupere_interaction(
        self, identifiant_interaction: UUID
    ) -> Optional[Interaction]:
        return self._interactions.get(identifiant_interaction)

    def ferme_connexion(self) -> None:
        self._interactions.clear()
