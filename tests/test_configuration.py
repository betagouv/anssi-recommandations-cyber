from unittest.mock import patch
from configuration import recupere_configuration


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
