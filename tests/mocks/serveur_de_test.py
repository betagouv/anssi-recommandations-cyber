from serveur import fabrique_serveur
from configuration import Mode
from unittest.mock import Mock
from services.albert import ServiceAlbert, fabrique_service_albert
from schemas.client_albert import Paragraphe, ReponseQuestion
from adaptateurs.adaptateur_base_de_donnees_postgres import (
    fabrique_adaptateur_base_de_donnees_retour_utilisatrice,
)
from adaptateurs import AdaptateurBaseDeDonnees


class ConstructeurServiceAlbert:
    def __init__(self):
        self._mock = Mock()
        self._mock.recherche_paragraphes.return_value = []

    def qui_retourne_les_paragraphes(self, paragraphes: list[Paragraphe]):
        self._mock.recherche_paragraphes.return_value = paragraphes
        return self

    def qui_repond_aux_questions(self, reponse: ReponseQuestion):
        self._mock.pose_question.return_value = reponse
        return self

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

    def avec_adaptateur_base_de_donnees(
        self, adaptateur_base_de_donnees: AdaptateurBaseDeDonnees
    ):
        self._serveur.dependency_overrides[
            fabrique_adaptateur_base_de_donnees_retour_utilisatrice
        ] = lambda: adaptateur_base_de_donnees
        return self

    def construit(self):
        return self._serveur


serveur = ConstructeurServeur().construit()
