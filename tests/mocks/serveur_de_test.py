from typing import Optional

from serveur import fabrique_serveur
from configuration import Mode
from unittest.mock import Mock
from services.albert import ServiceAlbert, fabrique_service_albert
from schemas.client_albert import Paragraphe, ReponseQuestion
from schemas.retour_utilisatrice import RetourUtilisatrice
from adaptateurs.adaptateur_base_de_donnees_postgres import (
    fabrique_adaptateur_base_de_donnees_retour_utilisatrice,
)
from adaptateurs.journal import (
    AdaptateurJournal,
    fabrique_adaptateur_journal,
)
from adaptateurs.chiffrement import (
    AdaptateurChiffrement,
    fabrique_adaptateur_chiffrement,
)
from adaptateurs import AdaptateurBaseDeDonnees


class ConstructeurAdaptateurBaseDeDonnees:
    def __init__(self):
        self._mock = Mock()
        self._mock.sauvegarde_interaction.return_value = "id-interaction-test"

    def avec_retour(self, retour: Optional[RetourUtilisatrice]):
        self._mock.ajoute_retour_utilisatrice.return_value = retour
        return self

    def construit(self):
        return self._mock


class ConstructeurAdaptateurChiffrement:
    def __init__(self):
        self._mock = Mock()

    def qui_hache(self, hache: str):
        self._mock.hache.return_value = hache
        return self

    def construit(self):
        return self._mock


class ConstructeurAdaptateurJournal:
    def __init__(self):
        self._mock = Mock()

    def construit(self):
        return self._mock


class ConstructeurServiceAlbert:
    def __init__(self):
        self._mock = Mock()
        self._mock.recherche_paragraphes.return_value = []

    def avec_prompt_systeme(self, prompt: str):
        self._mock.PROMPT_SYSTEME = prompt
        return self

    def qui_retourne_les_paragraphes(self, paragraphes: list[Paragraphe]):
        self._mock.recherche_paragraphes.return_value = paragraphes
        return self

    def qui_repond_aux_questions(self, reponse: ReponseQuestion):
        self._mock.pose_question.return_value = reponse
        return self

    def construit(self):
        return self._mock


class ConstructeurServeur:
    def __init__(self, mode: Mode = Mode.PRODUCTION):
        self._serveur = fabrique_serveur(mode)

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

    def avec_adaptateur_chiffrement(
        self, adaptateur_chiffrement: AdaptateurChiffrement
    ):
        self._serveur.dependency_overrides[fabrique_adaptateur_chiffrement] = (
            lambda: adaptateur_chiffrement
        )
        return self

    def avec_adaptateur_journal(self, adaptateur_journal: AdaptateurJournal):
        self._serveur.dependency_overrides[fabrique_adaptateur_journal] = (
            lambda: adaptateur_journal
        )
        return self

    def construit(self):
        return self._serveur


serveur = ConstructeurServeur().construit()
