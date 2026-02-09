import uuid
from uuid import UUID

from typing import Dict, Optional

from schemas.retour_utilisatrice import Interaction, Conversation
from .adaptateur_base_de_donnees import AdaptateurBaseDeDonnees


class AdaptateurBaseDeDonneesEnMemoire(AdaptateurBaseDeDonnees):
    def __init__(self, id_interaction: str | None = None) -> None:
        self.id_interaction = id_interaction
        self._interactions: Dict[UUID, Interaction] = {}
        self._conversations: Dict[UUID, Conversation] = {}

    def sauvegarde_interaction(self, interaction: Interaction) -> None:
        self._interactions[interaction.id] = interaction
        return None

    def recupere_interaction(
        self, identifiant_interaction: UUID
    ) -> Optional[Interaction]:
        return self._interactions.get(identifiant_interaction)

    def ferme_connexion(self) -> None:
        self._interactions.clear()

    def recupere_conversation(self, id_conversation: uuid.UUID):
        return self._conversations.get(id_conversation)

    def sauvegarde_conversation(self, conversation: Conversation):
        self._conversations[conversation.id_conversation] = conversation
        return None
