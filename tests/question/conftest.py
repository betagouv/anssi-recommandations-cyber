import uuid
from typing import Callable, Optional

import pytest

from adaptateurs import AdaptateurBaseDeDonneesEnMemoire
from adaptateurs.journal import AdaptateurJournalMemoire
from client_albert_de_test import ClientAlbertMemoire
from question.question import ConfigurationQuestion
from schemas.albert import ReponseQuestion
from schemas.retour_utilisatrice import Conversation, Interaction
from tests.conftest import ConstructeurDeReponseQuestion
from adaptateur_chiffrement import AdaptateurChiffrementDeTest
from serveur_de_test import ServiceAlbertMemoire

from configuration import Albert
from services.service_albert import ServiceAlbert, Prompts


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
    [Optional[ServiceAlbert]],
    tuple[
        ConfigurationQuestion,
        ServiceAlbertMemoire | ServiceAlbert,
        AdaptateurBaseDeDonneesEnMemoire,
        AdaptateurJournalMemoire,
    ],
]:
    def _une_configuration_complete(
        service_albert: Optional[ServiceAlbert] = None,
    ) -> tuple[
        ConfigurationQuestion,
        ServiceAlbertMemoire | ServiceAlbert,
        AdaptateurBaseDeDonneesEnMemoire,
        AdaptateurJournalMemoire,
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
        )

    return _une_configuration_complete


@pytest.fixture()
def un_service_albert_avec_un_client_memoire() -> Callable[
    [ClientAlbertMemoire, Prompts], ServiceAlbert
]:
    def _un_service_albert_avec_un_client_memoire(
        client_albert_memoire: ClientAlbertMemoire, prompts: Prompts
    ) -> ServiceAlbert:
        return ServiceAlbert(
            configuration_service_albert=Albert.Service(  # type:ignore[attr-defined]
                collection_nom_anssi_lab="",
                collection_id_anssi_lab=42,
                reclassement_active=False,
                modele_reclassement="Aucun",
                taille_fenetre_historique=10,
            ),
            client=client_albert_memoire,
            utilise_recherche_hybride=False,
            prompts=prompts,
        )

    return _un_service_albert_avec_un_client_memoire
