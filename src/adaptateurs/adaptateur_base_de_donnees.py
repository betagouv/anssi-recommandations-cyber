from abc import ABC, abstractmethod
from typing import Dict, Optional
from schemas.retour_utilisatrice import RetourUtilisatrice, Interaction
from schemas.client_albert import ReponseQuestion


class AdaptateurBaseDeDonnees(ABC):
    @abstractmethod
    def sauvegarde_interaction(self, reponse_question: ReponseQuestion) -> str:
        pass

    @abstractmethod
    def ajoute_retour_utilisatrice(
        self, identifiant_interaction: str, retour: RetourUtilisatrice
    ) -> bool:
        pass

    @abstractmethod
    def lit_interaction(self, identifiant_interaction: str) -> Optional[Interaction]:
        pass

    @abstractmethod
    def obtient_statistiques(self) -> Dict[str, int]:
        pass

    @abstractmethod
    def ferme_connexion(self) -> None:
        pass
