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
from services.contexte_documents import texte_visible_description
from services.contrat_reclassement_llm import (
    ADEQUATIONS_DOCUMENT,
    APPORTS,
    CATEGORIES,
    CATEGORIES_SANS_PREUVE,
    DEGRES_PERTINENCE,
    PORTEES_PREUVE,
    RELATIONS,
    objet_json_sans_cles_dupliquees,
    schema_classification,
    schema_qualification_documents,
    valide_classification,
)
from services.selection_reclassement import applique_plage_probante, fusionne_preuves


class ReclasseurLLMEnParallele(Reclasseur):
    requiert_contexte_documents_msc = True
    _CATEGORIES = CATEGORIES
    _CATEGORIES_SANS_PREUVE = CATEGORIES_SANS_PREUVE
    _ADEQUATIONS_DOCUMENT = ADEQUATIONS_DOCUMENT
    _DEGRES_PERTINENCE = DEGRES_PERTINENCE
    _PORTEES_PREUVE = PORTEES_PREUVE
    _RELATIONS = RELATIONS
    _APPORTS = APPORTS

    @staticmethod
    def _formate_candidats_avec_segments(
        paragraphes: list[Paragraphe],
        premier_id: int = 1,
        identifiants_documents: dict[str, str] | None = None,
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
                f"id_document={identifiants_documents.get(paragraphe.nom_document, '') if identifiants_documents else ''} "
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
        prompt_qualification: str = "{QUESTION}\n{DOCUMENTS}",
    ) -> None:
        if coordinateur is None:
            raise ValueError(
                "Le mode de reclassement parallèle requiert un coordinateur partagé."
            )
        if not prompt_qualification.strip():
            raise ValueError("Le prompt de qualification des documents est requis.")
        self.client = client
        self.prompt_classification = prompt_classification
        self.prompt_qualification = prompt_qualification
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
            adequations_documents, evaluations = self._classifie_en_parallele(
                workflow, question, paragraphes
            )
            for evaluation in evaluations:
                evaluation["adequation_document"] = adequations_documents.get(
                    evaluation["id_document"], "indetermine"
                )
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
    ) -> tuple[dict[str, str], list[dict]]:
        identifiants_documents: dict[str, str] = {}
        contextes_documents: dict[str, tuple[str, str] | None] = {}
        documents_contradictoires: set[str] = set()
        for paragraphe in paragraphes:
            document = paragraphe.nom_document
            if document not in identifiants_documents:
                identifiants_documents[document] = f"D{len(identifiants_documents) + 1}"
            contexte = paragraphe.contexte_document_msc
            valeurs = (
                (contexte.nom, contexte.description)
                if contexte and contexte.nom and contexte.description
                else None
            )
            if document not in contextes_documents:
                contextes_documents[document] = valeurs
            elif valeurs is not None and document not in documents_contradictoires:
                existant = contextes_documents[document]
                if existant is None:
                    contextes_documents[document] = valeurs
                elif existant != valeurs:
                    contextes_documents[document] = None
                    documents_contradictoires.add(document)
        documents = {
            identifiant: {
                "nom_fichier": document,
                "nom": (contextes_documents[document] or ("", ""))[0],
                "description": (contextes_documents[document] or ("", ""))[1],
            }
            for document, identifiant in identifiants_documents.items()
        }
        debuts_lots = list(range(0, len(paragraphes), self.taille_lot))
        if len(debuts_lots) + 1 > workflow.nombre_maximum_d_appels:
            raise ValueError(
                "Le nombre de lots dépasse la capacité du workflow de reclassement."
            )
        futures: dict[Future, str] = {}
        future_qualification = workflow.soumet(
            self._qualifie_documents,
            question,
            documents,
        )
        futures[future_qualification] = "qualification"

        def soumet_lot(debut: int) -> None:
            fin = min(debut + self.taille_lot, len(paragraphes))
            future = workflow.soumet(
                self._classifie_lot,
                question,
                paragraphes[debut:fin],
                debut + 1,
                identifiants_documents,
            )
            futures[future] = "classification"

        for debut in debuts_lots:
            soumet_lot(debut)

        evaluations: list[dict] = []
        adequations_documents: dict[str, str] = {}
        while futures:
            future = next(as_completed(futures))
            type_appel = futures.pop(future)
            resultat = future.result()
            if type_appel == "qualification":
                adequations_documents = resultat
            else:
                evaluations.extend(resultat)
            workflow.verifie_succes()
        return adequations_documents, sorted(
            evaluations, key=lambda evaluation: evaluation["id"]
        )

    def _qualifie_documents(
        self, question: str, documents: dict[str, dict[str, str]]
    ) -> dict[str, str]:
        ids_documents = list(documents)
        documents_pour_qualification = {
            identifiant: {
                **document,
                "description": texte_visible_description(document["description"]),
            }
            for identifiant, document in documents.items()
        }
        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": self.prompt_qualification.format(
                    QUESTION=question,
                    DOCUMENTS=json.dumps(
                        documents_pour_qualification, ensure_ascii=False
                    ),
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
                    "schema": self._schema_qualification_documents(
                        documents_pour_qualification
                    ),
                },
            },
        )
        resultat = self._recupere_resultat(messages, format_reponse)
        if set(resultat) != set(ids_documents):
            raise ValueError("La qualification doit couvrir exactement les documents.")
        qualifications: dict[str, str] = {}
        for identifiant, adequation in resultat.items():
            if (
                not isinstance(adequation, str)
                or adequation not in self._ADEQUATIONS_DOCUMENT
            ):
                raise ValueError("La qualification du document est invalide.")
            if (
                not documents_pour_qualification[identifiant]["nom"]
                or not documents_pour_qualification[identifiant]["description"]
            ):
                if adequation != "indetermine":
                    raise ValueError(
                        "La qualification d'un document sans métadonnées doit rester indéterminée."
                    )
            qualifications[identifiant] = adequation
        return qualifications

    @classmethod
    def _schema_qualification_documents(
        cls, documents: dict[str, dict[str, str]]
    ) -> dict:
        return schema_qualification_documents(documents)

    def _classifie_lot(
        self,
        question: str,
        paragraphes: list[Paragraphe],
        premier_id: int,
        identifiants_documents: dict[str, str],
    ) -> list[dict]:
        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": self.prompt_classification.format(
                    QUESTION=question,
                    CANDIDATS=self._formate_candidats_avec_segments(
                        paragraphes, premier_id, identifiants_documents
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
        return valide_classification(
            resultat, paragraphes, premier_id, identifiants_documents
        )

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
