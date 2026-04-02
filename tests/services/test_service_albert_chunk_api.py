from client_albert_de_test import (
    ClientAlbertMemoire,
    un_resultat_de_recherche,
)
from schemas.albert import (
    RechercheMetadonneesJeopardy,
    RechercheChunkJeopardy,
    ResultatRechercheJeopardy,
)
from configuration import Albert
from services.service_albert import ServiceAlbert, Prompts


def test_recherche_chunk_par_id_utilise_api_documents():
    client_albert_memoire = ClientAlbertMemoire()

    chunk_source = (
        un_resultat_de_recherche().ayant_pour_contenu("Contenu du chunk 73").construis()
    )
    client_albert_memoire.avec_chunk_par_id(chunk_source)

    resultat = client_albert_memoire.recherche_chunk_par_id(
        document_id="4065642", chunk_id=73
    )

    assert resultat.chunk.content == "Contenu du chunk 73"
    assert client_albert_memoire.document_id_recu == "4065642"
    assert client_albert_memoire.chunk_id_recu == 73


def test_recherche_jeopardy_utilise_recherche_chunk_par_id():
    client_albert_memoire = ClientAlbertMemoire()
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
    chunks_sources = [
        un_resultat_de_recherche()
        .ayant_pour_contenu("Contenu du chunk 73")
        .construis(),
        un_resultat_de_recherche()
        .ayant_pour_contenu("Contenu du chunk 74")
        .construis(),
    ]
    client_albert_memoire.avec_chunks_par_id(chunks_sources)
    PROMPTS = Prompts(
        prompt_systeme="Prompt système",
        prompt_reclassement="Prompt reclassement",
    )
    configuration = Albert.Service(
        collection_nom_anssi_lab="",
        collection_id_anssi_lab=157814,
        collection_id_anssi_lab_jeopardy=161155,
        reclassement_active=False,
        modele_reclassement="",
        taille_fenetre_historique=2,
        reformulateur_active=False,
        jeopardy_active=False,
    )
    service_albert = ServiceAlbert(
        configuration_service_albert=configuration,
        client=client_albert_memoire,
        utilise_recherche_hybride=False,
        prompts=PROMPTS,
    )
    paragraphes = service_albert._ServiceAlbert__recherche_dans_collection_jeopardy(
        "Ma question ?"
    )

    assert len(paragraphes) == 2
    assert paragraphes[0].contenu == "Contenu du chunk 73"
    assert paragraphes[1].contenu == "Contenu du chunk 74"
    assert len(client_albert_memoire.appels_recherche_chunk_par_id) == 2
    assert client_albert_memoire.appels_recherche_chunk_par_id[0] == ("4065642", 73)
    assert client_albert_memoire.appels_recherche_chunk_par_id[1] == ("4065642", 74)
