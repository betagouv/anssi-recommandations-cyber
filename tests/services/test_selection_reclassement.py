import pytest

from schemas.albert import ParagrapheReponseMaitrisee
from services.selection_reclassement import (
    applique_unite_probante,
    fusionne_preuves,
)
from unites_source_de_test import une_unite_source


def une_preuve(identifiant, degre_pertinence=3, **champs):
    return {
        "id": identifiant,
        "categorie": "preuve_principale",
        "relation": "directe",
        "portee_preuve": "generale",
        "apport": "reponse_centrale",
        "degre_pertinence": degre_pertinence,
        **champs,
    }


NON_DEMANDEE = {"portee_preuve": "specifique_non_demandee"}
NAVIGATION = {"apport": "navigation_ou_simple_illustration"}

CAS_DE_FUSION = {
    "un_degre_superieur_ecarte_un_degre_inferieur": (
        [une_preuve(1, 1), une_preuve(2, 3)],
        [2],
    ),
    "toutes_les_preuves_du_degre_maximal_sont_gardees": (
        [une_preuve(1), une_preuve(2, 1), une_preuve(3)],
        [1, 3],
    ),
    "les_preuves_retenues_sont_ordonnees_par_identifiant": (
        [une_preuve(3), une_preuve(1)],
        [1, 3],
    ),
    "une_preuve_specifique_non_demandee_ne_bloque_pas_le_repli_general": (
        [une_preuve(1, **NON_DEMANDEE), une_preuve(2, 2)],
        [2],
    ),
    "une_relation_indirecte_est_ecartee": (
        [une_preuve(1, relation="indirecte"), une_preuve(2, 1)],
        [2],
    ),
    "un_apport_de_navigation_est_ecarte": (
        [une_preuve(1, **NAVIGATION), une_preuve(2, 1)],
        [2],
    ),
    "aucune_preuve_admissible": ([une_preuve(1, **NON_DEMANDEE)], []),
    "aucune_preuve": ([], []),
}


@pytest.mark.parametrize(
    ("preuves", "ids_retenus"),
    CAS_DE_FUSION.values(),
    ids=CAS_DE_FUSION.keys(),
)
def test_fusionne_les_preuves_admissibles_du_degre_maximal(
    des_paragraphes, preuves, ids_retenus
):
    assert fusionne_preuves(des_paragraphes(3), preuves) == ids_retenus


@pytest.fixture
def un_paragraphe_maitrise_a_unites():
    return ParagrapheReponseMaitrisee(
        contenu="Un contenu",
        reponse="Réponse maîtrisée",
        score_similarite=0.8,
        score_reclassement=0.2,
        numero_page=1,
        url="https://exemple.test/source.pdf",
        nom_document="source.pdf",
        unites_source=[une_unite_source(numero_page=page) for page in (33, 34, 35)],
    )


@pytest.mark.parametrize(("unite_probante", "numero_page"), [(1, 33), (2, 34), (3, 35)])
def test_applique_la_page_de_l_unite_probante(
    un_paragraphe_maitrise_a_unites, unite_probante, numero_page
):
    evaluation = {"unite_probante": unite_probante}

    retenu = applique_unite_probante(un_paragraphe_maitrise_a_unites, evaluation)

    assert retenu.numero_page == numero_page


def test_conserve_la_source_et_son_type_en_appliquant_l_unite_probante(
    un_paragraphe_maitrise_a_unites,
):
    retenu = applique_unite_probante(
        un_paragraphe_maitrise_a_unites, {"unite_probante": 2}
    )

    assert isinstance(retenu, ParagrapheReponseMaitrisee)
    assert retenu.contenu == un_paragraphe_maitrise_a_unites.contenu
    assert retenu.reponse == "Réponse maîtrisée"
    assert retenu.score_reclassement == 1.0


def test_sans_unites_enrichies_garde_la_page_du_paragraphe(
    un_constructeur_de_paragraphe,
):
    paragraphe = un_constructeur_de_paragraphe().a_la_page(12).construis()

    assert applique_unite_probante(paragraphe, {"unite_probante": 1}).numero_page == 12
