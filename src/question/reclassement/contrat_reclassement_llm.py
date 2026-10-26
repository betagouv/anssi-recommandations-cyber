from collections.abc import Iterable

from schemas.albert import Paragraphe
from question.reclassement.unites_source import unites_du_paragraphe

CATEGORIES_SANS_PREUVE = (
    "hors_sujet",
    "dans_la_thematique_sans_apport",
    "element_de_reponse",
)
PORTEES_PREUVE = ("generale", "specifique_demandee", "specifique_non_demandee")
RELATIONS = ("directe", "indirecte")
APPORTS = (
    "reponse_centrale",
    "explication_directe",
    "principe_direct",
    "navigation_ou_simple_illustration",
)
DEGRES_PAR_APPORT = {
    "reponse_centrale": 3,
    "explication_directe": 2,
    "principe_direct": 1,
}
APPORTS_PROBANTS = tuple(DEGRES_PAR_APPORT)


def _chaine_parmi(valeurs: Iterable[str]) -> dict:
    return {"type": "string", "enum": list(valeurs)}


def _objet_ferme(proprietes: dict[str, dict]) -> dict:
    return {
        "type": "object",
        "properties": proprietes,
        "required": list(proprietes),
        "additionalProperties": False,
    }


def _schema_candidat_sans_preuve() -> dict:
    return _objet_ferme(
        {
            "categorie": _chaine_parmi(CATEGORIES_SANS_PREUVE),
            "relation": _chaine_parmi(RELATIONS),
            "portee": _chaine_parmi(PORTEES_PREUVE),
            "apport": _chaine_parmi(APPORTS),
        }
    )


def _schema_candidat_preuve(unites_substantielles: list[int]) -> dict:
    return _objet_ferme(
        {
            "categorie": {"type": "string", "const": "preuve_principale"},
            "relation": {"type": "string", "const": "directe"},
            "portee": _chaine_parmi(PORTEES_PREUVE),
            "apport": _chaine_parmi(APPORTS_PROBANTS),
            "unite_probante": {"type": "integer", "enum": unites_substantielles},
        }
    )


def _branches_candidat(paragraphe: Paragraphe) -> list[dict]:
    unites_substantielles = [
        indice
        for indice, unite in enumerate(unites_du_paragraphe(paragraphe), 1)
        if unite.est_substantielle
    ]
    branches = [_schema_candidat_sans_preuve()]
    if unites_substantielles:
        branches.append(_schema_candidat_preuve(unites_substantielles))
    return branches


def schema_classification(paragraphes: list[Paragraphe], premier_id: int) -> dict:
    candidats = {
        str(identifiant): {"anyOf": _branches_candidat(paragraphe)}
        for identifiant, paragraphe in enumerate(paragraphes, premier_id)
    }
    return _objet_ferme({"candidats": _objet_ferme(candidats)})


def evaluations_de_classification(
    resultat: dict, paragraphes: list[Paragraphe], premier_id: int
) -> list[dict]:
    evaluations = []
    for identifiant in range(premier_id, premier_id + len(paragraphes)):
        classification = resultat["candidats"][str(identifiant)]
        evaluation = {
            "id": identifiant,
            "categorie": classification["categorie"],
            "relation": classification["relation"],
            "portee_preuve": classification["portee"],
            "apport": classification["apport"],
            "degre_pertinence": DEGRES_PAR_APPORT.get(classification["apport"], 0),
        }
        if classification["categorie"] == "preuve_principale":
            evaluation["unite_probante"] = classification["unite_probante"]
        evaluations.append(evaluation)
    return evaluations
