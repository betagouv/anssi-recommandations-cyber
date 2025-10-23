import hashlib
from abc import ABC, abstractmethod


class AdaptateurChiffrement(ABC):
    @abstractmethod
    def hache(self, valeur: str) -> str:
        pass


class AdaptateurChiffrementStandard(AdaptateurChiffrement):
    def hache(self, valeur: str) -> str:
        return hashlib.sha256(valeur.encode()).hexdigest()


def fabrique_adaptateur_chiffrement() -> AdaptateurChiffrement:
    return AdaptateurChiffrementStandard()
