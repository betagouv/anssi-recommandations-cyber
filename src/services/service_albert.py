from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import Choice
from typing import Optional, cast, NamedTuple, Union

from configuration import Albert, TypeReclasseur
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from question.reformulateur_de_question import ReformulateurDeQuestion
from schemas.albert import (
    Paragraphe,
    RecherchePayload,
    ReponseQuestion,
    ParagrapheReponseMaitrisee,
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
    ReclasseurBGE,
    ReclasseurLLM,
    ResultatReclassement,
)


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
    ) -> None:
        self.id_collection = configuration_service_albert.id_collection_anssi_lab
        self.id_collection_jeopardy = (
            configuration_service_albert.id_collection_anssi_lab_jeopardy
        )
        self.reclassement_active = configuration_service_albert.reclassement_active
        self.jeopardy_active = configuration_service_albert.jeopardy_active
        self.modele_reclassement = configuration_service_albert.modele_reclassement
        self.seuil_reponse_maitrisee = (
            configuration_service_albert.seuil_reponse_maitrisee
        )
        self.taille_fenetre_historique = (
            configuration_service_albert.taille_fenetre_historique
        )
        self.nombre_paragraphes = configuration_service_albert.nombre_paragraphes
        self.prompt_systeme = prompts.prompt_systeme
        self.prompt_reclassement = prompts.prompt_reclassement
        self.client = client
        self.utilise_recherche_hybride = utilise_recherche_hybride
        self.reformulateur = reformulateur
        self.mapping_reponses = mapping_reponses
        self.reclasseur: Reclasseur = self.__fabrique_reclasseur(
            configuration_service_albert.type_reclasseur,
            self.prompt_reclassement,
        )

    def __fabrique_reclasseur(
        self, type_reclasseur: TypeReclasseur, prompt_reclassement: str
    ) -> Reclasseur:
        if type_reclasseur is TypeReclasseur.LLM:
            return ReclasseurLLM(self.client, prompt_reclassement)
        return ReclasseurBGE(
            self.client,
            self.modele_reclassement,
            self.prompt_reclassement,
            self.nombre_paragraphes,
        )

    def recherche_paragraphes(self, question: str) -> list[Paragraphe]:
        methode_recherche = "hybrid" if self.utilise_recherche_hybride else "semantic"
        nombre_paragraphes_a_retourner = (
            20 if self.reclassement_active else self.nombre_paragraphes
        )

        payload_classique = RecherchePayload(
            collection_ids=[self.id_collection],
            limit=10 if self.jeopardy_active else nombre_paragraphes_a_retourner,
            prompt=question,
            method=methode_recherche,
        )

        def _transforme_en_paragraphe(donnee):
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
                )

            return Paragraphe(
                contenu=donnee.chunk.content,
                url=donnee.chunk.metadata.source_url,
                score_similarite=donnee.score,
                numero_page=donnee.chunk.metadata.page,
                nom_document=donnee.chunk.metadata.nom_document,
            )

        donnees_classiques = self.client.recherche(payload_classique)
        paragraphes_classiques = [
            _transforme_en_paragraphe(donnee).model_copy(update={"rang_initial": rang})
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

            if self.reclassement_active:
                return paragraphes_uniques[:20]
            else:
                return paragraphes_uniques
        else:
            return paragraphes_classiques

    def __recherche_dans_collection_jeopardy(self, question: str) -> list[Paragraphe]:
        methode_recherche = "hybrid" if self.utilise_recherche_hybride else "semantic"
        payload = RecherchePayload(
            collection_ids=[self.id_collection_jeopardy],
            limit=10,
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
            paragraphes=paragraphes,
            question=question,
            question_reformulee=question_reformulee,
            violation=violation_resultat,
        )

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
        propositions_albert = self.client.recupere_propositions(messages)
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
        if self.reclassement_active and len(paragraphes) > 0:
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
