from schemas.albert import Paragraphe
from question.reclassement.unites_source import unites_du_paragraphe


PRIORITES_ADEQUATION_DOCUMENT = {"perimetre_demande": 0, "consacre_au_sujet": 1}


def _priorite_document(preuve: dict) -> int:
    return PRIORITES_ADEQUATION_DOCUMENT.get(preuve.get("adequation_document", ""), 2)


def fusionne_preuves(paragraphes: list[Paragraphe], preuves: list[dict]) -> list[int]:
    eligibles = [
        preuve
        for preuve in preuves
        if preuve["relation"] == "directe"
        and preuve["portee_preuve"] != "specifique_non_demandee"
        and preuve["apport"]
        in ("reponse_centrale", "explication_directe", "principe_direct")
    ]
    if not eligibles:
        return []
    meilleure_priorite = min(_priorite_document(preuve) for preuve in eligibles)
    eligibles = [
        preuve
        for preuve in eligibles
        if _priorite_document(preuve) == meilleure_priorite
    ]
    degre_maximal = max(preuve["degre_pertinence"] for preuve in eligibles)
    retenues = sorted(
        preuve["id"]
        for preuve in eligibles
        if preuve["degre_pertinence"] == degre_maximal
    )
    premier_id_du_document: dict[str, int] = {}
    for identifiant in retenues:
        premier_id_du_document.setdefault(
            paragraphes[identifiant - 1].nom_document, identifiant
        )
    return sorted(
        retenues,
        key=lambda identifiant: (
            premier_id_du_document[paragraphes[identifiant - 1].nom_document],
            identifiant,
        ),
    )


def applique_unite_probante(paragraphe: Paragraphe, evaluation: dict) -> Paragraphe:
    unite = unites_du_paragraphe(paragraphe)[evaluation["unite_probante"] - 1]
    return paragraphe.model_copy(
        update={"numero_page": unite.numero_page, "score_reclassement": 1.0}
    )
