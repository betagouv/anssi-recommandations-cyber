import uuid
from typing import Dict
from schemas.retour_utilisatrice import RetourUtilisatrice, Interaction
from schemas.reponses import ReponseQuestion
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
    ) -> bool:
        if identifiant_interaction not in self._interactions:
            return False

        interaction = self._interactions[identifiant_interaction]
        interaction_mise_a_jour = Interaction(
            reponse_question=interaction.reponse_question, retour_utilisatrice=retour
        )
        self._interactions[identifiant_interaction] = interaction_mise_a_jour
        return True

    def obtient_statistiques(self) -> Dict[str, int]:
        total_interactions = len(self._interactions)
        total_retours = 0
        pouces_leves = 0

        for interaction in self._interactions.values():
            if interaction.retour_utilisatrice is not None:
                total_retours += 1
                if interaction.retour_utilisatrice.pouce_leve:
                    pouces_leves += 1

        return {
            "total_interactions": total_interactions,
            "total_retours": total_retours,
            "pouces_leves": pouces_leves,
        }

    def ferme_connexion(self) -> None:
        self._interactions.clear()
