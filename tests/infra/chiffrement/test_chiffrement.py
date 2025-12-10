from infra.chiffrement.chiffrement import chiffre


def test_chiffre_modele():
    def fonction_interne():
        def autre_fonction():
            return {
                "cle_avec_valeur_en_clair": "valeur_en_clair",
                "cle_avec_valeur_chiffree_1": "valeur_a_chiffrer_1",
                "cle_avec_valeur_chiffree_2": "valeur_a_chiffrer_2",
            }

        return autre_fonction

    fonction = chiffre(
        modele={"cles": ["cle_avec_valeur_chiffree_1", "cle_avec_valeur_chiffree_2"]}
    )
    modele_chiffre = fonction(fonction_interne())()

    assert modele_chiffre == {
        "cle_avec_valeur_en_clair": "valeur_en_clair",
        "cle_avec_valeur_chiffree_1": "valeur_a_chiffrer_1_chiffre",
        "cle_avec_valeur_chiffree_2": "valeur_a_chiffrer_2_chiffre",
    }
