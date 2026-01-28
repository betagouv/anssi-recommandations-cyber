from abc import ABC, abstractmethod
from typing import Dict, Any, List
import sentry_sdk
from configuration import logging, Sentry, recupere_configuration


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


class AdaptateurSentryStandard(AdaptateurSentry):
    @staticmethod
    def init(configuration: Sentry):
        sentry_sdk.init(dsn=configuration.dsn, environment=configuration.environnement)

    def capture_exception(self, exception: Exception) -> None:
        pass
        # sentry_sdk.capture_message("Hello Sentry!")


def fabrique_adaptateur_sentry() -> AdaptateurSentry:
    configuration = recupere_configuration().sentry
    logging.info(f"Configuration Sentry : {configuration.type_adaptateur_sentry}")
    if configuration.type_adaptateur_sentry == "standard":
        AdaptateurSentryStandard.init(configuration)
        return AdaptateurSentryStandard()
    return AdaptateurSentryMemoire()
