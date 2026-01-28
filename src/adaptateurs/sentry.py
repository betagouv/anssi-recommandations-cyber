from abc import ABC, abstractmethod
from typing import Dict, Any, List


class AdaptateurSentry(ABC):
    @abstractmethod
    def capture_exception(self, exception: Exception) -> None:
        pass

    @abstractmethod
    def capture_message(self, message: str) -> None:
        pass

    @abstractmethod
    def definis_contexte(self, cle: str, contexte: Dict[str, Any]) -> None:
        pass


class AdaptateurSentryMemoire(AdaptateurSentry):
    def __init__(self) -> None:
        self.exceptions_capturees: List[Exception] = []
        self.messages_captures: List[str] = []
        self.contextes: Dict[str, Dict[str, Any]] = {}
        self.utilisateur: Dict[str, Any] = {}

    def capture_exception(self, exception: Exception) -> None:
        self.exceptions_capturees.append(exception)

    def capture_message(self, message: str) -> None:
        self.messages_captures.append(message)

    def definis_contexte(self, cle: str, contexte: Dict[str, Any]) -> None:
        self.contextes[cle] = contexte
