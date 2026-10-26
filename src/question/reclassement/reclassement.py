from abc import ABC, abstractmethod
from typing import NamedTuple

from schemas.albert import Paragraphe


class ResultatReclassement(NamedTuple):
    paragraphes_retenus: list[Paragraphe]
    tous_les_candidats: list[Paragraphe]
    aucune_source_utile: bool = False


class Reclasseur(ABC):
    @abstractmethod
    def reclasse(
        self, question: str, paragraphes: list[Paragraphe]
    ) -> ResultatReclassement:
        pass
