import json
from pathlib import Path
from typing import Optional


class MappingReponsesMaitrisees:
    def __init__(self, mapping: dict[str, str]):
        self._mapping = mapping

    @classmethod
    def depuis_chemin(cls, chemin: Path) -> "MappingReponsesMaitrisees":
        mapping = json.loads(chemin.read_text(encoding="utf-8"))
        return cls(mapping)

    def resoudre(self, id_reponse: str) -> Optional[str]:
        return self._mapping.get(id_reponse)
