from abc import ABC, abstractmethod
from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import Choice
from typing import Optional, cast
from configuration import Albert
from schemas.albert import (
    Paragraphe,
    RecherchePayload,
    ReponseQuestion,
    ResultatRecherche,
    ReclassePayload,
    ReclasseReponse,
)
from schemas.violations import (
    Violation,
    ViolationIdentite,
    ViolationThematique,
    ViolationMalveillance,
    REPONSE_PAR_DEFAUT,
)


class ClientAlbert(ABC):
    @abstractmethod
    def recherche(self, payload: RecherchePayload) -> list[ResultatRecherche]:
        pass

    @abstractmethod
    def recupere_propositions(
        self, messages: list[ChatCompletionMessageParam]
    ) -> list[Choice]:
        pass

    @abstractmethod
    def reclasse(self, payload: ReclassePayload) -> ReclasseReponse:
        pass


class ServiceAlbert:
    def __init__(
        self,
        configuration: Albert.Service,  # type: ignore [name-defined]
        client: ClientAlbert,
        prompt_systeme: str,
        utilise_recherche_hybride: bool,
    ) -> None:
        self.id_collection = configuration.collection_id_anssi_lab
        self.PROMPT_SYSTEME = prompt_systeme
        self.client = client
        self.utilise_recherche_hybride = utilise_recherche_hybride

    def recherche_paragraphes(self, question: str) -> list[Paragraphe]:
        methode_recherche = "hybrid" if self.utilise_recherche_hybride else "semantic"
        payload = RecherchePayload(
            collections=[self.id_collection],
            k=5,
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
        self, question: str, prompt: Optional[str] = None
    ) -> ReponseQuestion:
        paragraphes = self.recherche_paragraphes(question)
        paragraphes_concatenes = "\n\n\n".join([p.contenu for p in paragraphes])

        reclasse_payload = ReclassePayload(
            prompt="reclasse les documents",
            input=list(map(lambda p: p.contenu, paragraphes)),
            model="un modele",
        )
        reclassement = self.reclasse(reclasse_payload)

        contenus_tries = reclassement["paragraphes_tries"]
        if len(contenus_tries) > 0:
            paragraphes = [
                next(p for p in paragraphes if p.contenu == contenu)
                for contenu in contenus_tries
            ][:5]

        prompt_systeme = prompt if prompt else self.PROMPT_SYSTEME

        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": prompt_systeme.format(chunks=paragraphes_concatenes),
            },
            {
                "role": "user",
                "content": f"Question :\n{question}",
            },
        ]
        propositions_albert = self.client.recupere_propositions(messages)
        (reponse, paragraphes, violation) = (
            self._recupere_reponse_paragraphes_et_violation(
                propositions_albert, paragraphes
            )
        )

        return ReponseQuestion(
            reponse=reponse,
            paragraphes=paragraphes,
            question=question,
            violation=violation,
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
            return reponse_albert, paragraphes, None
        else:
            return REPONSE_PAR_DEFAUT, [], None

    def reclasse(self, payload: ReclassePayload):
        resultat_du_reclassement = self.client.reclasse(payload)

        resultats_reclassement_donnees = resultat_du_reclassement.data
        resultats_reclassement_donnees.sort(key=lambda data: data.score, reverse=True)
        index_tries = list(map(lambda d: d.index, resultats_reclassement_donnees))
        toutes_les_entrees = payload.input

        return {"paragraphes_tries": [toutes_les_entrees[i] for i in index_tries]}
