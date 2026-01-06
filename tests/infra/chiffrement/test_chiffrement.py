from unittest.mock import patch

from adaptateurs.adaptateur_base_de_donnees_postgres import (
    CHEMINS_INTERACTION_A_CONSERVER_EN_CLAIR,
)
from infra.chiffrement.chiffrement import ServiceDeChiffrementAES
from service_chiffrement_de_test import ServiceDeChiffrementDeTest


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


def test_dechiffre_un_dict_lorsque_une_clef_a_une_valeur_none():
    key = b"abcdefghijklmnopqrstuvwxyz123456"

    dictionnaire_chiffre = ServiceDeChiffrementAES(key).dechiffre_dict(
        {"champ_1": "le champ", "champ_a_dechiffrer": None},
        ["champ_1"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_a_dechiffrer": None,
    }


def test_dechiffre_un_dict():
    dictionnaire_chiffre = ServiceDeChiffrementDeTest().dechiffre_dict(
        {"champ_1": "le champ", "champ_chiffre": "l’autre champ_chiffre"},
        ["champ_1"],
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
                "niveau_1": {
                    "niveau_2": {"champ": "champ imbriqué_chiffre"},
                    "champ_pas_chiffre": "value_non_chiffree",
                }
            },
        },
        ["champ_1", "champ_imbrique/niveau_1/niveau_2/champ_pas_chiffre"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_chiffre": "l’autre champ",
        "champ_imbrique": {
            "niveau_1": {
                "niveau_2": {"champ": "champ imbriqué"},
                "champ_pas_chiffre": "value_non_chiffree",
            }
        },
    }


def test_dechiffre_un_dict_en_donnant_le_chemin_des_elements_dans_un_tableau():
    dictionnaire_chiffre = ServiceDeChiffrementDeTest().dechiffre_dict(
        {
            "champ_1": "le champ",
            "champ_chiffre": "l’autre champ_chiffre",
            "champs_imbriques": [
                {
                    "niveau_1": {
                        "niveau_2": {"champ": "champ imbriqué_1_chiffre"},
                        "champ_pas_chiffre": "value_non_chiffree",
                    }
                },
                {"niveau_1": {"niveau_2": {"champ": "champ imbriqué_2_chiffre"}}},
            ],
        },
        ["champ_chiffre", "champs_imbriques/*/niveau_1/niveau_2/champ_pas_chiffre"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_chiffre": "l’autre champ",
        "champs_imbriques": [
            {
                "niveau_1": {
                    "niveau_2": {"champ": "champ imbriqué_1"},
                    "champ_pas_chiffre": "value_non_chiffree",
                }
            },
            {"niveau_1": {"niveau_2": {"champ": "champ imbriqué_2"}}},
        ],
    }


def test_dechiffre_une_liste_de_chaines_de_caracteres():
    dictionnaire_chiffre = ServiceDeChiffrementDeTest().dechiffre_dict(
        {
            "champ_1": "le champ",
            "champ_chiffre": "l’autre champ_chiffre",
            "niveau1": {
                "niveau2": {
                    "liste_chiffre": ["valeur1_chiffre", "valeur2_chiffre"],
                    "liste_en_clair": ["valeur3", "valeur4"],
                }
            },
        },
        ["champ_chiffre", "niveau1/niveau2/liste_en_clair"],
    )

    assert dictionnaire_chiffre == {
        "champ_1": "le champ",
        "champ_chiffre": "l’autre champ",
        "niveau1": {
            "niveau2": {
                "liste_chiffre": ["valeur1", "valeur2"],
                "liste_en_clair": ["valeur3", "valeur4"],
            }
        },
    }


def test_dechiffre_interaction_avec_aes():
    le_test_chiffre = {
        "reponse_question": {
            "reponse": "U33dQGNospkFP/99rAMj30I9l3R0yq4XcOxcc247HVs9DzYmM9sI3GH5Lj20G47+9/UWSYWe7y5N7f4H8Zp+/4Gu6qBZQB1/IoNbzgfDxAdPy6H7CxZioYWhIlX1ZGan5/OAcZA+koBxiqoI7Cimrynjh4dN5xwgzfYlLRkDI89RgbqwTIc5G70ybAGtplxaVXEqYr6F1Ofhgqy3KW6+2hdQHGhSaQa16EeeFYr1BjjZNKHNYzj9gEHGOJhByWVM7QTLRKpCQ9pVDmZzhqlKpDCpVCFGTS+v44ISXBW3Y73Yf2aUU6SR7N2VGJHytREbm586hQLPfm/4CVuha7PsZtJZ9oFify+xCgWRJ2cWz6UX2ZFA9XAgIDqMnnpW1h+S+Z5fRR8FJ3bbEK5NIslkeVWlm4sv5a6rsWHlgm0+gKzYnsYX03QLW8Yvmy6E/CbWte6gDXzOXo4mUwaDmavq/6yIx7sLq8kYRXi+7SEh59fKic8nw+cziXofbFcdeb1UL3razFC5m90SzAu0goFFtZHP1na+1txkql9CEhYNE/LKCFOzZ5VzML90BeDd1e/no19yjCul7h09UI4VE4PKYjS86o3WTfW9PJrtSEEmVLuHZrf6dv2efLW7KB4ruldXTY0mKCJTp0aN8CS+3EadMfAlMQSI+87OQKSohakcBcN+pwrIZaHk8LOIToQ1ikSTBEq9Ju29nkAAbFbTcU+5hi23BhluukU/BhKACdLfzcpAmAQcQq1eBQAaRLwkM8o6k0HHDj5QM/mh6OVLcgLEhtkaBLGtPsiMQIbRQ2HRcHVHnhSj9cWqHrXuMje3V00J2LR9Yl1mfYqJUajZACouB46RW68Kc91PvVrefdzPbw2Uxb9BrKWck/1SB4Iz+1dmkSu2bv/XV1xKC73QiihwAJWXQ4A3XHqecR6UVIjoaatLGfqj0N7GC9Ysu13vL2apHNK1hIibNFd9JluRxOeA+69T81+PIrYEPFID3E30PusjiMGB0EU0xuo0k2KpPZPZ7jY8/CKrCc034Vn7VBnNL1Vj7FpvmFqw+qnGVxYRFPY7f59x44m9o+NwLD7S+IpS/JO2fzAjxycJ8fUR3NyALe4nlWRrKykAENDjlzCrJjqHWLC+OUU6LU8R/efBUam3lzyCwAgC031yVEhBZgp0rffSSXEDICLQzhG864cx8Mfe1Z+OUY3vuQ2R5TOOMPFhwNmw0RiwEoG++5Q6MVCiaqA3ICCssDQFAGGZTYrDkA3Bt3Kdhz5qZo//eka+YL57vzIorOaNlOgHeWmU6pRTgPiKvjKbA/laYe6JE1sLRnmShBTirksx7aCmHKz0mUW0v+WwgxmKCTYADHfsxqPh6O4GgAoZazksy+SHm23f6TvJzUOkr2vktZ574/0QkqEQDajj1iq0kk5miOR4ICYehXzHFEEqseJJtLnwE9NOZBs0TVLDIxMjTREj8y4xe2Z8fimGyT3tHc6q/lkim6Tpt/jqR+YLx8O+5+SlCy8qYJQQMLthcaAlDIthnIrB",
            "question": "r6e4sdbK1EoEphHzef6WR/m0Os+wdwSjp8eUy3GdlQtBHo4xyhlBk9MFH4+eh3i3t+XjfMTs2+LbTlOQ7JY0xrm24YuWX0t14DOdO4J0NWlqq+Ya2z7H9fJWYGYpe3sEayxN9rlKbBJ3Od4=",
            "violation": None,
            "paragraphes": [
                {
                    "url": "https://cyber.gouv.fr/sites/default/files/2020/06/anssi-guide-passerelle_internet_securisee-v3.pdf",
                    "contenu": "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",
                    "numero_page": 11,
                    "nom_document": "Y+Q4hma8aWFBmbOrXmC79DZr5d+KqhYYycKXv1KwbsKvgztQ6OTwd5sYYl4u1xWA+N+pEXTtvYjSUdNoFAOmpwm/g2CbFYxPrWN5wQ==",
                    "score_similarite": 0.79410887,
                },
                {
                    "url": "https://cyber.gouv.fr/sites/default/files/2020/06/anssi-guide-passerelle_internet_securisee-v3.pdf",
                    "contenu": "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",
                    "numero_page": 53,
                    "nom_document": "HogOytob7f9k2RCkT4zGCFh3ySROCE2iHYcte0hlTBeWwf4AyHrKJPBTk1prCCW4EfG2huoPLcIkJflVLRfEsnAynvOhCVT+l5Octg==",
                    "score_similarite": 0.7925291,
                },
                {
                    "url": "https://cyber.gouv.fr/sites/default/files/2020/06/anssi-guide-passerelle_internet_securisee-v3.pdf",
                    "contenu": "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",
                    "numero_page": 10,
                    "nom_document": "stbOXhqUkErM+5y512Lo+4MchZTOMbKjD2zIa3V9KuSWxTQoz/Xtm48fDs9m23nc0phlGwDiHMVglPn33chIH33hA0+nxg6TLdHaDQ==",
                    "score_similarite": 0.79187536,
                },
                {
                    "url": "https://cyber.gouv.fr/sites/default/files/2018/04/anssi-guide-admin_securisee_si_v3-0.pdf",
                    "contenu": "c1SjfCd5JaJluYvLXio+0aopk/IMuJHlLrcSy2TDyv0bQDsN+JlXPinjt5ox8mYwYRfm8+9jBl3rTlihhReqo4pwS/je/oRRaWqVPVbgUBuu9rNDOfDwRFgKFLr1OZv1l8ValL0gdIZfRL45ysYJmfwvaZA356iJxnhEbgTACnmTiiwqe3vmbdbHGBaBbMR8M06NOPBKhIYmZLZUP5GD66mN2tkoTdhvsMphcebhUbNn6si4IR7avE4QvdiGWe1J+QyVuTgEJYzNWJ0r+m8V13lETXXdrFzK8jYs9j1WC/sJVMdTKEjREzXEXVDjz4ftLqby5Pbqly1V64MAHx3W3+l3Vkvo3YGp80IWcj6AoJIkLSznLw5Zu0IkBqPYx5CfNuJq1JZhoDdGQrOp28OO39pO1l33EKb6F4+hoKqVUXwh5WUBGWvRoJVXa1w7CLqFfzMxOFQeG/Vd5pcduGyy4AD4QCpZUjgGljdxZe+haE09cfeh6PVtD0HPa+7jeRBhqv2iKQKaWQotZEnchKdcjEBPlt5FXKruWZFdUpSzRcqMOq2VHuh8zFK4LcYcEO2t0LYaCHj+DxvpX0Ct8ARx5sK1gX7+iav7oEb8RapEpWalDZUo0dS7koC0gQjUZu4IoW1covIlkxZuphLifAMo6ptV1ykzmQnalHknpXLZtZHDD+/CoKu9aI8meAba1MFyyYFcn7pVoOWYqfFN4fjeA9MKDjHIR/K9UcNL1jqaQ/U/Xa81J7XSLmbm8pDR3ceyakeXijugOn2vO9X0ymbVMpDkYXJvb+wd2LmZfdXN6IOc8pUJCwiNW7jam5mdyQ3eRcHwnvXpTmipF+zse0eEYNjOWxt7i8V1UpBC5qX7YKz5XUbv5R1uoPqiAnTKnjYtrxRx+HUyVYhTt+hY5oeqMvQ2SH6bxidhPXA9qKb5A9BRnDVT5PzDdpoUYn5tFmpKoUvTWLJPO4PnP89coQ+90LVq0A==",
                    "numero_page": 58,
                    "nom_document": "7CZkQ/lFgOct3zesms8c8ss3I8F+eATA3h03yfnnzGkqGarHapErehqz8WyG5APH1bQgTBXFkBef5vjdyMNTcg7UeA==",
                    "score_similarite": 0.785512,
                },
                {
                    "url": "https://cyber.gouv.fr/sites/default/files/2018/04/anssi-guide-admin_securisee_si_v3-0.pdf",
                    "contenu": "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",
                    "numero_page": 41,
                    "nom_document": "gkIPDrgw574n5B/f7mfTGpz1ggujKGGKvRFOJkDXFZybAV/VQdYKiCz4cWkhMFwPvJ7Fc0GVZA2NHdVcgSPUKW/2+A==",
                    "score_similarite": 0.779377,
                },
            ],
        },
        "retour_utilisatrice": None,
    }

    resultat = ServiceDeChiffrementAES(
        "abcdefghijklmnopqrstuvwxyz123456".encode("utf-8")
    ).dechiffre_dict(le_test_chiffre, CHEMINS_INTERACTION_A_CONSERVER_EN_CLAIR)

    assert len(resultat["reponse_question"]["paragraphes"]) == 5
