from adaptateurs.chiffrement import AdaptateurChiffrementStandard
from configuration import Chiffrement
from infra.chiffrement.chiffrement import ServiceDeChiffrementEnClair


def test_hache_transforme_une_valeur_donnee():
    configuration = Chiffrement(sel_de_hachage="un sel", clef_chiffrement="une clef")
    adaptateur_chiffrement = AdaptateurChiffrementStandard(
        configuration, ServiceDeChiffrementEnClair()
    )
    une_valeur_hachee_salee_avec_sha256 = (
        "2858298547f43ce75907f4b19f5c0e78e36706d9ab0da1b1c234b412eb31b8c3"
    )
    assert (
        adaptateur_chiffrement.hache("une valeur")
        == une_valeur_hachee_salee_avec_sha256
    )


def test_recupere_nonce_retourne_une_valeur_assez_longue():
    configuration = Chiffrement(sel_de_hachage="un sel", clef_chiffrement="une clef")
    adaptateur_chiffrement = AdaptateurChiffrementStandard(
        configuration, ServiceDeChiffrementEnClair()
    )

    nonce = adaptateur_chiffrement.recupere_nonce()

    assert len(nonce) >= 16
