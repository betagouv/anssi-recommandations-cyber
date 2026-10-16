from unittest.mock import patch
import pytest
from configuration import (
    TypeReclasseur,
    calcule_capacite_reclassement_parallele,
    recupere_configuration,
)


@patch("os.getenv")
def test_configuration_leve_une_exception_lorsque_des_variables_sont_manquantes(
    mock_getenv,
):
    def side_effect(key, default=None):
        if key == "MODE":
            return "production"
        return default

    mock_getenv.side_effect = side_effect
    exception_levee = False
    try:
        recupere_configuration()
    except Exception as e:
        exception_levee = True
        assert (
            "Les variables d'environnement suivantes sont manquantes :\n - ALBERT_API_KEY\n - ALBERT_MODELE"
            "\n - ALBERT_MODELE_REFORMULATION\n - COLLECTION_ID_ANSSI_LAB\n - DB_NAME\n - DB_HOST\n - DB_PORT\n - DB_USER"
            "\n - DB_PASSWORD\n - CHIFFREMENT_SEL_DE_HACHAGE\n - CHIFFREMENT_CLEF_DE_CHIFFREMENT\n - HOST\n - PORT"
        ) in str(e)
    assert exception_levee is True


@patch("os.getenv")
def test_configuration_ne_verifie_pas_les_variables_d_environnement_si_on_est_en_developpement(
    mock_getenv,
):
    def side_effect(key, default=None):
        if key == "MODE":
            return "developpement"
        return default

    mock_getenv.side_effect = side_effect

    exception_levee = False
    try:
        recupere_configuration()
    except Exception:
        exception_levee = True

    assert exception_levee is False


@patch("os.getenv")
def test_configuration_ne_verifie_pas_les_variables_d_environnement_si_on_est_sur_la_CI(
    mock_getenv,
):
    def side_effect(key, default=None):
        if key == "MODE":
            return "test"
        return default

    mock_getenv.side_effect = side_effect

    exception_levee = False
    try:
        recupere_configuration()
    except Exception:
        exception_levee = True

    assert exception_levee is False


@patch("os.getenv")
def test_configuration_selectionne_le_type_de_reclasseur_depuis_l_environnement(
    mock_getenv,
):
    def side_effect(key, default=None):
        if key == "MODE":
            return "test"
        if key == "COLLECTION_ID_ANSSI_LAB":
            return "42"
        if key == "TYPE_RECLASSEUR":
            return "llm"
        return default

    mock_getenv.side_effect = side_effect

    configuration = recupere_configuration()

    assert configuration.albert.service.type_reclasseur is TypeReclasseur.LLM


def test_calcul_capacite_reclassement_couvre_les_deux_collections_et_tous_les_lots():
    capacite = calcule_capacite_reclassement_parallele(
        nombre_paragraphes=20, taille_lot=5, jeopardy_active=True
    )

    assert capacite.nombre_maximum_candidats == 40
    assert capacite.nombre_maximum_d_appels_par_workflow == 9
    assert capacite.nombre_threads == 18


def test_calcul_capacite_reclassement_tient_compte_du_dernier_lot_partiel():
    capacite = calcule_capacite_reclassement_parallele(
        nombre_paragraphes=20, taille_lot=6, jeopardy_active=False
    )

    assert capacite.nombre_maximum_candidats == 20
    assert capacite.nombre_maximum_d_appels_par_workflow == 5
    assert capacite.nombre_threads == 10


@pytest.mark.parametrize(
    ("nombre_paragraphes", "taille_lot", "jeopardy_active"),
    [
        (0, 5, False),
        (20, 0, False),
        (-1, 5, False),
        (20, -1, False),
        (True, 5, False),
        (20, True, False),
        (20, 5, 1),
    ],
)
def test_calcul_capacite_reclassement_refuse_les_limites_invalides(
    nombre_paragraphes, taille_lot, jeopardy_active
):
    with pytest.raises(ValueError):
        calcule_capacite_reclassement_parallele(
            nombre_paragraphes, taille_lot, jeopardy_active
        )
