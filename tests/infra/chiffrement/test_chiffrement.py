from unittest.mock import patch
from infra.chiffrement.chiffrement import ServiceDeChiffrementAES


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
