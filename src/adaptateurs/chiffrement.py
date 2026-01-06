import hashlib
import secrets
from abc import ABC, abstractmethod
from configuration import Chiffrement, recupere_configuration
from infra.chiffrement.chiffrement import (
    fabrique_fournisseur_de_chiffrement,
    ServiceDeChiffrement,
)


class AdaptateurChiffrement(ABC):
    def __init__(
        self, configuration: Chiffrement, service_de_chiffrement: ServiceDeChiffrement
    ):
        self.sel_de_hachage = configuration.sel_de_hachage
        self.service_de_chiffrement = service_de_chiffrement

    @abstractmethod
    def hache(self, valeur: str) -> str:
        pass

    @abstractmethod
    def recupere_nonce(self) -> str:
        pass

    @abstractmethod
    def chiffre(self, contenu: str) -> str:
        pass

    @abstractmethod
    def dechiffre(self, contenu_chiffre: str) -> str:
        pass


class AdaptateurChiffrementStandard(AdaptateurChiffrement):
    def chiffre(self, contenu: str) -> str:
        return self.service_de_chiffrement.chiffre(contenu)

    def dechiffre(self, contenu_chiffre: str) -> str:
        return self.service_de_chiffrement.dechiffre(contenu_chiffre)

    def hache(self, valeur: str) -> str:
        return hashlib.sha256(f"{self.sel_de_hachage}{valeur}".encode()).hexdigest()

    def recupere_nonce(self) -> str:
        return secrets.token_hex(16)


def fabrique_adaptateur_chiffrement() -> AdaptateurChiffrement:
    configuration = recupere_configuration().chiffrement
    service_de_chiffrement = fabrique_fournisseur_de_chiffrement(
        recupere_configuration()
    )
    return AdaptateurChiffrementStandard(configuration, service_de_chiffrement)
