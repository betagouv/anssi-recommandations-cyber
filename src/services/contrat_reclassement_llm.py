from schemas.albert import Paragraphe
from services.unites_source import premiere_unite_substantielle, unites_du_paragraphe


def objet_json_sans_cles_dupliquees(paires: list[tuple[str, object]]) -> dict:
    objet: dict = {}
    for cle, valeur in paires:
        if cle in objet:
            raise ValueError("La réponse JSON contient une clé dupliquée.")
        objet[cle] = valeur
    return objet


CATEGORIES = {
    "hors_sujet",
    "dans_la_thematique_sans_apport",
    "element_de_reponse",
    "preuve_principale",
}
CATEGORIES_SANS_PREUVE = (
    "hors_sujet",
    "dans_la_thematique_sans_apport",
    "element_de_reponse",
)
DEGRES_PERTINENCE = (1, 2, 3)
PORTEES_PREUVE = ("generale", "specifique_demandee", "specifique_non_demandee")
RELATIONS = ("directe", "indirecte")
APPORTS = (
    "reponse_centrale",
    "explication_directe",
    "principe_direct",
    "navigation_ou_simple_illustration",
)


def schema_classification(paragraphes: list[Paragraphe], premier_id: int) -> dict:
    proprietes_candidats: dict[str, dict] = {}
    for identifiant, paragraphe in enumerate(paragraphes, premier_id):
        branches = [
            {
                "type": "object",
                "properties": {
                    "categorie": {
                        "type": "string",
                        "enum": list(CATEGORIES_SANS_PREUVE),
                    },
                    "relation": {
                        "type": "string",
                        "enum": list(RELATIONS),
                    },
                    "portee": {
                        "type": "string",
                        "enum": list(PORTEES_PREUVE),
                    },
                    "apport": {
                        "type": "string",
                        "enum": list(APPORTS),
                    },
                },
                "required": ["categorie", "relation", "portee", "apport"],
                "additionalProperties": False,
            }
        ]
        unites = unites_du_paragraphe(paragraphe)
        unites_substantielles = [
            indice
            for indice, unite in enumerate(unites, 1)
            if unite.type_de_bloc != "table_des_matieres"
        ]
        if unites_substantielles:
            branches.append(
                {
                    "type": "object",
                    "properties": {
                        "categorie": {
                            "type": "string",
                            "const": "preuve_principale",
                        },
                        "relation": {"type": "string", "const": "directe"},
                        "portee": {
                            "type": "string",
                            "enum": list(PORTEES_PREUVE),
                        },
                        "apport": {
                            "type": "string",
                            "enum": [
                                "reponse_centrale",
                                "explication_directe",
                                "principe_direct",
                            ],
                        },
                        "debut_unite": {
                            "type": "integer",
                            "enum": unites_substantielles,
                        },
                        "fin_unite": {
                            "type": "integer",
                            "enum": unites_substantielles,
                        },
                    },
                    "required": [
                        "categorie",
                        "relation",
                        "portee",
                        "apport",
                        "debut_unite",
                        "fin_unite",
                    ],
                    "additionalProperties": False,
                }
            )
        proprietes_candidats[str(identifiant)] = {"anyOf": branches}
    return {
        "type": "object",
        "properties": {
            "candidats": {
                "type": "object",
                "properties": proprietes_candidats,
                "required": list(proprietes_candidats),
                "additionalProperties": False,
            },
        },
        "required": ["candidats"],
        "additionalProperties": False,
    }


def valide_classification(
    resultat: dict,
    paragraphes: list[Paragraphe],
    premier_id: int,
) -> list[dict]:
    if set(resultat) != {"candidats"}:
        raise ValueError("Les champs de la classification sont invalides.")
    candidats = resultat["candidats"]
    ids_attendus = set(range(premier_id, premier_id + len(paragraphes)))
    if not isinstance(candidats, dict) or set(candidats) != {
        str(identifiant) for identifiant in ids_attendus
    }:
        raise ValueError("La classification doit couvrir exactement les candidats.")

    evaluations = []
    degres = {
        "reponse_centrale": 3,
        "explication_directe": 2,
        "principe_direct": 1,
    }
    for identifiant in sorted(ids_attendus):
        classification = candidats[str(identifiant)]
        if not isinstance(classification, dict):
            raise ValueError("Une classification doit être un objet.")
        categorie = classification.get("categorie")
        attendus_champs = {"categorie", "relation", "portee", "apport"}
        preuve = categorie == "preuve_principale"
        if preuve:
            attendus_champs |= {"debut_unite", "fin_unite"}
        if set(classification) != attendus_champs:
            raise ValueError("Les champs d'une classification sont invalides.")
        if categorie not in CATEGORIES:
            raise ValueError("Une catégorie de candidat est invalide.")
        if classification["relation"] not in RELATIONS:
            raise ValueError("La relation du candidat est invalide.")
        if classification["portee"] not in PORTEES_PREUVE:
            raise ValueError("La portée de la preuve est invalide.")
        if classification["apport"] not in APPORTS:
            raise ValueError("L'apport du candidat est invalide.")
        paragraphe = paragraphes[identifiant - premier_id]
        evaluation = {
            "id": identifiant,
            "categorie": categorie,
            "relation": classification["relation"],
            "portee_preuve": classification["portee"],
            "apport": classification["apport"],
            "degre_pertinence": degres.get(classification["apport"], 0),
        }
        if preuve:
            debut = classification["debut_unite"]
            fin = classification["fin_unite"]
            unites = unites_du_paragraphe(paragraphe)
            if (
                type(debut) is not int
                or type(fin) is not int
                or debut < 1
                or fin < debut
                or fin > len(unites)
                or unites[debut - 1].type_de_bloc == "table_des_matieres"
                or unites[fin - 1].type_de_bloc == "table_des_matieres"
                or premiere_unite_substantielle(unites, debut, fin) is None
                or classification["relation"] != "directe"
                or classification["apport"] == "navigation_ou_simple_illustration"
            ):
                raise ValueError("La plage d'une preuve est invalide.")
            evaluation["debut_unite"] = debut
            evaluation["fin_unite"] = fin
            evaluation["extrait_probant"] = "\n\n".join(
                unite.contenu for unite in unites[debut - 1 : fin]
            )
        evaluations.append(evaluation)
    return evaluations
