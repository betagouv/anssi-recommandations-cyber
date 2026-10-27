from adaptateurs.bus_evenements import BusEvenementsEnMemoire
from client_albert_de_test import (
    ClientAlbertMemoire,
    un_choix_de_proposition,
    un_resultat_de_recherche,
)
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from question.reclassement.reclassement import Reclasseur, ResultatReclassement
from reformulateur_de_question_de_test import ReformulateurDeQuestionDeTest
from schemas.albert import (
    Paragraphe,
    RechercheChunk,
    RechercheMetadonnees,
)
from serveur_de_test import AdaptateurExecuteurDeRequetesMemoire
from services.service_albert import ServiceAlbert
from services.strategie_enrichissement_paragraphes import (
    ParPagePrecedenteEtSuivante,
)


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
        prompt_syteme="Sources : {chunks}",
        reformulateur=ReformulateurDeQuestionDeTest(),
        mapping_reponses=MappingReponsesMaitrisees({}),
        reclasseur=reclasseur,
        executeur_de_requetes=AdaptateurExecuteurDeRequetesMemoire(),
        bus_evenements=BusEvenementsEnMemoire(),
        strategie_enrichissement=StrategieEnrichissementDeTest(),
    )

    service_albert.pose_question(question="Une question")

    assert reclasseur.paragraphes_recus[0].contenu == "Contexte enrichi"


class RecuperateurChunksEnMemoire:
    def __init__(self, chunks: list[RechercheChunk]):
        self.chunks = chunks

    def recupere_chunks_document(self, identifiant_document: int):
        return self.chunks


def test_enrichit_conserve_chaque_chunk_et_ses_metadonnees_pour_le_reclassement():
    chunks = [
        RechercheChunk(
            content="Section de contexte.",
            metadata=RechercheMetadonnees(
                source_url="https://exemple.test/guide.pdf",
                page=5,
                nom_document="guide.pdf",
                type_de_bloc="type-source-verifie",
                code_recommandation="R12",
                chemin_sections=["Chapitre", "Contexte"],
                position_page=1,
                identifiant_document=42,
            ),
        ),
        RechercheChunk(
            content="Recommandation utile.",
            metadata=RechercheMetadonnees(
                source_url="https://exemple.test/guide.pdf",
                page=6,
                nom_document="guide.pdf",
                type_de_bloc="autre-type-verifie",
                code_recommandation="R13",
                chemin_sections=["Chapitre", "Recommandations"],
                position_page=2,
                identifiant_document=42,
            ),
        ),
    ]
    paragraphe = Paragraphe(
        contenu="Recommandation utile.",
        url="https://exemple.test/guide.pdf",
        score_similarite=0.8,
        numero_page=6,
        nom_document="guide.pdf",
        identifiant_document=42,
    )

    enrichis = ParPagePrecedenteEtSuivante(
        RecuperateurChunksEnMemoire(chunks)
    ).enrichis([paragraphe])[0]

    assert [unite.contenu for unite in enrichis.unites_source] == [
        "Section de contexte.",
        "Recommandation utile.",
    ]
    assert [unite.numero_page for unite in enrichis.unites_source] == [5, 6]
    assert [unite.type_de_bloc for unite in enrichis.unites_source] == [
        "type-source-verifie",
        "autre-type-verifie",
    ]
    assert [unite.code_recommandation for unite in enrichis.unites_source] == [
        "R12",
        "R13",
    ]
    assert [unite.chemin_sections for unite in enrichis.unites_source] == [
        ["Chapitre", "Contexte"],
        ["Chapitre", "Recommandations"],
    ]
    assert "unites_source" not in enrichis.model_dump()
