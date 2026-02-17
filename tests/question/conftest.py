import uuid
from typing import Callable, Optional

import pytest

from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from adaptateurs.journal import AdaptateurJournalMemoire
from question.question import ConfigurationQuestion
from schemas.albert import ReponseQuestion
from schemas.retour_utilisatrice import Conversation, Interaction
from tests.conftest import ConstructeurDeReponseQuestion
from adaptateur_chiffrement import AdaptateurChiffrementDeTest
from serveur_de_test import ServiceAlbertMemoire


class ConstructeurDeConversation:
    def __init__(self, reponse_question: ReponseQuestion):
        super().__init__()
        self.interaction = Interaction(
            reponse_question=reponse_question, retour_utilisatrice=None, id=uuid.uuid4()
        )

    def construis(self) -> Conversation:
        return Conversation(self.interaction)


@pytest.fixture()
def un_constructeur_de_conversation(
    un_constructeur_de_reponse_question,
) -> Callable[[Optional[ConstructeurDeReponseQuestion]], ConstructeurDeConversation]:
    def _un_constructeur_de_conversation(
        constructeur_de_reponse_question: Optional[
            ConstructeurDeReponseQuestion
        ] = None,
    ):
        return ConstructeurDeConversation(
            constructeur_de_reponse_question.construis()
            if constructeur_de_reponse_question is not None
            else un_constructeur_de_reponse_question().construis()
        )

    return _un_constructeur_de_conversation


@pytest.fixture()
def une_configuration_complete() -> Callable[
    [],
    tuple[
        ConfigurationQuestion,
        ServiceAlbertMemoire,
        AdaptateurBaseDeDonneesEnMemoire,
        AdaptateurJournalMemoire,
    ],
]:
    def _une_configuration_complete() -> tuple[
        ConfigurationQuestion,
        ServiceAlbertMemoire,
        AdaptateurBaseDeDonneesEnMemoire,
        AdaptateurJournalMemoire,
    ]:
        service_albert = ServiceAlbertMemoire()
        adaptateur_chiffrement = AdaptateurChiffrementDeTest()
        adaptateur_base_de_donnees = AdaptateurBaseDeDonneesEnMemoire()
        adaptateur_journal = AdaptateurJournalMemoire()
        configuration = ConfigurationQuestion(
            adaptateur_chiffrement=adaptateur_chiffrement,
            adaptateur_base_de_donnees=adaptateur_base_de_donnees,
            adaptateur_journal=adaptateur_journal,
            service_albert=service_albert,
        )

        return (
            configuration,
            service_albert,
            adaptateur_base_de_donnees,
            adaptateur_journal,
        )

    return _une_configuration_complete
