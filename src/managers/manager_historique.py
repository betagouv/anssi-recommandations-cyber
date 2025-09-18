from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List


class ManagerHistorique(ABC):
    @abstractmethod
    def ajoute_message_utilisateur(self, message: str) -> None:
        pass

    @abstractmethod
    def ajoute_message_assistant(self, message: str) -> None:
        pass

    @abstractmethod
    def recuperer_messages(self) -> List[Dict[str, str]]:
        pass
