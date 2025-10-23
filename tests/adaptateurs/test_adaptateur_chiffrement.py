from adaptateurs.chiffrement import AdaptateurChiffrementStandard
from configuration import Chiffrement


def test_hache_transforme_une_valeur_donnee():
    configuration = Chiffrement(sel_de_hachage="un sel")
    adaptateur_chiffrement = AdaptateurChiffrementStandard(configuration)
    une_valeur_hachee_salee_avec_sha256 = (
        "2858298547f43ce75907f4b19f5c0e78e36706d9ab0da1b1c234b412eb31b8c3"
    )
    assert (
        adaptateur_chiffrement.hache("une valeur")
        == une_valeur_hachee_salee_avec_sha256
    )
