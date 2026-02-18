from abc import ABC, abstractmethod

from openai.types.chat import ChatCompletionMessageParam
from openai.types.chat.chat_completion import Choice

from schemas.albert import (
    RecherchePayload,
    ResultatRecherche,
    ReclassePayload,
    ReclasseReponse,
)


class ClientAlbert(ABC):
    @abstractmethod
    def recherche(self, payload: RecherchePayload) -> list[ResultatRecherche]:
        pass

    @abstractmethod
    def recupere_propositions(
        self, messages: list[ChatCompletionMessageParam], modele: str | None = None
    ) -> list[Choice]:
        pass

    @abstractmethod
    def reclasse(self, payload: ReclassePayload) -> ReclasseReponse:
        pass
