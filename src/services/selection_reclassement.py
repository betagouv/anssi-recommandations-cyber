from schemas.albert import Paragraphe
from services.unites_source import unites_du_paragraphe


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
    degre_maximal = max(preuve["degre_pertinence"] for preuve in eligibles)
    return sorted(
        preuve["id"]
        for preuve in eligibles
        if preuve["degre_pertinence"] == degre_maximal
    )


def applique_unite_probante(paragraphe: Paragraphe, evaluation: dict) -> Paragraphe:
    unite = unites_du_paragraphe(paragraphe)[evaluation["unite_probante"] - 1]
    return paragraphe.model_copy(
        update={"numero_page": unite.numero_page, "score_reclassement": 1.0}
    )
