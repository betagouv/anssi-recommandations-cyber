import pytest
import uuid
from typing import Callable, Optional

from adaptateur_chiffrement import AdaptateurChiffrementDeTest
from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from adaptateurs.journal import AdaptateurJournalMemoire
from client_albert_de_test import ClientAlbertMemoire
from question.question import ConfigurationQuestion
from question.reformulateur_de_question import ReformulateurDeQuestion
from schemas.albert import ReponseQuestion
from schemas.retour_utilisatrice import Conversation, Interaction
from serveur_de_test import ServiceAlbertMemoire, MappingReponsesMaitriseesDeTest
from services.service_albert import ServiceAlbert, Prompts
from tests.conftest import ConstructeurDeReponseQuestion


class ConstructeurDeConversation:
    def __init__(self, reponse_question: ReponseQuestion):
        super().__init__()
        self.interactions: list[Interaction] = []
        self.interaction = Interaction(
            reponse_question=reponse_question, retour_utilisatrice=None, id=uuid.uuid4()
        )

    def avec_interaction(self, interaction: Interaction):
        self.interaction = interaction
        return self

    def ajoute_interaction(self, interaction: Interaction):
        self.interactions.append(interaction)
        return self

    def construis(self) -> Conversation:
        conversation = Conversation(self.interaction)
        for interaction in self.interactions:
            conversation.ajoute_interaction(interaction)
        return conversation


class ReformulateurDeQuestionDeTest(ReformulateurDeQuestion):
    def __init__(self):
        super().__init__(ClientAlbertMemoire(), "", "")

    def reformule(
        self, question: str, conversation: Optional[Conversation] = None
    ) -> str | None:
        return question


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
    [Optional[ServiceAlbert]],
    tuple[
        ConfigurationQuestion,
        ServiceAlbertMemoire | ServiceAlbert,
        AdaptateurBaseDeDonneesEnMemoire,
        AdaptateurJournalMemoire,
        AdaptateurChiffrementDeTest,
    ],
]:
    def _une_configuration_complete(
        service_albert: Optional[ServiceAlbert] = None,
    ) -> tuple[
        ConfigurationQuestion,
        ServiceAlbertMemoire | ServiceAlbert,
        AdaptateurBaseDeDonneesEnMemoire,
        AdaptateurJournalMemoire,
        AdaptateurChiffrementDeTest,
    ]:
        if service_albert is None:
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
            adaptateur_chiffrement,
        )

    return _une_configuration_complete


@pytest.fixture()
def un_service_albert_avec_un_client_memoire(
    un_reclasseur,
    un_adaptateur_executeur_de_requetes,
    une_configuration_de_service_albert,
) -> Callable[[ClientAlbertMemoire, Prompts], ServiceAlbert]:
    def _un_service_albert_avec_un_client_memoire(
        client_albert_memoire: ClientAlbertMemoire, prompts: Prompts
    ) -> ServiceAlbert:
        return ServiceAlbert(
            configuration_service_albert=une_configuration_de_service_albert(),
            client=client_albert_memoire,
            utilise_recherche_hybride=False,
            prompts=prompts,
            reformulateur=ReformulateurDeQuestionDeTest(),
            mapping_reponses=MappingReponsesMaitriseesDeTest(),
            reclasseur=un_reclasseur,
            executeur_de_requetes=un_adaptateur_executeur_de_requetes,
        )

    return _un_service_albert_avec_un_client_memoire
