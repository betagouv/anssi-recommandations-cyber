from client_albert_de_test import (
    ClientAlbertMemoire,
    un_choix_de_proposition,
    un_resultat_de_recherche,
)
from adaptateurs.bus_evenements import BusEvenementsEnMemoire
from configuration import TypeReclasseur
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from question.reclassement.reclassement import Reclasseur, ResultatReclassement
from reformulateur_de_question_de_test import ReformulateurDeQuestionDeTest
from schemas.albert import ParagrapheReponseMaitrisee
from services.service_albert import ServiceAlbert

QUESTION = "Comment choisir un mot de passe ?"
REPONSE = "Utiliser un mot de passe long et unique."
NOM_DOCUMENT = "authentification.pdf"


class ReclasseurAvecContexteMsc(Reclasseur):
    def __init__(self) -> None:
        self.paragraphes_recus: list[ParagrapheReponseMaitrisee] = []

    def reclasse(self, question, paragraphes):
        self.paragraphes_recus = paragraphes
        return ResultatReclassement(paragraphes, paragraphes)


def test_service_albert_charge_et_transmet_le_contexte_msc_au_reclassement(
    une_configuration_de_service_albert,
    un_adaptateur_executeur_de_requetes,
):
    client = ClientAlbertMemoire()
    client.avec_les_resultats(
        [
            un_resultat_de_recherche()
            .ayant_pour_contenu(REPONSE)
            .ayant_pour_document(NOM_DOCUMENT)
            .construis()
        ]
    )
    client.avec_les_propositions(
        [un_choix_de_proposition().ayant_pour_contenu(REPONSE).construis()]
    )
    executeur = un_adaptateur_executeur_de_requetes
    executeur.reponse = [
        {
            "id": "guide-authentification",
            "nom": "Guide des mots de passe",
            "description": "Choix et gestion des mots de passe.",
            "listeDocuments": [
                {"libelle": "Authentification", "nomFichier": NOM_DOCUMENT}
            ],
            "dateMiseAJour": "2026-01-01",
        }
    ]
    reclasseur = ReclasseurAvecContexteMsc()
    configuration = une_configuration_de_service_albert(
        type_reclasseur=TypeReclasseur.LLM_PARALLELE
    )
    service = ServiceAlbert(
        configuration,
        client,
        False,
        "{chunks}",
        ReformulateurDeQuestionDeTest(),
        MappingReponsesMaitrisees({}),
        reclasseur,
        executeur,
        bus_evenements=BusEvenementsEnMemoire(),
    )

    reponse = service.pose_question(question=QUESTION)

    assert reclasseur.paragraphes_recus[0].contexte_document_msc.nom == (
        "Guide des mots de passe"
    )
    assert reponse.paragraphes[0].titre == "Guide des mots de passe"
