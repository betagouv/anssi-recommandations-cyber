from abc import ABC, abstractmethod

from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import Choice

from schemas.albert import (
    RecherchePayload,
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
    def recupere_propositions(
        self, messages: list[ChatCompletionMessageParam], modele: str | None = None
    ) -> list[Choice]:
        pass

    @abstractmethod
    def reclasse(self, payload: ReclassePayload) -> ReclasseReponse:
        pass
