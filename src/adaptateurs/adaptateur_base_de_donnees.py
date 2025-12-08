from abc import ABC, abstractmethod
from typing import Optional
from schemas.retour_utilisatrice import RetourUtilisatrice, Interaction
from schemas.albert import ReponseQuestion


class AdaptateurBaseDeDonnees(ABC):
    @abstractmethod
    def sauvegarde_interaction(self, reponse_question: ReponseQuestion) -> str:
        pass

    @abstractmethod
    def ajoute_retour_utilisatrice(
        self, identifiant_interaction: str, retour: RetourUtilisatrice
    ) -> Optional[RetourUtilisatrice]:
        pass

    @abstractmethod
    def supprime_retour_utilisatrice(
        self, identifiant_interaction: str
    ) -> Optional[str]:
        pass

    @abstractmethod
    def recupere_interaction(
        self, identifiant_interaction: str
    ) -> Optional[Interaction]:
        pass

    @abstractmethod
    def ferme_connexion(self) -> None:
        pass
