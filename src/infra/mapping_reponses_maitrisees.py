import json
from pathlib import Path
from typing import Optional


class MappingReponsesMaitrisees:
    def __init__(self, chemin: Path):
        self._mapping: dict[str, str] = json.loads(chemin.read_text(encoding="utf-8"))

    def resoudre(self, id_reponse: str) -> Optional[str]:
        return self._mapping.get(id_reponse)
