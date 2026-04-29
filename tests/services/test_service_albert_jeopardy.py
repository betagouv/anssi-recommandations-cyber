from client_albert_de_test import ClientAlbertMemoire, un_resultat_de_recherche
from configuration import Albert
from infra.mapping_reponses_maitrisees import MappingReponsesMaitrisees
from question.reformulateur_de_question import ReformulateurDeQuestion
from schemas.albert import (
    RechercheMetadonneesJeopardy,
    RechercheChunkJeopardy,
    ResultatRechercheJeopardy,
)
from services.service_albert import ServiceAlbert, Prompts

PROMPTS = Prompts(
    prompt_systeme="Prompt système",
    prompt_reclassement="Prompt reclassement",
)


def test_recherche_jeopardy_retourne_les_chunks_sources():
    client_albert_memoire = ClientAlbertMemoire()

    # Résultats jeopardy (questions générées)
    resultats_jeopardy = [
        ResultatRechercheJeopardy(
            chunk=RechercheChunkJeopardy(
                content="Question générée 1 ?",
                metadata=RechercheMetadonneesJeopardy(
                    source_id_document="4065642",
                    source_id_chunk=73,
                    source_numero_page=17,
                ),
            ),
            score=0.9,
        ),
        ResultatRechercheJeopardy(
            chunk=RechercheChunkJeopardy(
                content="Question générée 2 ?",
                metadata=RechercheMetadonneesJeopardy(
                    source_id_document="4065642",
                    source_id_chunk=74,
                    source_numero_page=18,
                ),
            ),
            score=0.8,
        ),
    ]
    client_albert_memoire.avec_les_resultats_jeopardy(resultats_jeopardy)

    # Chunks sources correspondants
    chunks_sources = [
        un_resultat_de_recherche()
        .ayant_pour_contenu("Contenu du chunk 73")
        .construis(),
        un_resultat_de_recherche()
        .ayant_pour_contenu("Contenu du chunk 74")
        .construis(),
    ]
    client_albert_memoire.avec_chunks_par_id(chunks_sources)

    configuration = Albert.Service(
        collection_nom_anssi_lab="",
        collection_id_anssi_lab=157814,
        collection_id_anssi_lab_jeopardy=161155,
        reclassement_active=False,
        modele_reclassement="",
        taille_fenetre_historique=2,
        jeopardy_active=False,
        seuil_reponse_maitrisee=0.5,
    )

    service_albert = ServiceAlbert(
        configuration_service_albert=configuration,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
        reformulateur=ReformulateurDeQuestion(client_albert_memoire, "", ""),
        mapping_reponses=MappingReponsesMaitrisees({}),
    )

    paragraphes = service_albert._ServiceAlbert__recherche_dans_collection_jeopardy(
        "Ma question ?"
    )

    assert len(paragraphes) == 2
    assert paragraphes[0].contenu == "Contenu du chunk 73"
    assert paragraphes[1].contenu == "Contenu du chunk 74"
    assert client_albert_memoire.payload_jeopardy_recu.collection_ids == [161155]


def test_recherche_paragraphes_fusionne_resultats_classique_et_jeopardy():
    client_albert_memoire = ClientAlbertMemoire()

    resultats_classiques = [
        un_resultat_de_recherche()
        .ayant_pour_contenu(f"Chunk classique {i}")
        .construis()
        for i in range(5)
    ]

    resultats_jeopardy = [
        ResultatRechercheJeopardy(
            chunk=RechercheChunkJeopardy(
                content=f"Question {i}",
                metadata=RechercheMetadonneesJeopardy(
                    source_id_document="4065642",
                    source_id_chunk=100 + i,
                    source_numero_page=i,
                ),
            ),
            score=0.8,
        )
        for i in range(5)
    ]
    client_albert_memoire.avec_les_resultats_jeopardy(resultats_jeopardy)

    chunks_sources_jeopardy = [
        un_resultat_de_recherche()
        .ayant_pour_contenu(f"Chunk source jeopardy {i}")
        .construis()
        for i in range(5)
    ]

    client_albert_memoire.avec_les_resultats(resultats_classiques)
    client_albert_memoire.avec_chunks_par_id(chunks_sources_jeopardy)

    configuration = Albert.Service(
        collection_nom_anssi_lab="",
        collection_id_anssi_lab=157814,
        collection_id_anssi_lab_jeopardy=161155,
        reclassement_active=False,
        modele_reclassement="",
        taille_fenetre_historique=2,
        jeopardy_active=True,
        seuil_reponse_maitrisee=0.5,
    )

    service_albert = ServiceAlbert(
        configuration_service_albert=configuration,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
        reformulateur=ReformulateurDeQuestion(client_albert_memoire, "", ""),
        mapping_reponses=MappingReponsesMaitrisees({}),
    )

    paragraphes = service_albert.recherche_paragraphes("Ma question ?")

    assert len(paragraphes) == 10


def test_recherche_paragraphes_dedoublonne_les_chunks_communs():
    client_albert_memoire = ClientAlbertMemoire()

    resultats_classiques = [
        un_resultat_de_recherche().ayant_pour_contenu("Chunk unique 1").construis(),
        un_resultat_de_recherche().ayant_pour_contenu("Chunk commun").construis(),
        un_resultat_de_recherche().ayant_pour_contenu("Chunk unique 2").construis(),
    ]

    resultats_jeopardy = [
        ResultatRechercheJeopardy(
            chunk=RechercheChunkJeopardy(
                content="Question 1",
                metadata=RechercheMetadonneesJeopardy(
                    source_id_document="4065642",
                    source_id_chunk=100,
                    source_numero_page=1,
                ),
            ),
            score=0.9,
        ),
    ]
    client_albert_memoire.avec_les_resultats_jeopardy(resultats_jeopardy)

    chunks_sources_jeopardy = [
        un_resultat_de_recherche().ayant_pour_contenu("Chunk commun").construis(),
    ]

    client_albert_memoire.avec_les_resultats(resultats_classiques)
    client_albert_memoire.avec_chunks_par_id(chunks_sources_jeopardy)

    configuration = Albert.Service(
        collection_nom_anssi_lab="",
        collection_id_anssi_lab=157814,
        collection_id_anssi_lab_jeopardy=161155,
        reclassement_active=False,
        modele_reclassement="",
        taille_fenetre_historique=2,
        jeopardy_active=True,
        seuil_reponse_maitrisee=0.5,
    )

    service_albert = ServiceAlbert(
        configuration_service_albert=configuration,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
        reformulateur=ReformulateurDeQuestion(client_albert_memoire, "", ""),
        mapping_reponses=MappingReponsesMaitrisees({}),
    )

    paragraphes = service_albert.recherche_paragraphes("Ma question ?")

    contenus = [p.contenu for p in paragraphes]
    assert len(paragraphes) == 3
    assert contenus.count("Chunk commun") == 1


def test_recherche_paragraphes_limite_a_20_candidats():
    client_albert_memoire = ClientAlbertMemoire()

    resultats_classiques = [
        un_resultat_de_recherche()
        .ayant_pour_contenu(f"Chunk classique {i}")
        .construis()
        for i in range(15)
    ]

    resultats_jeopardy = [
        ResultatRechercheJeopardy(
            chunk=RechercheChunkJeopardy(
                content=f"Question {i}",
                metadata=RechercheMetadonneesJeopardy(
                    source_id_document="4065642",
                    source_id_chunk=100 + i,
                    source_numero_page=i,
                ),
            ),
            score=0.8,
        )
        for i in range(15)
    ]
    client_albert_memoire.avec_les_resultats_jeopardy(resultats_jeopardy)

    chunks_sources_jeopardy = [
        un_resultat_de_recherche()
        .ayant_pour_contenu(f"Chunk source jeopardy {i}")
        .construis()
        for i in range(15)
    ]

    client_albert_memoire.avec_les_resultats_par_appel(
        [resultats_classiques, chunks_sources_jeopardy]
    )

    configuration = Albert.Service(
        collection_nom_anssi_lab="",
        collection_id_anssi_lab=157814,
        collection_id_anssi_lab_jeopardy=161155,
        reclassement_active=True,
        modele_reclassement="",
        taille_fenetre_historique=2,
        jeopardy_active=True,
        seuil_reponse_maitrisee=0.5,
    )

    service_albert = ServiceAlbert(
        configuration_service_albert=configuration,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
        reformulateur=ReformulateurDeQuestion(client_albert_memoire, "", ""),
        mapping_reponses=MappingReponsesMaitrisees({}),
    )

    paragraphes = service_albert.recherche_paragraphes("Ma question ?")

    assert len(paragraphes) <= 20
