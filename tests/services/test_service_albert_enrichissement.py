from adaptateurs.bus_evenements import BusEvenementsEnMemoire
from client_albert_de_test import (
    ClientAlbertMemoire,
    un_choix_de_proposition,
    un_resultat_de_recherche,
)
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from reformulateur_de_question_de_test import ReformulateurDeQuestionDeTest
from serveur_de_test import AdaptateurExecuteurDeRequetesMemoire
from schemas.albert import Paragraphe
from services.reclasseur import Reclasseur, ResultatReclassement
from services.service_albert import Prompts, ServiceAlbert


class StrategieEnrichissementDeTest:
    def enrichis(self, paragraphes: list[Paragraphe]) -> list[Paragraphe]:
        return [
            paragraphe.model_copy(update={"contenu": "Contexte enrichi"})
            for paragraphe in paragraphes
        ]


class ReclasseurQuiConserveLesParagraphes(Reclasseur):
    def __init__(self):
        self.paragraphes_recus: list[Paragraphe] = []

    def reclasse(
        self, question: str, paragraphes: list[Paragraphe]
    ) -> ResultatReclassement:
        self.paragraphes_recus = paragraphes
        return ResultatReclassement(paragraphes, paragraphes)


def test_pose_question_enrichit_les_paragraphes_avant_le_reclassement(
    une_configuration_de_service_albert,
):
    client_albert = ClientAlbertMemoire()
    client_albert.avec_les_resultats(
        [un_resultat_de_recherche().ayant_pour_contenu("Contenu source").construis()]
    )
    client_albert.avec_les_propositions(
        [un_choix_de_proposition().ayant_pour_contenu("Réponse").construis()]
    )
    reclasseur = ReclasseurQuiConserveLesParagraphes()
    service_albert = ServiceAlbert(
        configuration_service_albert=une_configuration_de_service_albert(),
        client=client_albert,
        utilise_recherche_hybride=False,
        prompts=Prompts(prompt_systeme="Sources : {chunks}", prompt_reclassement=""),
        reformulateur=ReformulateurDeQuestionDeTest(),
        mapping_reponses=MappingReponsesMaitrisees({}),
        reclasseur=reclasseur,
        executeur_de_requetes=AdaptateurExecuteurDeRequetesMemoire(),
        bus_evenements=BusEvenementsEnMemoire(),
        strategie_enrichissement=StrategieEnrichissementDeTest(),
    )

    service_albert.pose_question(question="Une question")

    assert reclasseur.paragraphes_recus[0].contenu == "Contexte enrichi"
