from classification_de_test import (
    classification_element_de_reponse,
    classification_preuve_principale,
    resultat_de_classification,
)
from question.reclassement.contrat_reclassement_llm import (
    evaluations_de_classification,
    schema_classification,
)
from services.fichier_prompt import lis_fichier_prompt
from unites_source_de_test import une_table_des_matieres, une_unite_source

PROMPT = "prompt_reclassement_llm_classification.txt"


def _branches(schema, identifiant="1"):
    return schema["properties"]["candidats"]["properties"][identifiant]["anyOf"]


def test_le_schema_demande_une_classification_fermee_par_identifiant_global(
    des_paragraphes,
):
    schema = schema_classification(des_paragraphes(2), premier_id=4)

    candidats = schema["properties"]["candidats"]
    assert list(candidats["properties"]) == candidats["required"] == ["4", "5"]
    assert schema["additionalProperties"] is candidats["additionalProperties"] is False
    assert all(b["additionalProperties"] is False for b in _branches(schema, "4"))


def test_un_candidat_est_classe_sans_preuve_ou_comme_preuve_principale(
    des_paragraphes,
):
    sans_preuve, preuve = _branches(schema_classification(des_paragraphes(1), 1))

    assert sans_preuve["required"] == ["categorie", "relation", "portee", "apport"]
    assert sans_preuve["properties"]["categorie"]["enum"] == [
        "hors_sujet",
        "dans_la_thematique_sans_apport",
        "element_de_reponse",
    ]
    assert preuve["required"][-1] == "unite_probante"
    assert preuve["properties"]["categorie"]["const"] == "preuve_principale"
    assert preuve["properties"]["apport"]["enum"] == [
        "reponse_centrale",
        "explication_directe",
        "principe_direct",
    ]
    assert preuve["properties"]["portee"]["enum"] == [
        "generale",
        "specifique_demandee",
        "specifique_non_demandee",
    ]


def test_une_preuve_principale_ne_peut_designer_qu_une_unite_substantielle(
    un_constructeur_de_paragraphe,
):
    paragraphe = (
        un_constructeur_de_paragraphe()
        .avec_les_unites_source(
            [
                une_table_des_matieres(),
                une_unite_source(),
                une_table_des_matieres(),
                une_unite_source(),
            ]
        )
        .construis()
    )

    _, preuve = _branches(schema_classification([paragraphe], premier_id=1))

    assert preuve["properties"]["unite_probante"] == {
        "type": "integer",
        "enum": [2, 4],
    }


def test_un_candidat_sans_unite_substantielle_ne_peut_pas_etre_une_preuve(
    un_constructeur_de_paragraphe,
):
    paragraphe = un_constructeur_de_paragraphe().avec_contenu(" \n\t ").construis()

    assert len(_branches(schema_classification([paragraphe], premier_id=1))) == 1


def test_extrait_une_evaluation_par_candidat_avec_le_degre_de_son_apport(
    des_paragraphes,
):
    resultat = resultat_de_classification(
        {
            4: classification_preuve_principale(
                apport="reponse_centrale", unite_probante=2
            ),
            5: classification_element_de_reponse(apport="explication_directe"),
            6: classification_element_de_reponse(apport="principe_direct"),
            7: classification_element_de_reponse(
                relation="indirecte",
                portee="specifique_demandee",
                apport="navigation_ou_simple_illustration",
            ),
        }
    )

    evaluations = evaluations_de_classification(
        resultat, des_paragraphes(4), premier_id=4
    )

    assert [
        (e["id"], e["categorie"], e["apport"], e["degre_pertinence"])
        for e in evaluations
    ] == [
        (4, "preuve_principale", "reponse_centrale", 3),
        (5, "element_de_reponse", "explication_directe", 2),
        (6, "element_de_reponse", "principe_direct", 1),
        (7, "element_de_reponse", "navigation_ou_simple_illustration", 0),
    ]
    assert evaluations[0]["unite_probante"] == 2
    assert evaluations[3]["relation"] == "indirecte"
    assert evaluations[3]["portee_preuve"] == "specifique_demandee"


def test_le_prompt_de_classification_demande_les_champs_du_schema():
    champs = ("categorie", "relation", "portee", "apport", "unite_probante")

    assert all(f"`{champ}`" in lis_fichier_prompt(PROMPT) for champ in champs)


def test_le_prompt_de_classification_se_formate_avec_la_question_et_les_candidats():
    prompt = lis_fichier_prompt(PROMPT).format(
        QUESTION="Une question ?", CANDIDATS="Des candidats"
    )

    assert "Une question ?" in prompt
    assert "Des candidats" in prompt
