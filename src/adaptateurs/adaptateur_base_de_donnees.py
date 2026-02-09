from abc import ABC, abstractmethod
from uuid import UUID

from typing import Optional

from schemas.retour_utilisatrice import Interaction


class AdaptateurBaseDeDonnees(ABC):
    @abstractmethod
    def sauvegarde_interaction(self, interaction: Interaction) -> None:
        pass

    @abstractmethod
    def recupere_interaction(
        self, identifiant_interaction: UUID
    ) -> Optional[Interaction]:
        pass

    @abstractmethod
    def ferme_connexion(self) -> None:
        pass
