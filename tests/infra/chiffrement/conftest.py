from typing import Any
import pytest
from infra.chiffrement.chiffrement import (
    FournisseurDeServiceDeChiffrement,
    ServiceDeChiffrement,
)


class ServiceDeChiffrementDeTest(ServiceDeChiffrement):
    def dechiffre(self, contenu_chiffre: Any) -> bytes:
        return bytes(contenu_chiffre.decode("utf-8").removesuffix("_chiffre"), "utf-8")

    def chiffre(self, contenu: bytes) -> bytes:
        return bytes(f"{contenu}_chiffre", "utf-8")  # type: ignore


@pytest.fixture(autouse=True)
def chiffrement_de_test():
    FournisseurDeServiceDeChiffrement.service = ServiceDeChiffrementDeTest()
