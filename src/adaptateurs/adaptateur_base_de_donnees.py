from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from schemas.retour_utilisatrice import RetourUtilisatrice, Interaction


class AdaptateurBaseDeDonnees(ABC):
    @abstractmethod
    def sauvegarde_interaction(self, interaction: Interaction) -> None:
        pass

    @abstractmethod
    def ajoute_retour_utilisatrice(
        self, interaction: Interaction
    ) -> Optional[RetourUtilisatrice]:
        pass

    @abstractmethod
    def supprime_retour_utilisatrice(self, interaction: Interaction) -> None:
        pass

    @abstractmethod
    def recupere_interaction(
        self, identifiant_interaction: UUID
    ) -> Optional[Interaction]:
        pass

    @abstractmethod
    def ferme_connexion(self) -> None:
        pass
