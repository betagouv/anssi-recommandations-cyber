from schemas.albert import Paragraphe
from services.unites_source import premiere_unite_substantielle, unites_du_paragraphe


def fusionne_preuves(paragraphes: list[Paragraphe], preuves: list[dict]) -> list[int]:
    priorites_document = {
        "perimetre_demande": 0,
        "consacre_au_sujet": 1,
        "general_ou_contextuel": 2,
        "indetermine": 2,
    }
    paragraphes_par_id = dict(enumerate(paragraphes, 1))
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
    priorite_documentale = min(
        priorites_document[preuve["adequation_document"]] for preuve in eligibles
    )
    eligibles = [
        preuve
        for preuve in eligibles
        if priorites_document[preuve["adequation_document"]] == priorite_documentale
    ]
    degre_maximal = max(preuve["degre_pertinence"] for preuve in eligibles)
    preuves_retenues = [
        preuve for preuve in eligibles if preuve["degre_pertinence"] == degre_maximal
    ]
    groupes_retenus: dict[str, list[dict]] = {}
    for preuve in preuves_retenues:
        document = paragraphes_par_id[preuve["id"]].nom_document
        groupes_retenus.setdefault(document, []).append(preuve)

    def cle_document(document: str) -> tuple[int, int]:
        evaluations = groupes_retenus[document]
        premier_id = min(evaluation["id"] for evaluation in evaluations)
        return 0, premier_id

    return [
        evaluation["id"]
        for document in sorted(groupes_retenus, key=cle_document)
        for evaluation in sorted(
            groupes_retenus[document], key=lambda element: element["id"]
        )
    ]


def applique_plage_probante(paragraphe: Paragraphe, evaluation: dict) -> Paragraphe:
    unites = unites_du_paragraphe(paragraphe)
    unite = premiere_unite_substantielle(
        unites, evaluation["debut_unite"], evaluation["fin_unite"]
    )
    return paragraphe.model_copy(
        update={
            "numero_page": unite.numero_page
            if unite is not None
            else paragraphe.numero_page,
            "score_reclassement": 1.0,
        }
    )
