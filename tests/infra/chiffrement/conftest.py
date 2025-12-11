import pytest

from infra.chiffrement.chiffrement import (
    FournisseurDeServiceDeChiffrement,
    ServiceDeChiffrementEnClair,
)


@pytest.fixture(autouse=True)
def chiffrement_de_test():
    FournisseurDeServiceDeChiffrement.service = ServiceDeChiffrementEnClair()
