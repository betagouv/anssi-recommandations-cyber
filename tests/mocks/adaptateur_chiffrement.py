from unittest.mock import Mock


class ConstructeurAdaptateurChiffrement:
    def __init__(self):
        self._mock = Mock()

    def qui_hache(self, hache: str):
        self._mock.hache.return_value = hache
        return self

    def qui_retourne_nonce(self, nonce: str):
        self._mock.recupere_nonce.return_value = nonce
        return self

    def construis(self):
        return self._mock
