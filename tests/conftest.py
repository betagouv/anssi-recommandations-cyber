import random
import uuid
from pathlib import Path

import pytest
from fastapi import FastAPI
from mypy_extensions import DefaultNamedArg
from typing import Callable, Optional

from adaptateur_chiffrement import AdaptateurChiffrementDeTest
from adaptateurs import AdaptateurBaseDeDonnees
from adaptateurs.chiffrement import AdaptateurChiffrement
from adaptateurs.horloge import Horloge
from adaptateurs.journal import AdaptateurJournal
from configuration import Mode
from schemas.albert import Paragraphe, ReponseQuestion
from schemas.api import QuestionRequete
from schemas.retour_utilisatrice import Interaction
from schemas.type_utilisateur import TypeUtilisateur
from serveur_de_test import (
    ConstructeurServeur,
)
from services.service_albert import ServiceAlbert


class ConstructeurDeParagraphe:
    def __init__(self):
        self.url = "http://mondocument.local"
        self.score_similarite = random.uniform(0, 1)
        self.contenu = "un contenu"
        self.numero_page = random.randint(1, 100)
        self.nom_document = "Mon document"

    def avec_contenu(self, contenu: str):
        self.contenu = contenu
        return self

    def ayant_comme_score(self, score: float):
        self.score_similarite = score
        return self

    def a_la_page(self, numero_page: int):
        self.numero_page = numero_page
        return self

    def dans_le_document(self, nom_document: str):
        self.nom_document = nom_document
        self.url = f"{self.url}/{nom_document}"
        return self

    def construis(self) -> Paragraphe:
        return Paragraphe(
            nom_document=self.nom_document,
            numero_page=self.numero_page,
            contenu=self.contenu,
            score_similarite=self.score_similarite,
            url=self.url,
        )


@pytest.fixture()
def un_constructeur_de_paragraphe() -> Callable[
    [],
    ConstructeurDeParagraphe,
]:
    def _un_constructeur_de_paragraphe():
        return ConstructeurDeParagraphe()

    return _un_constructeur_de_paragraphe


class ConstructeurDeReponseQuestion:
    def __init__(self):
        super().__init__()
        self.reponse = "Une réponse"
        self.question = "Une question"
        self.paragraphes = []
        self.violation = None

    def a_partir_d_une_requete(self, requete_question: QuestionRequete):
        self.question = requete_question.question
        return self

    def donnant_en_reponse(self, reponse: str):
        self.reponse = reponse
        return self

    def avec_les_paragraphes(self, paragraphes: list[Paragraphe]):
        self.paragraphes = paragraphes
        return self

    def avec_une_question(self, question: str):
        self.question = question
        return self

    def construis(self) -> ReponseQuestion:
        return ReponseQuestion(
            reponse=self.reponse,
            paragraphes=self.paragraphes,
            question=self.question,
            violation=self.violation,
        )


@pytest.fixture()
def un_constructeur_de_reponse_question() -> Callable[
    [], ConstructeurDeReponseQuestion
]:
    def _un_constructeur_de_reponse_question():
        return ConstructeurDeReponseQuestion()

    return _un_constructeur_de_reponse_question


@pytest.fixture()
def une_reponse_question():
    return ReponseQuestion(
        reponse="Une réponse", question="Une question", paragraphes=[], violation=None
    )


@pytest.fixture(autouse=True)
def pages_statiques(tmp_path) -> Path:
    def crees_la_page_statique(page: Path):
        page.write_text(
            "<html><body>%%NONCE_A_INJECTER%%</body></html>",
            encoding="utf-8",
        )

    root = tmp_path
    (root / "ui" / "dist" / "assets").mkdir(parents=True, exist_ok=True)
    (root / "ui" / "dist" / "fonts").mkdir(parents=True, exist_ok=True)
    (root / "ui" / "dist" / "icons").mkdir(parents=True, exist_ok=True)
    (root / "ui" / "dist" / "images").mkdir(parents=True, exist_ok=True)

    crees_la_page_statique(root / "ui" / "dist" / "index.html")
    crees_la_page_statique(root / "ui" / "dist" / "politique-confidentialite.html")
    crees_la_page_statique(root / "ui" / "dist" / "cgu.html")
    return root


@pytest.fixture()
def un_adaptateur_de_chiffrement() -> Callable[
    [
        DefaultNamedArg(type=Optional[str], name="nonce"),
        DefaultNamedArg(type=Optional[str], name="hachage"),
        DefaultNamedArg(type=Optional[TypeUtilisateur | str], name="dechiffre"),
        DefaultNamedArg(type=Optional[bool], name="leve_une_erreur"),
    ],
    AdaptateurChiffrement,
]:
    def _un_adaptateur_de_chiffrement(
        *,
        nonce: Optional[str] = "nonce",
        hachage: Optional[str] = "test",
        dechiffre: Optional[TypeUtilisateur | str] = None,
        leve_une_erreur: Optional[bool] = False,
    ):
        adaptateur = AdaptateurChiffrementDeTest()
        if dechiffre:
            return adaptateur.qui_dechiffre(dechiffre)
        if leve_une_erreur:
            return adaptateur.qui_leve_une_erreur_au_dechiffrement()
        if nonce:
            adaptateur = adaptateur.qui_retourne_nonce(nonce)
        if hachage:
            adaptateur = adaptateur.qui_hache(hachage)
        return adaptateur

    return _un_adaptateur_de_chiffrement


@pytest.fixture()
def un_serveur_de_test(
    pages_statiques, un_adaptateur_de_chiffrement
) -> Callable[
    [
        DefaultNamedArg(type=Optional[Mode], name="mode"),
        DefaultNamedArg(
            type=Optional[AdaptateurChiffrement], name="adaptateur_chiffrement"
        ),
        DefaultNamedArg(type=Optional[int], name="rate_limit"),
        DefaultNamedArg(type=Optional[ServiceAlbert], name="service_albert"),
        DefaultNamedArg(
            type=Optional[AdaptateurBaseDeDonnees], name="adaptateur_base_de_donnees"
        ),
        DefaultNamedArg(type=Optional[AdaptateurJournal], name="adaptateur_journal"),
    ],
    FastAPI,
]:
    def _un_serveur_de_test(
        *,
        mode: Optional[Mode] = Mode.DEVELOPPEMENT,
        adaptateur_chiffrement: Optional[
            AdaptateurChiffrement
        ] = un_adaptateur_de_chiffrement(nonce="un-nonce"),
        rate_limit: Optional[int] = 600,
        service_albert: Optional[ServiceAlbert] = None,
        adaptateur_base_de_donnees: Optional[AdaptateurBaseDeDonnees] = None,
        adaptateur_journal: Optional[AdaptateurJournal] = None,
    ):
        serveur = ConstructeurServeur(
            mode=mode,  # type: ignore[arg-type]
            adaptateur_chiffrement=adaptateur_chiffrement,  # type: ignore[arg-type]
            max_requetes_par_minute=rate_limit,  # type: ignore[arg-type]
        ).avec_pages_statiques(pages_statiques)
        if service_albert:
            serveur = serveur.avec_service_albert(service_albert)
        if adaptateur_base_de_donnees:
            serveur = serveur.avec_adaptateur_base_de_donnees(
                adaptateur_base_de_donnees
            )
        if adaptateur_journal:
            serveur = serveur.avec_adaptateur_journal(adaptateur_journal)
        return serveur.construis()

    return _un_serveur_de_test


@pytest.fixture(autouse=True)
def reset_horloge_apres_test():
    yield
    Horloge.reinitialise()


class ConstructeurDInteraction:
    def __init__(self):
        super().__init__()
        self.reponse_question = ReponseQuestion(
            reponse="Je suis Albert, pour vous servir",
            paragraphes=[],
            question="une question",
            violation=None,
        )
        self.retour_utilisatrice = None

    def construis(self) -> Interaction:
        return Interaction(
            reponse_question=self.reponse_question,
            retour_utilisatrice=self.retour_utilisatrice,
            id=uuid.uuid4(),
        )

    def avec_question(self, question: str):
        self.reponse_question = ReponseQuestion(
            reponse=f"réponse : {question}",
            paragraphes=[],
            question=question,
            violation=None,
        )
        return self


@pytest.fixture()
def un_constructeur_d_interaction() -> Callable[[], ConstructeurDInteraction]:
    def _un_constructeur_d_interaction():
        return ConstructeurDInteraction()

    return _un_constructeur_d_interaction
