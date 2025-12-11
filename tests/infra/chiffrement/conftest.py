import pytest

from infra.chiffrement.chiffrement import (
    FournisseurDeServiceDeChiffrement,
    ServiceDeChiffrement,
)


class ServiceDeChiffrementDeTest(ServiceDeChiffrement):
    def dechiffre(self, contenu_chiffre: str) -> str:
        return contenu_chiffre.removesuffix("_chiffre")

    def chiffre(self, contenu: str) -> str:
        return f"{contenu}_chiffre"


@pytest.fixture(autouse=True)
def chiffrement_de_test():
    FournisseurDeServiceDeChiffrement.service = ServiceDeChiffrementDeTest()
