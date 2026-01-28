from abc import ABC, abstractmethod
from typing import Dict, Any, List


class AdaptateurSentry(ABC):
    @abstractmethod
    def capture_exception(self, exception: Exception) -> None:
        pass


class AdaptateurSentryMemoire(AdaptateurSentry):
    def __init__(self) -> None:
        self.exceptions_capturees: List[Exception] = []
        self.messages_captures: List[str] = []
        self.contextes: Dict[str, Dict[str, Any]] = {}
        self.utilisateur: Dict[str, Any] = {}

    def capture_exception(self, exception: Exception) -> None:
        self.exceptions_capturees.append(exception)
