import json
from concurrent.futures import Future, as_completed
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.completion_create_params import ResponseFormat
from typing import cast

from adaptateurs.bus_evenements import BusEvenements, publie_erreur_technique
from schemas.albert import Paragraphe
from services.client_albert import ClientAlbert
from services.exceptions import (
    ErreurCommunicationModeleReclassement,
)
from services.unites_source import unites_du_paragraphe
from services.coordinateur_reclassement_parallele import (
    CoordinateurReclassementParallele,
    WorkflowReclassement,
)
from services.reclassement import Reclasseur, ResultatReclassement
from services.contrat_reclassement_llm import (
    CATEGORIES,
    CATEGORIES_SANS_PREUVE,
    DEGRES_PERTINENCE,
    PORTEES_PREUVE,
    RELATIONS,
    objet_json_sans_cles_dupliquees,
    schema_classification,
    valide_classification,
)
from services.selection_reclassement import applique_plage_probante, fusionne_preuves


class ReclasseurLLMEnParallele(Reclasseur):
    _CATEGORIES = CATEGORIES
    _CATEGORIES_SANS_PREUVE = CATEGORIES_SANS_PREUVE
    _DEGRES_PERTINENCE = DEGRES_PERTINENCE
    _PORTEES_PREUVE = PORTEES_PREUVE
    _RELATIONS = RELATIONS

    @staticmethod
    def _formate_candidats_avec_segments(
        paragraphes: list[Paragraphe],
        premier_id: int = 1,
    ) -> str:
        passages = []
        for identifiant, paragraphe in enumerate(paragraphes, premier_id):
            unites = unites_du_paragraphe(paragraphe)
            unites_formatees = "\n".join(
                f"[UNITE id={id_unite} page={unite.numero_page} "
                f"type_de_bloc={unite.type_de_bloc!r} "
                f"code_recommandation={unite.code_recommandation!r} "
                f"chemin_sections={' > '.join(unite.chemin_sections)!r} "
                f"url={unite.url!r}]\n{unite.contenu}\n[/UNITE]"
                for id_unite, unite in enumerate(unites, 1)
            )
            passages.append(
                f"[PASSAGE id={identifiant} rang_initial={paragraphe.rang_initial} "
                f"document={paragraphe.nom_document!r} "
                f"page={paragraphe.numero_page} "
                f"score_initial={paragraphe.score_similarite} "
                f"type_de_bloc={paragraphe.type_de_bloc!r} "
                f"code_recommandation={paragraphe.code_recommandation!r} "
                f"chemin_sections={' > '.join(paragraphe.chemin_sections)!r}]\n"
                f"{unites_formatees or '[AUCUNE_UNITE]'}\n[/PASSAGE]"
            )
        return "\n\n".join(passages)

    def __init__(
        self,
        client: ClientAlbert,
        prompt_classification: str,
        bus_evenements: BusEvenements,
        coordinateur: CoordinateurReclassementParallele | None = None,
        taille_lot: int = 5,
    ) -> None:
        if coordinateur is None:
            raise ValueError(
                "Le mode de reclassement parallèle requiert un coordinateur partagé."
            )
        self.client = client
        self.prompt_classification = prompt_classification
        self.bus_evenements = bus_evenements
        self.coordinateur = coordinateur
        self.taille_lot = taille_lot

    def reclasse(
        self, question: str, paragraphes: list[Paragraphe]
    ) -> ResultatReclassement:
        if not paragraphes:
            return ResultatReclassement([], [], aucune_source_utile=True)
        workflow: WorkflowReclassement | None = None
        try:
            workflow = self.coordinateur.ouvre_workflow()
            if (
                workflow.nombre_maximum_de_candidats is not None
                and len(paragraphes) > workflow.nombre_maximum_de_candidats
            ):
                raise ValueError(
                    "Le nombre de candidats dépasse la capacité du reclassement."
                )
            evaluations = self._classifie_en_parallele(workflow, question, paragraphes)
            preuves = [
                evaluation
                for evaluation in evaluations
                if evaluation["categorie"] == "preuve_principale"
            ]
            if not preuves:
                workflow.termine()
                return ResultatReclassement([], paragraphes, aucune_source_utile=True)
            ids_retenus = fusionne_preuves(paragraphes, preuves)
            workflow.termine()
            paragraphes_par_id = dict(enumerate(paragraphes, 1))
            evaluations_par_id = {
                evaluation["id"]: evaluation for evaluation in preuves
            }
            paragraphes_tries = [
                applique_plage_probante(
                    paragraphes_par_id[identifiant], evaluations_par_id[identifiant]
                )
                for identifiant in ids_retenus
            ]
            return ResultatReclassement(paragraphes_tries, paragraphes, not ids_retenus)
        except Exception as erreur:
            if workflow is not None:
                workflow.annule_en_attente()
                workflow.termine()
            erreur_reclassement = ErreurCommunicationModeleReclassement(
                "Impossible de reclasser les paragraphes de la question posée."
            )
            publie_erreur_technique(
                self.bus_evenements, erreur_reclassement, "reclassement"
            )
            raise erreur_reclassement from erreur

    def _classifie_en_parallele(
        self,
        workflow: WorkflowReclassement,
        question: str,
        paragraphes: list[Paragraphe],
    ) -> list[dict]:
        debuts_lots = list(range(0, len(paragraphes), self.taille_lot))
        if len(debuts_lots) > workflow.nombre_maximum_d_appels:
            raise ValueError(
                "Le nombre de lots dépasse la capacité du workflow de reclassement."
            )
        futures: dict[Future, str] = {}

        def soumet_lot(debut: int) -> None:
            fin = min(debut + self.taille_lot, len(paragraphes))
            future = workflow.soumet(
                self._classifie_lot,
                question,
                paragraphes[debut:fin],
                debut + 1,
            )
            futures[future] = "classification"

        for debut in debuts_lots:
            soumet_lot(debut)

        evaluations: list[dict] = []
        while futures:
            future = next(as_completed(futures))
            futures.pop(future)
            resultat = future.result()
            evaluations.extend(resultat)
            workflow.verifie_succes()
        return sorted(evaluations, key=lambda evaluation: evaluation["id"])

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
                    "schema": self._schema_classification(
                        paragraphes,
                        premier_id,
                    ),
                },
            },
        )
        resultat = self._recupere_resultat(messages, format_reponse)
        return valide_classification(resultat, paragraphes, premier_id)

    @classmethod
    def _schema_classification(
        cls, paragraphes: list[Paragraphe], premier_id: int
    ) -> dict:
        return schema_classification(paragraphes, premier_id)

    def _recupere_resultat(
        self,
        messages: list[ChatCompletionMessageParam],
        format_reponse: ResponseFormat | None = None,
    ) -> dict:
        propositions = self.client.recupere_propositions(
            messages,
            temperature=0,
            format_reponse=format_reponse,
        )
        if not propositions or propositions[0].message.content is None:
            raise ValueError("Le modèle a retourné une réponse vide.")
        contenu = propositions[0].message.content
        if not isinstance(contenu, str) or not contenu.strip():
            raise ValueError("Le modèle a retourné une réponse vide.")
        resultat = json.loads(
            contenu, object_pairs_hook=objet_json_sans_cles_dupliquees
        )
        if not isinstance(resultat, dict):
            raise ValueError("La réponse du modèle doit être un objet JSON.")
        return resultat
