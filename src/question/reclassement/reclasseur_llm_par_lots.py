import json
from abc import abstractmethod
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.completion_create_params import ResponseFormat
from typing import cast

from adaptateurs.bus_evenements import BusEvenements, publie_erreur_technique
from question.reclassement.reclassement import Reclasseur, ResultatReclassement
from schemas.albert import Paragraphe, UniteSource
from services.client_albert import ClientAlbert
from question.reclassement.contrat_reclassement_llm import (
    evaluations_de_classification,
    schema_classification,
)
from services.exceptions import ErreurCommunicationModeleReclassement
from question.reclassement.selection_reclassement import applique_unite_probante, fusionne_preuves
from question.reclassement.unites_source import unites_du_paragraphe


def _formate_unite(id_unite: int, unite: UniteSource) -> str:
    return (
        f"[UNITE id={id_unite} page={unite.numero_page} "
        f"type_de_bloc={unite.type_de_bloc!r} "
        f"code_recommandation={unite.code_recommandation!r} "
        f"chemin_sections={' > '.join(unite.chemin_sections)!r} "
        f"url={unite.url!r}]\n{unite.contenu}\n[/UNITE]"
    )


def _formate_passage(identifiant: int, paragraphe: Paragraphe) -> str:
    unites = "\n".join(
        _formate_unite(id_unite, unite)
        for id_unite, unite in enumerate(unites_du_paragraphe(paragraphe), 1)
    )
    return (
        f"[PASSAGE id={identifiant} rang_initial={paragraphe.rang_initial} "
        f"document={paragraphe.nom_document!r} "
        f"page={paragraphe.numero_page} "
        f"score_initial={paragraphe.score_similarite} "
        f"type_de_bloc={paragraphe.type_de_bloc!r} "
        f"code_recommandation={paragraphe.code_recommandation!r} "
        f"chemin_sections={' > '.join(paragraphe.chemin_sections)!r}]\n"
        f"{unites or '[AUCUNE_UNITE]'}\n[/PASSAGE]"
    )


class ReclasseurLLMParLots(Reclasseur):
    @staticmethod
    def _formate_candidats_avec_segments(
        paragraphes: list[Paragraphe], premier_id: int = 1
    ) -> str:
        return "\n\n".join(
            _formate_passage(identifiant, paragraphe)
            for identifiant, paragraphe in enumerate(paragraphes, premier_id)
        )

    def __init__(
        self,
        client: ClientAlbert,
        prompt_classification: str,
        bus_evenements: BusEvenements,
        taille_lot: int = 5,
    ) -> None:
        self.client = client
        self.prompt_classification = prompt_classification
        self.bus_evenements = bus_evenements
        self.taille_lot = taille_lot

    def reclasse(
        self, question: str, paragraphes: list[Paragraphe]
    ) -> ResultatReclassement:
        if not paragraphes:
            return ResultatReclassement([], [], aucune_source_utile=True)

        try:
            evaluations = self._classifie_lots(question, paragraphes)
            return self._cree_resultat(paragraphes, evaluations)
        except Exception as erreur:
            erreur_reclassement = ErreurCommunicationModeleReclassement(
                "Impossible de reclasser les paragraphes de la question posée."
            )
            publie_erreur_technique(
                self.bus_evenements, erreur_reclassement, "reclassement"
            )
            raise erreur_reclassement from erreur

    def _cree_resultat(
        self, paragraphes: list[Paragraphe], evaluations: list[dict]
    ) -> ResultatReclassement:
        preuves = [
            evaluation
            for evaluation in evaluations
            if evaluation["categorie"] == "preuve_principale"
        ]
        if not preuves:
            return ResultatReclassement([], paragraphes, aucune_source_utile=True)

        ids_retenus = fusionne_preuves(preuves)
        paragraphes_par_id = dict(enumerate(paragraphes, 1))
        evaluations_par_id = {evaluation["id"]: evaluation for evaluation in preuves}
        paragraphes_tries = [
            applique_unite_probante(
                paragraphes_par_id[identifiant], evaluations_par_id[identifiant]
            )
            for identifiant in ids_retenus
        ]
        return ResultatReclassement(paragraphes_tries, paragraphes, not ids_retenus)

    @abstractmethod
    def _classifie_lots(
        self, question: str, paragraphes: list[Paragraphe]
    ) -> list[dict]:
        pass

    def _classifie_lot(
        self,
        question: str,
        paragraphes: list[Paragraphe],
        premier_id: int,
    ) -> list[dict]:
        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": self.prompt_classification.format(
                    QUESTION=question,
                    CANDIDATS=self._formate_candidats_avec_segments(
                        paragraphes, premier_id
                    ),
                ),
            }
        ]
        format_reponse = cast(
            ResponseFormat,
            {
                "type": "json_schema",
                "json_schema": {
                    "name": "classification_passages",
                    "strict": True,
                    "schema": schema_classification(paragraphes, premier_id),
                },
            },
        )
        resultat = self._recupere_resultat(messages, format_reponse)
        return evaluations_de_classification(resultat, paragraphes, premier_id)

    def _recupere_resultat(
        self,
        messages: list[ChatCompletionMessageParam],
        format_reponse: ResponseFormat,
    ) -> dict:
        propositions = self.client.recupere_propositions(
            messages, temperature=0, format_reponse=format_reponse
        )
        return json.loads(propositions[0].message.content or "")
