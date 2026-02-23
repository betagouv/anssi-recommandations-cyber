import datetime
import psycopg2
from abc import ABC, abstractmethod
from enum import StrEnum
from pydantic import BaseModel
from typing import Literal, Optional

from configuration import BaseDeDonnees, recupere_configuration
from schemas.retour_utilisatrice import TagPositif, TagNegatif
from schemas.type_utilisateur import TypeUtilisateur


class Donnees(BaseModel):
    pass


class ParagrapheRetourne(BaseModel):
    nom_document: str
    numero_page: int


class DonneesConversationCreee(Donnees):
    id_conversation: str
    id_interaction: str
    longueur_question: int
    longueur_reponse: int
    longueur_paragraphes: int
    type_utilisateur: TypeUtilisateur
    question: Optional[str] = None
    sources: Optional[list[ParagrapheRetourne]] = None


class DonneesInteractionAjoutee(DonneesConversationCreee):
    pass


class DonneesViolationDetectee(Donnees):
    id_interaction: str
    type_violation: str


class DonneesAvisUtilisateurSoumis(Donnees):
    id_interaction: str
    type_retour: Literal["positif", "negatif"]
    tags: list[TagPositif | TagNegatif]
    type_utilisateur: TypeUtilisateur


class DonneesAvisUtilisateurSupprime(Donnees):
    id_interaction: str
    type_utilisateur: TypeUtilisateur


class TypeEvenement(StrEnum):
    CONVERSATION_CREEE = "CONVERSATION_CREEE"
    INTERACTION_AJOUTEE = "INTERACTION_AJOUTEE"
    VIOLATION_DETECTEE = "VIOLATION_DETECTEE"
    AVIS_UTILISATEUR_SOUMIS = "AVIS_UTILISATEUR_SOUMIS"
    AVIS_UTILISATEUR_SUPPRIME = "AVIS_UTILISATEUR_SUPPRIME"


class AdaptateurJournal(ABC):
    @abstractmethod
    def consigne_evenement(self, type: TypeEvenement, donnees: Donnees) -> None:
        pass


class AdaptateurJournalMemoire(AdaptateurJournal):
    def __init__(self):
        self.evenements: list[tuple[TypeEvenement, Donnees]] = []

    def consigne_evenement(self, type: TypeEvenement, donnees: Donnees) -> None:
        self.evenements.append((type, donnees))

    def les_evenements(self):
        return list(map(lambda e: {"donnees": e[1], "type": e[0]}, self.evenements))


class AdaptateurJournalPostgres(AdaptateurJournal):
    def __init__(self, configuration: BaseDeDonnees):
        self._connexion = psycopg2.connect(
            host=configuration.hote,
            database=configuration.nom,
            user=configuration.utilisateur,
            password=configuration.mot_de_passe,
            port=configuration.port,
        )
        self._connexion.autocommit = True

    def consigne_evenement(self, type: TypeEvenement, donnees: Donnees):
        curseur = self._get_curseur()
        curseur.execute(
            "INSERT INTO journal_mqc.evenements (date, type, donnees) VALUES (%s, %s, %s)",
            (datetime.datetime.now(), type, donnees.model_dump_json()),
        )

    def _get_curseur(self):
        return self._connexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def ferme_connexion(self) -> None:
        if self._connexion:
            self._connexion.close()


def fabrique_adaptateur_journal() -> AdaptateurJournal:
    configuration = recupere_configuration()
    return (
        AdaptateurJournalPostgres(configuration.base_de_donnees_journal)
        if configuration.base_de_donnees_journal
        else AdaptateurJournalMemoire()
    )
