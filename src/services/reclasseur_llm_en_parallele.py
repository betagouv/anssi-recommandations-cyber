from concurrent.futures import as_completed

from adaptateurs.bus_evenements import BusEvenements
from question.reclassement.reclasseur_llm_par_lots import ReclasseurLLMParLots
from schemas.albert import Paragraphe
from services.client_albert import ClientAlbert
from services.coordinateur_reclassement_parallele import (
    CoordinateurReclassementParallele,
)


class ReclasseurLLMEnParallele(ReclasseurLLMParLots):
    def __init__(
        self,
        client: ClientAlbert,
        prompt_classification: str,
        bus_evenements: BusEvenements,
        coordinateur: CoordinateurReclassementParallele,
        taille_lot: int = 5,
    ) -> None:
        super().__init__(client, prompt_classification, bus_evenements, taille_lot)
        self.coordinateur = coordinateur

    def _classifie_lots(
        self, question: str, paragraphes: list[Paragraphe]
    ) -> list[dict]:
        debuts = range(0, len(paragraphes), self.taille_lot)
        capacite = self.coordinateur.capacite
        if len(debuts) > capacite.nombre_maximum_d_appels_par_workflow:
            raise ValueError("Le nombre de lots dépasse la capacité du reclassement.")
        workflow = self.coordinateur.ouvre_workflow()
        try:
            classifications_de_lots = [
                workflow.soumet(
                    self._classifie_lot,
                    question,
                    paragraphes[debut : debut + self.taille_lot],
                    debut + 1,
                )
                for debut in debuts
            ]
            return [
                evaluation
                for classification_de_lot in as_completed(classifications_de_lots)
                for evaluation in classification_de_lot.result()
            ]
        finally:
            workflow.termine()
