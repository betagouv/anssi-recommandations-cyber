from abc import ABC, abstractmethod
from typing import Dict, Any, List
import sentry_sdk

from configuration import logging, Sentry, recupere_configuration


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


class AdaptateurSentryStandard(AdaptateurSentry):
    @staticmethod
    def init(configuration: Sentry):
        sentry_sdk.init(dsn=configuration.dsn, environment=configuration.environnement)

    def capture_exception(self, exception: Exception) -> None:
        pass
        # sentry_sdk.capture_message("Hello Sentry!")

    def capture_message(self, message: str) -> None:
        pass
        # sentry_sdk.capture_message("Hello Sentry!")

    def definis_contexte(self, cle: str, contexte: Dict[str, Any]) -> None:
        pass


def fabrique_adaptateur_sentry() -> AdaptateurSentry:
    configuration = recupere_configuration().sentry
    logging.info(f"Configuration Sentry : {configuration.type_adaptateur_sentry}")
    if configuration.type_adaptateur_sentry == "standard":
        AdaptateurSentryStandard.init(configuration)
        return AdaptateurSentryStandard()
    return AdaptateurSentryMemoire()
