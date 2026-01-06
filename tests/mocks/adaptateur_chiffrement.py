from unittest.mock import Mock

from adaptateurs.chiffrement import AdaptateurChiffrement, AdaptateurChiffrementStandard
from configuration import Chiffrement
from infra.chiffrement.chiffrement import ServiceDeChiffrementEnClair
from schemas.type_utilisateur import TypeUtilisateur
from service_chiffrement_de_test import ServiceDeChiffrementDeTest


class ConstructeurAdaptateurChiffrement:
    def __init__(self):
        self._mock = Mock()
        self._mock.service_de_chiffrement = ServiceDeChiffrementEnClair()

    def qui_hache(self, hache: str):
        self._mock.hache.return_value = hache
        return self

    def qui_retourne_nonce(self, nonce: str):
        self._mock.recupere_nonce.return_value = nonce
        return self

    def qui_dechiffre(self, type_utilisateur: TypeUtilisateur):
        self._mock.dechiffre.return_value = type_utilisateur
        return self

    def construis(self):
        return self._mock


configuration_chiffrement = Chiffrement(clef_chiffrement="", sel_de_hachage="")


class ConstructeurAdaptateurChiffrementDeTest(AdaptateurChiffrement):
    def __init__(self):
        super().__init__(
            configuration=configuration_chiffrement,
            service_de_chiffrement=ServiceDeChiffrementEnClair(),
        )

    def hache(self, valeur: str) -> str:
        return valeur

    def recupere_nonce(self) -> str:
        return "nonce"

    def chiffre(self, contenu: str) -> str:
        return contenu

    def dechiffre(self, contenu_chiffre: str) -> str:
        return contenu_chiffre

    def qui_dechiffre(
        self, type_utilisateur: TypeUtilisateur | str
    ) -> AdaptateurChiffrement:
        return AdaptateurChiffrementStandard(
            configuration=configuration_chiffrement,
            service_de_chiffrement=ServiceDeChiffrementDeTest().qui_dechiffre(
                type_utilisateur
            ),
        )

    def qui_leve_une_erreur_au_dechiffrement(self) -> AdaptateurChiffrement:
        return AdaptateurChiffrementStandard(
            configuration=configuration_chiffrement,
            service_de_chiffrement=ServiceDeChiffrementDeTest().qui_leve_une_erreur_au_dechiffrement(),
        )
