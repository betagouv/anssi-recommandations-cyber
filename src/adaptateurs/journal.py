from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Dict


class TypeEvenement(StrEnum):
    INTERACTION_CREEE = "INTERACTION_CREEE"


class AdaptateurJournal(ABC):
    @abstractmethod
    def consigne_evenement(self, type: TypeEvenement, donnees: Dict) -> None:
        pass


class AdaptateurJournalMemoire(AdaptateurJournal):
    def consigne_evenement(self, type: TypeEvenement, donnees: Dict) -> None:
        pass


def fabrique_adaptateur_journal() -> AdaptateurJournal:
    return AdaptateurJournalMemoire()
