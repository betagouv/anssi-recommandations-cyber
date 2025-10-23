from serveur import fabrique_serveur
from configuration import Mode
from unittest.mock import Mock
from services.albert import ServiceAlbert, fabrique_service_albert


class ConstructeurServiceAlbert:
    def __init__(self):
        self._mock = Mock()
        self._mock.recherche_paragraphes.return_value = []

    def construit(self):
        return self._mock


class ConstructeurServeur:
    def __init__(self):
        self._serveur = fabrique_serveur(Mode.PRODUCTION)

    def avec_service_albert(self, service_albert: ServiceAlbert):
        self._serveur.dependency_overrides[fabrique_service_albert] = (
            lambda: service_albert
        )
        return self

    def construit(self):
        return self._serveur


serveur = ConstructeurServeur().construit()
