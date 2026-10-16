from abc import ABC, abstractmethod

from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import Choice
from openai.types.chat.completion_create_params import ResponseFormat

from schemas.albert import (
    RecherchePayload,
    RechercheChunk,
    ResultatRecherche,
    ResultatRechercheJeopardy,
    ReclassePayload,
    ReclasseReponse,
)


class ClientAlbert(ABC):
    @abstractmethod
    def recherche(self, payload: RecherchePayload) -> list[ResultatRecherche]:
        pass

    @abstractmethod
    def recherche_jeopardy(
        self, payload: RecherchePayload
    ) -> list[ResultatRechercheJeopardy]:
        pass

    @abstractmethod
    def recherche_chunk_par_id(
        self, id_document: str, id_chunk: int
    ) -> ResultatRecherche:
        pass

    @abstractmethod
    def recupere_chunks_document(self, id_document: int) -> list[RechercheChunk]:
        pass

    @abstractmethod
    def recupere_propositions(
        self,
        messages: list[ChatCompletionMessageParam],
        modele: str | None = None,
        temperature: float | None = None,
        format_reponse: ResponseFormat | None = None,
    ) -> list[Choice]:
        pass

    @abstractmethod
    def reclasse(self, payload: ReclassePayload) -> ReclasseReponse:
        pass
