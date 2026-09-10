from abc import ABC, abstractmethod
from typing import Callable, NamedTuple


class ErreurTechniqueSurvenue(NamedTuple):
    exception: Exception
    contexte: str


class BusEvenements(ABC):
    @abstractmethod
    def souscris(
        self, type_evenement: type, gestionnaire: Callable[..., None]
    ) -> None:
        pass

    @abstractmethod
    def publie(self, evenement: object) -> None:
        pass


class BusEvenementsEnMemoire(BusEvenements):
    def __init__(self) -> None:
        self._gestionnaires: dict[type, list[Callable[..., None]]] = {}

    def souscris(
        self, type_evenement: type, gestionnaire: Callable[..., None]
    ) -> None:
        self._gestionnaires.setdefault(type_evenement, []).append(gestionnaire)

    def publie(self, evenement: object) -> None:
        for gestionnaire in self._gestionnaires.get(type(evenement), []):
            gestionnaire(evenement)


def publie_erreur_technique(
    bus_evenements: BusEvenements | None, exception: Exception, contexte: str
) -> None:
    if bus_evenements is not None:
        bus_evenements.publie(
            ErreurTechniqueSurvenue(exception=exception, contexte=contexte)
        )


_bus = BusEvenementsEnMemoire()


def fabrique_bus_evenements() -> BusEvenements:
    return _bus