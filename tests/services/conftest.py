import pytest
from concurrent.futures import ThreadPoolExecutor

from adaptateurs.bus_evenements import BusEvenementsEnMemoire
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from question.reformulateur_de_question import ReformulateurDeQuestion
from reformulateur_de_question_de_test import ReformulateurDeQuestionDeTest
from services.coordinateur_reclassement_parallele import (
    CoordinateurReclassementParallele,
)
from services.service_albert import Prompts, ServiceAlbert


@pytest.fixture()
def un_service_albert_de_test():
    def construit(
        configuration,
        client,
        *,
        reclasseur,
        executeur_de_requetes,
        reformulateur=None,
        mapping_reponses=None,
        bus_evenements=None,
        prompts=None,
        utilise_recherche_hybride=False,
    ):
        return ServiceAlbert(
            configuration_service_albert=configuration,
            client=client,
            utilise_recherche_hybride=utilise_recherche_hybride,
            prompts=prompts if prompts is not None else Prompts("", ""),
            reformulateur=(
                reformulateur
                if reformulateur is not None
                else ReformulateurDeQuestionDeTest()
            ),
            mapping_reponses=(
                mapping_reponses
                if mapping_reponses is not None
                else MappingReponsesMaitrisees({})
            ),
            reclasseur=reclasseur,
            executeur_de_requetes=executeur_de_requetes,
            bus_evenements=(
                bus_evenements
                if bus_evenements is not None
                else BusEvenementsEnMemoire()
            ),
        )

    return construit


@pytest.fixture()
def un_reformulateur_albert_de_test():
    def construit(client, *, prompt="", modele="", bus_evenements=None):
        return ReformulateurDeQuestion(
            client_albert=client,
            prompt_de_reformulation=prompt,
            modele_reformulation=modele,
            bus_evenements=(
                bus_evenements
                if bus_evenements is not None
                else BusEvenementsEnMemoire()
            ),
        )

    return construit


@pytest.fixture()
def un_coordinateur_reclassement():
    coordinateur = CoordinateurReclassementParallele(ThreadPoolExecutor(max_workers=5))
    yield coordinateur
    coordinateur.ferme()
