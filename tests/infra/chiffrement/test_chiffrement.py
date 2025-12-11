from unittest.mock import patch
from infra.chiffrement.chiffrement import ServiceDeChiffrementAES, ServiceDeChiffrement


class ServiceDeChiffrementDeTest(ServiceDeChiffrement):
    def chiffre(self, contenu: str) -> str:
        return f"{contenu}_chiffre"

    def dechiffre(self, contenu_chiffre: str) -> str:
        return contenu_chiffre.removesuffix("_chiffre")


def test_chiffre_une_chaine_de_caractere_avec_aes():
    with patch("secrets.token_bytes", return_value=b"\x01" * 12):
        key = b"abcdefghijklmnopqrstuvwxyz123456"

        chaine_chiffree = ServiceDeChiffrementAES(key).chiffre("Un contenu")

        assert chaine_chiffree == "AQEBAQEBAQEBAQEB25U5WnoGGxurQWkvDcnTSyo+ohgDhTuGxvM="


def test_dechiffre_une_chaine_de_caractere_avec_aes():
    key = b"abcdefghijklmnopqrstuvwxyz123456"

    chaine_dechiffree = ServiceDeChiffrementAES(key).dechiffre(
        "AQEBAQEBAQEBAQEB25U5WnoGGxurQWkvDcnTSyo+ohgDhTuGxvM="
    )

    assert chaine_dechiffree == "Un contenu"


def test_chiffre_un_dict():
    dictionnaire_chiffre = ServiceDeChiffrementDeTest().chiffre_dict(
        {"champ_1": "le champ", "champ_a_chiffrer": "le champ à chiffrer"},
        ["champ_1"],
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
            "champ_imbrique": {
                "niveau_1": {
                    "niveau_2": {
                        "champ": "champ imbriqué",
                    },
                    "autre_champ_pas_a_chiffrer": " autre champ imbriqué",
                }
            },
        },
        ["champ_1", "champ_imbrique/niveau_1/autre_champ_pas_a_chiffrer"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_a_chiffrer": "le champ à chiffrer_chiffre",
        "champ_imbrique": {
            "niveau_1": {
                "niveau_2": {"champ": "champ imbriqué_chiffre"},
                "autre_champ_pas_a_chiffrer": " autre champ imbriqué",
            }
        },
    }


def test_chiffre_un_dict_en_donnant_le_chemin_des_elements_dans_un_tableau():
    dictionnaire_chiffre = ServiceDeChiffrementDeTest().chiffre_dict(
        {
            "champ_1": "le champ",
            "champ_a_chiffrer": "le champ à chiffrer",
            "champs_imbriques": [
                {
                    "niveau_1": {
                        "niveau_2": {
                            "champ": "champ imbriqué_1",
                            "autre_champ_pas_a_chiffrer": " autre champ imbriqué",
                        }
                    }
                },
                {"niveau_1": {"niveau_2": {"champ": "champ imbriqué_2"}}},
            ],
        },
        ["champ_1", "champs_imbriques/*/niveau_1/niveau_2/autre_champ_pas_a_chiffrer"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_a_chiffrer": "le champ à chiffrer_chiffre",
        "champs_imbriques": [
            {
                "niveau_1": {
                    "niveau_2": {
                        "champ": "champ imbriqué_1_chiffre",
                        "autre_champ_pas_a_chiffrer": " autre champ imbriqué",
                    }
                }
            },
            {"niveau_1": {"niveau_2": {"champ": "champ imbriqué_2_chiffre"}}},
        ],
    }


def test_chiffre_un_dict_lorsque_une_clef_a_une_valeur_none():
    key = b"abcdefghijklmnopqrstuvwxyz123456"

    dictionnaire_chiffre = ServiceDeChiffrementAES(key).chiffre_dict(
        {"champ_1": "le champ", "champ_a_chiffrer": None},
        ["champ_1"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_a_chiffrer": None,
    }


def test_chiffre_une_liste_de_chaines_de_caracteres():
    dictionnaire_chiffre = ServiceDeChiffrementDeTest().chiffre_dict(
        {
            "champ_1": "le champ",
            "champ_a_chiffrer": "l’autre champ",
            "niveau1": {
                "niveau2": {
                    "liste_a_chiffrer": ["valeur1", "valeur2"],
                    "liste_en_clair": ["valeur3", "valeur4"],
                }
            },
        },
        ["champ_1", "niveau1/niveau2/liste_en_clair"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_a_chiffrer": "l’autre champ_chiffre",
        "niveau1": {
            "niveau2": {
                "liste_a_chiffrer": ["valeur1_chiffre", "valeur2_chiffre"],
                "liste_en_clair": ["valeur3", "valeur4"],
            }
        },
    }
