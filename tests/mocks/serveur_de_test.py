from pathlib import Path

from openai.types.chat.chat_completion import Choice
from typing import Callable, Dict, Optional

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
from schemas.retour_utilisatrice import Conversation
from schemas.violations import Violation
from serveur import fabrique_serveur
from services.fabrique_service_albert import fabrique_service_albert
from services.service_albert import ServiceAlbert, Prompts

NONCE = "un-nonce"
adaptateur_chiffrement = AdaptateurChiffrementDeTest().qui_retourne_nonce(NONCE)


class ServiceAlbertMemoire(ServiceAlbert):
    def __init__(self) -> None:
        self.paragraphes: list[Paragraphe] = []
        self.reponse = None
        self.recherche_paragraphes_a_ete_appele = False
        self.leve_une_erreur_sur_pose_question = False
        self.question_recue: str | None = None
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
        self.recherche_paragraphes_a_ete_appele = True
        return self.paragraphes

    def pose_question(
        self,
        *,
        question: str,
        prompt: Optional[str] = None,
        conversation: Optional[Conversation] = None,
    ) -> ReponseQuestion:
        self.question_recue = question
        if self.leve_une_erreur_sur_pose_question:
            raise Exception("Erreur sur pose_question")
        if self.reponse is not None:
            return self.reponse
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

    def ajoute_reponse(self, reponse):
        self.reponse = reponse

    def ajoute_paragraphes(self, paragraphes):
        self.paragraphes.extend(paragraphes)


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
