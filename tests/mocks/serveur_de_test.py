from pathlib import Path
from typing import Callable, Dict, Optional
from unittest.mock import Mock

from openai.types.chat.chat_completion import Choice

from adaptateur_chiffrement import AdaptateurChiffrementDeTest
from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.chiffrement import (
    AdaptateurChiffrement,
    fabrique_adaptateur_chiffrement,
)
from adaptateurs.journal import (
    AdaptateurJournal,
    fabrique_adaptateur_journal,
)
from client_albert_de_test import ClientAlbertMemoire
from configuration import Mode, Albert
from infra.fast_api.fabrique_adaptateur_base_de_donnees import (
    fabrique_adaptateur_base_de_donnees,
)
from schemas.albert import Paragraphe, ReponseQuestion, ReclassePayload, ReclasseReponse
from schemas.violations import Violation
from serveur import fabrique_serveur
from services.fabrique_service_albert import fabrique_service_albert
from services.service_albert import ServiceAlbert, Prompts

NONCE = "un-nonce"
adaptateur_chiffrement = AdaptateurChiffrementDeTest().qui_retourne_nonce(NONCE)


class ConstructeurAdaptateurJournal:
    def __init__(self):
        self._mock = Mock()

    def construis(self):
        return self._mock


class ConstructeurServiceAlbert:
    def __init__(self):
        self._mock = Mock()
        self._mock.recherche_paragraphes.return_value = []

    def avec_prompt_systeme(self, prompt: str):
        self._mock.prompt_systeme = prompt
        return self

    def qui_retourne_les_paragraphes(self, paragraphes: list[Paragraphe]):
        self._mock.recherche_paragraphes.return_value = paragraphes
        return self

    def qui_repond_aux_questions(self, reponse: ReponseQuestion):
        self._mock.pose_question.return_value = reponse
        return self

    def construis(self):
        return self._mock


class ServiceAlbertMemoire(ServiceAlbert):
    def __init__(self) -> None:
        self.leve_une_erreur_sur_pose_question = False
        super().__init__(
            Albert.Service(  # type: ignore[attr-defined]
                collection_nom_anssi_lab="",
                collection_id_anssi_lab=1,
                reclassement_active=False,
                modele_reclassement="",
            ),
            ClientAlbertMemoire(),
            False,
            Prompts(prompt_systeme="", prompt_reclassement=""),
        )

    def recherche_paragraphes(self, question: str) -> list[Paragraphe]:
        return []

    def pose_question(
        self, question: str, prompt: Optional[str] = None
    ) -> ReponseQuestion:
        if self.leve_une_erreur_sur_pose_question:
            raise Exception("Erreur sur pose_question")
        return ReponseQuestion(
            reponse="", paragraphes=[], question=question, violation=None
        )

    def reclasse(self, payload: ReclassePayload):
        return ReclasseReponse(data=[])

    def _recupere_reponse_paragraphes_et_violation(
        self, propositions_albert: list[Choice], paragraphes: list[Paragraphe]
    ) -> tuple[str, list[Paragraphe], Violation | None]:
        return "", paragraphes, None

    def qui_leve_une_erreur_sur_pose_question(self):
        self.leve_une_erreur_sur_pose_question = True


class ConstructeurServeur:
    def __init__(
        self,
        adaptateur_chiffrement: AdaptateurChiffrement,
        max_requetes_par_minute: int = 600,
        mode: Mode = Mode.PRODUCTION,
    ):
        self._adaptateur_chiffrement = (
            adaptateur_chiffrement or fabrique_adaptateur_chiffrement()
        )
        self._max_requetes_par_minute = max_requetes_par_minute
        self._mode = mode
        self._dependances: Dict[Callable, Callable] = {}
        self._dependances[fabrique_adaptateur_chiffrement] = (
            lambda: adaptateur_chiffrement
        )
        self.pages_statiques: Path = Path()

    def avec_service_albert(self, service_albert: ServiceAlbert):
        self._dependances[fabrique_service_albert] = lambda: service_albert
        return self

    def avec_adaptateur_base_de_donnees(
        self, adaptateur_base_de_donnees: AdaptateurBaseDeDonnees
    ):
        self._dependances[fabrique_adaptateur_base_de_donnees] = (
            lambda: adaptateur_base_de_donnees
        )
        return self

    def avec_adaptateur_chiffrement_pour_les_routes_d_api(
        self, adaptateur_chiffrement: AdaptateurChiffrement
    ):
        self._dependances[fabrique_adaptateur_chiffrement] = (
            lambda: adaptateur_chiffrement
        )
        return self

    def avec_adaptateur_journal(self, adaptateur_journal: AdaptateurJournal):
        self._dependances[fabrique_adaptateur_journal] = lambda: adaptateur_journal
        return self

    def avec_pages_statiques(self, pages_statiques):
        self.pages_statiques = pages_statiques
        return self

    def construis(self):
        self._serveur = fabrique_serveur(
            self._max_requetes_par_minute,
            self._mode,
            f"{self.pages_statiques}/ui/dist/",
        )
        for clef, dependance in self._dependances.items():
            self._serveur.dependency_overrides[clef] = dependance
        return self._serveur
