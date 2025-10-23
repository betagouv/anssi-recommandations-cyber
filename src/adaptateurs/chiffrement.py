import hashlib
from abc import ABC, abstractmethod
from configuration import Chiffrement, recupere_configuration


class AdaptateurChiffrement(ABC):
    def __init__(self, configuration: Chiffrement):
        self.sel_de_hachage = configuration.sel_de_hachage

    @abstractmethod
    def hache(self, valeur: str) -> str:
        pass


class AdaptateurChiffrementStandard(AdaptateurChiffrement):
    def hache(self, valeur: str) -> str:
        return hashlib.sha256(f"{self.sel_de_hachage}{valeur}".encode()).hexdigest()


def fabrique_adaptateur_chiffrement() -> AdaptateurChiffrement:
    configuration = recupere_configuration().chiffrement
    return AdaptateurChiffrementStandard(configuration)
