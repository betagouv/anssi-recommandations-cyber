from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import Choice
from pydantic import BaseModel
from typing import Optional, cast, NamedTuple, Union, Any

from adaptateurs.adaptateur_executeur_de_requetes import AdaptateurExecuteurDeRequetes
from configuration import Albert
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from question.reformulateur_de_question import ReformulateurDeQuestion
from schemas.albert import (
    Paragraphe,
    RecherchePayload,
    ReponseQuestion,
    ParagrapheReponseMaitrisee,
    ParagrapheReponseQuestion,
)
from schemas.retour_utilisatrice import Conversation
from schemas.violations import (
    Violation,
    ViolationIdentite,
    ViolationThematique,
    ViolationMalveillance,
    ViolationMeconnaissance,
    ViolationQuestionNonComprise,
    REPONSE_PAR_DEFAUT,
)
from services.client_albert import ClientAlbert
from services.reclasseur import (
    Reclasseur,
    ResultatReclassement,
)


class DocumentGuideMSC(BaseModel):
    libelle: str
    nomFichier: str


class ReponseGuideMSC(BaseModel):
    id: str
    nom: str
    description: str
    listeDocuments: list[DocumentGuideMSC]
    dateMiseAJour: str


def _filtre_reponses_maitrisees(
    paragraphes: list[Union[Paragraphe | ParagrapheReponseMaitrisee]],
    seuil: float,
) -> list[Union[Paragraphe | ParagrapheReponseMaitrisee]]:
    maitrisees: list[Union[Paragraphe | ParagrapheReponseMaitrisee]] = [
        p
        for p in paragraphes
        if isinstance(p, ParagrapheReponseMaitrisee) and p.score_reclassement >= seuil
    ]
    return maitrisees if maitrisees else paragraphes


class Prompts(NamedTuple):
    prompt_systeme: str
    prompt_reclassement: str


class ServiceAlbert:
    def __init__(
        self,
        configuration_service_albert: Albert.Service,  # type: ignore [name-defined]
        client: ClientAlbert,
        utilise_recherche_hybride: bool,
        prompts: Prompts,
        reformulateur: ReformulateurDeQuestion,
        mapping_reponses: MappingReponsesMaitrisees,
        reclasseur: Reclasseur,
        executeur_de_requetes: Optional[AdaptateurExecuteurDeRequetes],
    ) -> None:
        self.id_collection = configuration_service_albert.id_collection_anssi_lab
        self.id_collection_jeopardy = (
            configuration_service_albert.id_collection_anssi_lab_jeopardy
        )
        self.jeopardy_active = configuration_service_albert.jeopardy_active
        self.seuil_reponse_maitrisee = (
            configuration_service_albert.seuil_reponse_maitrisee
        )
        self.taille_fenetre_historique = (
            configuration_service_albert.taille_fenetre_historique
        )
        self.nombre_paragraphes = configuration_service_albert.nombre_paragraphes
        self.prompt_systeme = prompts.prompt_systeme
        self.client = client
        self.utilise_recherche_hybride = utilise_recherche_hybride
        self.reformulateur = reformulateur
        self.mapping_reponses = mapping_reponses
        self.reclasseur: Reclasseur = reclasseur
        self.executeur_de_requetes = executeur_de_requetes
        self.url_msc = configuration_service_albert.url_msc

    def recherche_paragraphes(self, question: str) -> list[Paragraphe]:
        methode_recherche = "hybrid" if self.utilise_recherche_hybride else "semantic"
        payload_classique = RecherchePayload(
            collection_ids=[self.id_collection],
            limit=self.nombre_paragraphes,
            prompt=question,
            method=methode_recherche,
        )

        def _transforme_en_paragraphe(donnee, rang):
            id_reponse = donnee.chunk.metadata.id_reponse

            if id_reponse:
                reponse_texte = self.mapping_reponses.resoudre(id_reponse)
                return ParagrapheReponseMaitrisee(
                    contenu=donnee.chunk.content,
                    url=donnee.chunk.metadata.source_url,
                    score_similarite=donnee.score,
                    numero_page=donnee.chunk.metadata.page,
                    nom_document=donnee.chunk.metadata.nom_document,
                    reponse=reponse_texte,
                    rang_initial=1,
                )

            return Paragraphe(
                contenu=donnee.chunk.content,
                url=donnee.chunk.metadata.source_url,
                score_similarite=donnee.score,
                numero_page=donnee.chunk.metadata.page,
                nom_document=donnee.chunk.metadata.nom_document,
                rang_initial=rang,
            )

        donnees_classiques = self.client.recherche(payload_classique)
        paragraphes_classiques = [
            _transforme_en_paragraphe(donnee, rang)
            for rang, donnee in enumerate(donnees_classiques, 1)
        ]

        if self.jeopardy_active:
            paragraphes_jeopardy = self.__recherche_dans_collection_jeopardy(question)
            paragraphes_fusionnes = paragraphes_classiques + paragraphes_jeopardy

            paragraphes_uniques = []
            contenus_vus = set()
            for p in paragraphes_fusionnes:
                if p.contenu not in contenus_vus:
                    paragraphes_uniques.append(p)
                    contenus_vus.add(p.contenu)

            return paragraphes_uniques
        else:
            return paragraphes_classiques

    def __recherche_dans_collection_jeopardy(self, question: str) -> list[Paragraphe]:
        methode_recherche = "hybrid" if self.utilise_recherche_hybride else "semantic"
        payload = RecherchePayload(
            collection_ids=[self.id_collection_jeopardy],
            limit=self.nombre_paragraphes,
            prompt=question,
            method=methode_recherche,
        )

        resultats_jeopardy = self.client.recherche_jeopardy(payload)

        if not resultats_jeopardy:
            return []

        paragraphes = []
        for rang, resultat in enumerate(resultats_jeopardy, 1):
            id_document = resultat.chunk.metadata.source_id_document
            id_chunk = resultat.chunk.metadata.source_id_chunk
            donnee = self.client.recherche_chunk_par_id(id_document, id_chunk)
            paragraphes.append(
                Paragraphe(
                    contenu=donnee.chunk.content,
                    url=donnee.chunk.metadata.source_url,
                    score_similarite=resultat.score,
                    numero_page=donnee.chunk.metadata.page,
                    nom_document=donnee.chunk.metadata.nom_document,
                    rang_initial=rang,
                )
            )
        return paragraphes

    def pose_question(
        self,
        *,
        question: str,
        prompt: Optional[str] = None,
        conversation: Optional[Conversation] = None,
    ) -> ReponseQuestion:
        question_reformulee = self.reformulateur.reformule(
            question, conversation=conversation
        )

        if question_reformulee == "QUESTION_NON_COMPRISE":
            violation = ViolationQuestionNonComprise()
            return ReponseQuestion(
                reponse=violation.reponse,
                paragraphes=[],
                question=question,
                question_reformulee=question_reformulee,
                violation=violation,
            )
        question_pour_recherche = (
            question_reformulee if question_reformulee else question
        )
        recherche_paragraphes = self.recherche_paragraphes(question_pour_recherche)
        resultat_reclassement = self.__effectue_reclassement(
            recherche_paragraphes, question_pour_recherche
        )
        if resultat_reclassement.aucune_source_utile:
            violation_meconnaissance = ViolationMeconnaissance()
            return ReponseQuestion(
                reponse=violation_meconnaissance.reponse,
                paragraphes=[],
                question=question,
                question_reformulee=question_reformulee,
                violation=violation_meconnaissance,
            )
        paragraphes = resultat_reclassement.paragraphes_retenus
        propositions_albert = self.__effectue_recuperation_propositions(
            paragraphes, prompt, question_pour_recherche, conversation
        )

        (reponse, paragraphes, violation_resultat) = (
            self._recupere_reponse_paragraphes_et_violation(
                propositions_albert, paragraphes
            )
        )

        return ReponseQuestion(
            reponse=reponse,
            paragraphes=(self._mappe_en_paragraphes_pour_la_reponse(paragraphes)),
            question=question,
            question_reformulee=question_reformulee,
            violation=violation_resultat,
        )

    def _mappe_en_paragraphes_pour_la_reponse(
        self, paragraphes_a_mapper: list[Paragraphe]
    ) -> list[Any]:
        guides_msc: list[ReponseGuideMSC] = (
            self.executeur_de_requetes.recupere(
                f"{self.url_msc}/api/guides", ReponseGuideMSC
            )
            if self.executeur_de_requetes
            else []
        )

        paragraphes = []
        for p in paragraphes_a_mapper:
            titre = ""
            date_mise_a_jour = ""
            for guide in guides_msc:
                doc = next(
                    (x for x in guide.listeDocuments if x.nomFichier == p.nom_document),
                    None,
                )
                if not doc:
                    continue
                titre = guide.nom
                date_mise_a_jour = guide.dateMiseAJour
                break
            paragraphes.append(
                ParagrapheReponseQuestion(
                    **p.model_dump(), titre=titre, date_mise_a_jour=date_mise_a_jour
                )
            )
        return paragraphes

    def __effectue_recuperation_propositions(
        self,
        paragraphes: list[Paragraphe],
        prompt: str | None,
        question: str,
        conversation: Conversation | None,
    ) -> list[Choice]:
        def _contenu_pour_llm(p: Paragraphe) -> str:
            return p.contexte_dans_le_document

        paragraphes_concatenes = "\n\n\n".join(
            [_contenu_pour_llm(p) for p in paragraphes]
        )

        prompt_systeme = prompt if prompt else self.prompt_systeme

        messages = self.__genere_les_messages_de_completion(
            conversation, paragraphes_concatenes, prompt_systeme, question
        )
        propositions_albert = self.client.recupere_propositions(messages, temperature=0)
        return propositions_albert

    def __genere_les_messages_de_completion(
        self,
        conversation: Conversation | None,
        paragraphes_concatenes: str,
        prompt_systeme: str,
        question: str,
    ) -> list[ChatCompletionMessageParam]:
        question_en_cours: ChatCompletionUserMessageParam = {
            "role": "user",
            "content": f"Question :\n{question}",
        }
        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": prompt_systeme.format(chunks=paragraphes_concatenes),
            },
        ]
        if conversation is not None:
            interactions_limitees = conversation.interactions_sans_violation[
                : self.taille_fenetre_historique
            ]
            for interaction in reversed(interactions_limitees):
                messages.extend(
                    [
                        {
                            "role": "user",
                            "content": f"Question :\n{interaction.reponse_question.question}",
                        },
                        {
                            "role": "assistant",
                            "content": interaction.reponse_question.reponse,
                        },
                    ]
                )

        messages.append(question_en_cours)
        return messages

    def __effectue_reclassement(
        self, paragraphes: list[Paragraphe], question: str
    ) -> ResultatReclassement:
        if len(paragraphes) > 0:
            resultat = self.reclasseur.reclasse(question, paragraphes)
            return ResultatReclassement(
                paragraphes_retenus=_filtre_reponses_maitrisees(
                    resultat.paragraphes_retenus,
                    self.seuil_reponse_maitrisee,
                ),
                tous_les_candidats=resultat.tous_les_candidats,
                aucune_source_utile=resultat.aucune_source_utile,
            )
        return ResultatReclassement(
            paragraphes_retenus=paragraphes,
            tous_les_candidats=paragraphes,
        )

    def _recupere_reponse_paragraphes_et_violation(
        self, propositions_albert: list[Choice], paragraphes: list[Paragraphe]
    ) -> tuple[str, list[Paragraphe], Violation | None]:
        def retourne_violation(v: Violation):
            return v.reponse, [], v

        reponse_presente = len(propositions_albert) > 0

        if reponse_presente:
            reponse_albert = cast(str, propositions_albert[0].message.content)
            if "ERREUR_IDENTITÉ" in reponse_albert:
                return retourne_violation(ViolationIdentite())
            elif "ERREUR_THÉMATIQUE" in reponse_albert:
                return retourne_violation(ViolationThematique())
            elif "ERREUR_MALVEILLANCE" in reponse_albert:
                return retourne_violation(ViolationMalveillance())
            elif "ERREUR_MECONNAISSANCE" in reponse_albert:
                return retourne_violation(ViolationMeconnaissance())
            return reponse_albert, paragraphes, None
        else:
            return REPONSE_PAR_DEFAUT, [], None
