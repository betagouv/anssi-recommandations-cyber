import json
from collections.abc import Mapping
from typing import TypeVar

Identifiant = TypeVar("Identifiant", int, str)


def resultat_de_classification(
    classifications: Mapping[Identifiant, object],
) -> dict:
    return {
        "candidats": {
            str(identifiant): classification
            for identifiant, classification in classifications.items()
        }
    }


def reponse_classification_avec_identifiants_globaux(
    classifications: Mapping[Identifiant, object],
) -> str:
    return json.dumps(resultat_de_classification(classifications))


def classification_element_de_reponse(
    *,
    relation: str = "directe",
    portee: str = "generale",
    apport: str = "principe_direct",
) -> dict[str, str | int]:
    return {
        "categorie": "element_de_reponse",
        "relation": relation,
        "portee": portee,
        "apport": apport,
    }


def classification_preuve_principale(
    *,
    portee: str = "generale",
    apport: str = "principe_direct",
    unite_probante: int = 1,
) -> dict[str, str | int]:
    return {
        "categorie": "preuve_principale",
        "relation": "directe",
        "portee": portee,
        "apport": apport,
        "unite_probante": unite_probante,
    }
