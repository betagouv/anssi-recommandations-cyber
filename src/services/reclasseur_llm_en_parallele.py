import json
from concurrent.futures import Future, as_completed
from typing import cast

from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.completion_create_params import ResponseFormat

from adaptateurs.bus_evenements import BusEvenements
from schemas.albert import Paragraphe
from services.client_albert import ClientAlbert
from services.contrat_reclassement_llm import schema_qualification_documents
from services.coordinateur_reclassement_parallele import (
    CoordinateurReclassementParallele,
)
from services.reclasseur_llm_par_lots import ReclasseurLLMParLots


def _attends_la_fin_ou_la_premiere_erreur(appels: list[Future]) -> None:
    for appel_termine in as_completed(appels):
        appel_termine.result()


class ReclasseurLLMEnParallele(ReclasseurLLMParLots):
    def __init__(
        self,
        client: ClientAlbert,
        prompt_classification: str,
        bus_evenements: BusEvenements,
        coordinateur: CoordinateurReclassementParallele,
        prompt_qualification: str,
        taille_lot: int = 5,
    ) -> None:
        super().__init__(client, prompt_classification, bus_evenements, taille_lot)
        self.coordinateur = coordinateur
        self.prompt_qualification = prompt_qualification

    def _classifie_lots(
        self, question: str, paragraphes: list[Paragraphe]
    ) -> list[dict]:
        debuts = range(0, len(paragraphes), self.taille_lot)
        capacite = self.coordinateur.capacite
        if len(debuts) + 1 > capacite.nombre_maximum_d_appels_par_workflow:
            raise ValueError("Le nombre de lots dépasse la capacité du reclassement.")
        identifiants_documents, documents = self._prepare_documents(paragraphes)
        workflow = self.coordinateur.ouvre_workflow()
        try:
            qualification_des_documents = workflow.soumet(
                self._qualifie_documents, question, documents
            )
            classifications_de_lots = [
                workflow.soumet(
                    self._classifie_lot,
                    question,
                    paragraphes[debut : debut + self.taille_lot],
                    debut + 1,
                )
                for debut in debuts
            ]
            _attends_la_fin_ou_la_premiere_erreur(
                [qualification_des_documents, *classifications_de_lots]
            )
            adequation_par_identifiant_document = qualification_des_documents.result()
            adequation_par_nom_document = {
                nom_document: adequation_par_identifiant_document[identifiant]
                for nom_document, identifiant in identifiants_documents.items()
            }
            return [
                {
                    **evaluation,
                    "adequation_document": adequation_par_nom_document[
                        paragraphes[evaluation["id"] - 1].nom_document
                    ],
                }
                for classification_de_lot in classifications_de_lots
                for evaluation in classification_de_lot.result()
            ]
        finally:
            workflow.termine()

    @staticmethod
    def _prepare_documents(
        paragraphes: list[Paragraphe],
    ) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
        contextes = {
            paragraphe.nom_document: paragraphe.contexte_document_msc
            for paragraphe in paragraphes
        }
        identifiants = {nom: f"D{rang}" for rang, nom in enumerate(contextes, 1)}
        documents = {
            identifiants[nom]: {
                "nom_fichier": nom,
                "nom": contexte.nom if contexte else "",
                "description": contexte.description if contexte else "",
            }
            for nom, contexte in contextes.items()
        }
        return identifiants, documents

    def _qualifie_documents(
        self, question: str, documents: dict[str, dict[str, str]]
    ) -> dict[str, str]:
        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": self.prompt_qualification.format(
                    QUESTION=question,
                    DOCUMENTS=json.dumps(documents, ensure_ascii=False),
                ),
            }
        ]
        format_reponse = cast(
            ResponseFormat,
            {
                "type": "json_schema",
                "json_schema": {
                    "name": "qualification_guides",
                    "strict": True,
                    "schema": schema_qualification_documents(documents),
                },
            },
        )
        return self._recupere_resultat(messages, format_reponse)
