from __future__ import annotations
from typing import Dict, List
from managers.manager_historique import ManagerHistorique


class ManagerHistoriqueConcatenation(ManagerHistorique):
    def __init__(self) -> None:
        self._messages: List[Dict[str, str]] = []

    def ajoute_message_utilisateur(self, message: str) -> None:
        self._messages.append({"role": "user", "content": message})

    def ajoute_message_assistant(self, message: str) -> None:
        self._messages.append({"role": "assistant", "content": message})

    def recuperer_messages(self) -> List[Dict[str, str]]:
        return list(self._messages)
