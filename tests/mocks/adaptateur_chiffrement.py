from unittest.mock import Mock
from infra.chiffrement.chiffrement import ServiceDeChiffrementEnClair


class ConstructeurAdaptateurChiffrement:
    def __init__(self):
        self._mock = Mock()
        service_chiffrement_en_clair = ServiceDeChiffrementEnClair()
        self._mock.service_de_chiffrement = service_chiffrement_en_clair

    def qui_hache(self, hache: str):
        self._mock.hache.return_value = hache
        return self

    def qui_retourne_nonce(self, nonce: str):
        self._mock.recupere_nonce.return_value = nonce
        return self

    def construis(self):
        return self._mock
