from serveur import fabrique_serveur
from configuration import Mode
from unittest.mock import Mock


class ConstructeurServiceAlbert:
    def __init__(self):
        self._mock = Mock()
        self._mock.recherche_paragraphes.return_value = []

    def construit(self):
        return self._mock


serveur = fabrique_serveur(Mode.PRODUCTION)
