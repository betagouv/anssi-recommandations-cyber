from unittest.mock import patch
from infra.chiffrement.chiffrement import ServiceDeChiffrementAES, ServiceDeChiffrement


class ServiceDeChiffrementDeTest(ServiceDeChiffrement):
    def chiffre(self, contenu: str) -> str:
        return f"{contenu}_chiffre"

    def dechiffre(self, contenu_chiffre: str) -> str:
        return contenu_chiffre.removesuffix("_chiffre")


def test_chiffre_une_chaine_de_caractere_avec_aes():
    with patch("os.urandom", return_value=b"\x01" * 12):
        key = b"abcdefghijklmnopqrstuvwxyz123456"

        chaine_chiffree = ServiceDeChiffrementAES(key).chiffre("Un contenu")

        assert chaine_chiffree == "AQEBAQEBAQEBAQEB25U5WnoGGxurQWkvDcnTSyo+ohgDhTuGxvM="


def test_dechiffre_une_chaine_de_caractere_avec_aes():
    with patch("os.urandom", return_value=b"\x01" * 12):
        key = b"abcdefghijklmnopqrstuvwxyz123456"

        chaine_dechiffree = ServiceDeChiffrementAES(key).dechiffre(
            "AQEBAQEBAQEBAQEB25U5WnoGGxurQWkvDcnTSyo+ohgDhTuGxvM="
        )

        assert chaine_dechiffree == "Un contenu"


def test_chiffre_un_dict():
    dictionnaire_chiffre = ServiceDeChiffrementDeTest().chiffre_dict(
        {"champ_1": "le champ", "champ_a_chiffrer": "le champ à chiffrer"},
        ["champ_a_chiffrer"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_a_chiffrer": "le champ à chiffrer_chiffre",
    }


def test_chiffre_un_dict_en_donnant_le_chemin_des_elements():
    dictionnaire_chiffre = ServiceDeChiffrementDeTest().chiffre_dict(
        {
            "champ_1": "le champ",
            "champ_a_chiffrer": "le champ à chiffrer",
            "champ_imbrique": {"niveau_1": {"niveau_2": {"champ": "champ imbriqué"}}},
        },
        ["champ_a_chiffrer", "champ_imbrique/niveau_1/niveau_2/champ"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_a_chiffrer": "le champ à chiffrer_chiffre",
        "champ_imbrique": {
            "niveau_1": {"niveau_2": {"champ": "champ imbriqué_chiffre"}}
        },
    }


def test_chiffre_un_dict_en_donnant_le_chemin_des_elements_dans_un_tableau():
    dictionnaire_chiffre = ServiceDeChiffrementDeTest().chiffre_dict(
        {
            "champ_1": "le champ",
            "champ_a_chiffrer": "le champ à chiffrer",
            "champs_imbriques": [
                {"niveau_1": {"niveau_2": {"champ": "champ imbriqué_1"}}},
                {"niveau_1": {"niveau_2": {"champ": "champ imbriqué_2"}}},
            ],
        },
        ["champ_a_chiffrer", "champs_imbriques/*/niveau_1/niveau_2/champ"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_a_chiffrer": "le champ à chiffrer_chiffre",
        "champs_imbriques": [
            {"niveau_1": {"niveau_2": {"champ": "champ imbriqué_1_chiffre"}}},
            {"niveau_1": {"niveau_2": {"champ": "champ imbriqué_2_chiffre"}}},
        ],
    }


def test_chiffre_un_dict_lorsque_une_clef_a_une_valeur_none():
    key = b"abcdefghijklmnopqrstuvwxyz123456"

    dictionnaire_chiffre = ServiceDeChiffrementAES(key).chiffre_dict(
        {"champ_1": "le champ", "champ_a_chiffrer": None},
        ["champ_a_chiffrer"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_a_chiffrer": None,
    }


def test_dechiffre_un_dict_lorsque_une_clef_a_une_valeur_none():
    key = b"abcdefghijklmnopqrstuvwxyz123456"

    dictionnaire_chiffre = ServiceDeChiffrementAES(key).dechiffre_dict(
        {"champ_1": "le champ", "champ_a_dechiffrer": None},
        ["champ_a_dechiffrer"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_a_dechiffrer": None,
    }

def test_dechiffre_un_dict():
    dictionnaire_chiffre = ServiceDeChiffrementDeTest().dechiffre_dict(
        {"champ_1": "le champ", "champ_chiffre": "l’autre champ_chiffre"},
        ["champ_chiffre"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_chiffre": "l’autre champ",
    }


def test_dechiffre_un_dict_en_donnant_le_chemin_des_elements():
    dictionnaire_chiffre = ServiceDeChiffrementDeTest().dechiffre_dict(
        {
            "champ_1": "le champ",
            "champ_chiffre": "l’autre champ_chiffre",
            "champ_imbrique": {
                "niveau_1": {"niveau_2": {"champ": "champ imbriqué_chiffre"}}
            },
        },
        ["champ_chiffre", "champ_imbrique/niveau_1/niveau_2/champ"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_chiffre": "l’autre champ",
        "champ_imbrique": {"niveau_1": {"niveau_2": {"champ": "champ imbriqué"}}},
    }


def test_dechiffre_un_dict_en_donnant_le_chemin_des_elements_dans_un_tableau():
    dictionnaire_chiffre = ServiceDeChiffrementDeTest().dechiffre_dict(
        {
            "champ_1": "le champ",
            "champ_chiffre": "l’autre champ_chiffre",
            "champs_imbriques": [
                {"niveau_1": {"niveau_2": {"champ": "champ imbriqué_1_chiffre"}}},
                {"niveau_1": {"niveau_2": {"champ": "champ imbriqué_2_chiffre"}}},
            ],
        },
        ["champ_chiffre", "champs_imbriques/*/niveau_1/niveau_2/champ"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_chiffre": "l’autre champ",
        "champs_imbriques": [
            {"niveau_1": {"niveau_2": {"champ": "champ imbriqué_1"}}},
            {"niveau_1": {"niveau_2": {"champ": "champ imbriqué_2"}}},
        ],
    }
