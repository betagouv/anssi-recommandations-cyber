import uuid
from typing import Dict, Optional
from schemas.retour_utilisatrice import RetourUtilisatrice, Interaction
from schemas.client_albert import ReponseQuestion
from .adaptateur_base_de_donnees import AdaptateurBaseDeDonnees


class AdaptateurBaseDeDonneesEnMemoire(AdaptateurBaseDeDonnees):
    def __init__(self) -> None:
        self._interactions: Dict[str, Interaction] = {}

    def sauvegarde_interaction(self, reponse_question: ReponseQuestion) -> str:
        identifiant_interaction = str(uuid.uuid4())
        interaction = Interaction(
            reponse_question=reponse_question, retour_utilisatrice=None
        )
        self._interactions[identifiant_interaction] = interaction
        return identifiant_interaction

    def ajoute_retour_utilisatrice(
        self, identifiant_interaction: str, retour: RetourUtilisatrice
    ) -> Optional[RetourUtilisatrice]:
        if identifiant_interaction not in self._interactions:
            return None

        interaction = self._interactions[identifiant_interaction]
        interaction_mise_a_jour = Interaction(
            reponse_question=interaction.reponse_question, retour_utilisatrice=retour
        )
        self._interactions[identifiant_interaction] = interaction_mise_a_jour
        return retour

    def lit_interaction(self, identifiant_interaction: str) -> Optional[Interaction]:
        return self._interactions.get(identifiant_interaction)

    def ferme_connexion(self) -> None:
        self._interactions.clear()
