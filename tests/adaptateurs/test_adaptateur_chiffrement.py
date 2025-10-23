from adaptateurs.chiffrement import AdaptateurChiffrementStandard


def test_hache_transforme_une_valeur_donnee():
    adaptateur_chiffrement = AdaptateurChiffrementStandard()
    une_valeur_hachee_avec_sha256 = (
        "7babcb417f1e60ca1d5cc0a855de201df6de5683a600b90903a97c71275d6027"
    )
    assert adaptateur_chiffrement.hache("une valeur") == une_valeur_hachee_avec_sha256
