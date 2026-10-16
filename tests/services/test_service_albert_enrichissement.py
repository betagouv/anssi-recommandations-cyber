from adaptateurs.bus_evenements import BusEvenementsEnMemoire
from client_albert_de_test import (
    ClientAlbertMemoire,
    un_choix_de_proposition,
    un_resultat_de_recherche,
)
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from reformulateur_de_question_de_test import ReformulateurDeQuestionDeTest
from serveur_de_test import AdaptateurExecuteurDeRequetesMemoire
from schemas.albert import (
    Paragraphe,
    RechercheChunk,
    RechercheMetadonnees,
    UniteSource,
)
from services.reclasseur import Reclasseur, ResultatReclassement
from services.service_albert import Prompts, ServiceAlbert
from services.strategie_enrichissement_paragraphes import (
    ParPagePrecedenteEtSuivante,
)
from services.unites_source import (
    premiere_unite_substantielle,
    unites_du_paragraphe,
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


def test_sans_chunks_enrichis_decoupe_aux_frontieres_de_paragraphes_sans_tronquer():
    premier_paragraphe = "Texte de début.\nUne seconde ligne."
    second_paragraphe = "Règle utile. " + ("mot " * 200)
    paragraphe = Paragraphe(
        contenu=f"{premier_paragraphe}\n\n{second_paragraphe}",
        url="https://exemple.test/guide.pdf",
        score_similarite=0.8,
        numero_page=23,
        nom_document="guide.pdf",
        type_de_bloc="type-source-existant",
        code_recommandation="R17",
        chemin_sections=["Chapitre", "Règle"],
    )

    unites = unites_du_paragraphe(paragraphe)

    assert [unite.contenu for unite in unites] == [
        premier_paragraphe,
        second_paragraphe,
    ]
    assert [unite.numero_page for unite in unites] == [23, 23]
    assert [unite.type_de_bloc for unite in unites] == [
        "type-source-existant",
        "type-source-existant",
    ]


def test_plage_mixte_de_navigation_et_contenu_cible_la_premiere_unite_substantielle():
    unites_source = [
        UniteSource(
            contenu="Entrée de sommaire",
            url="https://exemple.test/guide.pdf",
            numero_page=4,
            nom_document="guide.pdf",
            type_de_bloc="table_des_matieres",
        ),
        UniteSource(
            contenu="Recommandation substantielle",
            url="https://exemple.test/guide.pdf",
            numero_page=7,
            nom_document="guide.pdf",
            type_de_bloc="type-inconnu-non-blackliste",
        ),
    ]

    premiere = premiere_unite_substantielle(unites_source, 1, 2)

    assert premiere is unites_source[1]
    assert premiere_unite_substantielle(unites_source, 1, 1) is None
