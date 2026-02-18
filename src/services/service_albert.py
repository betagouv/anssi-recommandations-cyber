from typing import Optional, cast, NamedTuple

from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion import Choice

from configuration import Albert
from question.reformulateur_de_question import ReformulateurDeQuestion
from schemas.albert import (
    Paragraphe,
    RecherchePayload,
    ReponseQuestion,
    ReclassePayload,
)
from schemas.retour_utilisatrice import Conversation
from schemas.violations import (
    Violation,
    ViolationIdentite,
    ViolationThematique,
    ViolationMalveillance,
    ViolationMeconnaissance,
    REPONSE_PAR_DEFAUT,
)
from services.client_albert import ClientAlbert


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
        reformulateur: Optional[ReformulateurDeQuestion] = None,
    ) -> None:
        self.id_collection = configuration_service_albert.collection_id_anssi_lab
        self.reclassement_active = configuration_service_albert.reclassement_active
        self.modele_reclassement = configuration_service_albert.modele_reclassement
        self.taille_fenetre_historique = (
            configuration_service_albert.taille_fenetre_historique
        )
        self.prompt_systeme = prompts.prompt_systeme
        self.prompt_reclassement = prompts.prompt_reclassement
        self.client = client
        self.utilise_recherche_hybride = utilise_recherche_hybride
        self.reformulateur = reformulateur

    def recherche_paragraphes(self, question: str) -> list[Paragraphe]:
        methode_recherche = "hybrid" if self.utilise_recherche_hybride else "semantic"
        nombre_paragraphes_a_retourner = 20 if self.reclassement_active else 5
        payload = RecherchePayload(
            collections=[self.id_collection],
            k=nombre_paragraphes_a_retourner,
            prompt=question,
            method=methode_recherche,
        )

        donnees = self.client.recherche(payload)

        def _transforme_en_paragraphe(donnee):
            return Paragraphe(
                contenu=donnee.chunk.content,
                url=donnee.chunk.metadata.source_url,
                score_similarite=donnee.score,
                numero_page=donnee.chunk.metadata.page,
                nom_document=donnee.chunk.metadata.nom_document,
            )

        return list(map(_transforme_en_paragraphe, donnees))

    def pose_question(
        self,
        *,
        question: str,
        prompt: Optional[str] = None,
        conversation: Optional[Conversation] = None,
    ) -> ReponseQuestion:
        question_reformulee = None
        if self.reformulateur is not None:
            question_reformulee = self.reformulateur.reformule(
                question, conversation=conversation
            )
        question_pour_recherche = (
            question_reformulee if question_reformulee else question
        )
        recherche_paragraphes = self.recherche_paragraphes(question_pour_recherche)
        paragraphes = self.__effectue_reclassement(
            recherche_paragraphes, question_pour_recherche
        )
        propositions_albert = self.__effectue_recuperation_propositions(
            paragraphes, prompt, question_pour_recherche, conversation
        )

        (reponse, paragraphes, violation) = (
            self._recupere_reponse_paragraphes_et_violation(
                propositions_albert, paragraphes
            )
        )

        return ReponseQuestion(
            reponse=reponse,
            paragraphes=paragraphes,
            question=question,
            question_reformulee=question_reformulee,
            violation=violation,
        )

    def reclasse(self, payload: ReclassePayload):
        resultat_du_reclassement = self.client.reclasse(payload)

        resultats_reclassement_donnees = resultat_du_reclassement.data
        resultats_reclassement_donnees.sort(key=lambda data: data.score, reverse=True)
        index_tries = list(map(lambda d: d.index, resultats_reclassement_donnees))
        toutes_les_entrees = payload.input

        return {"paragraphes_tries": [toutes_les_entrees[i] for i in index_tries]}

    def __effectue_recuperation_propositions(
        self,
        paragraphes: list[Paragraphe],
        prompt: str | None,
        question: str,
        conversation: Conversation | None,
    ) -> list[Choice]:
        paragraphes_concatenes = "\n\n\n".join([p.contenu for p in paragraphes])

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
            interactions_limitees = conversation.interactions[
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
    ) -> list[Paragraphe]:
        if self.reclassement_active and len(paragraphes) > 0:
            prompt_reclassement_avec_question = self.prompt_reclassement.format(
                QUESTION=question
            )
            reclasse_payload = ReclassePayload(
                prompt=prompt_reclassement_avec_question,
                input=list(map(lambda p: p.contenu, paragraphes)),
                model=self.modele_reclassement,
            )
            reclassement = self.reclasse(reclasse_payload)

            contenus_tries = reclassement["paragraphes_tries"]
            reclassement_non_vide = len(contenus_tries) > 0
            if reclassement_non_vide:
                return [
                    next(p for p in paragraphes if p.contenu == contenu)
                    for contenu in contenus_tries
                ][:5]
            else:
                return paragraphes[:5]
        return paragraphes

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
