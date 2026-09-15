from client_albert_de_test import (
    ConstructeurClientHttp,
    ConstructeurClientOpenai,
    RetourHttpJson,
)

from infra.albert.client_albert import ClientAlbertApi
from schemas.albert import RechercheChunk, RechercheMetadonnees, RecherchePayload


def test_recupere_les_chunks_d_un_document_avec_leurs_metadonnees(
    une_configuration_albert_client,
):
    retour = RetourHttpJson(
        {
            "data": [
                {
                    "content": "Contenu de la page 3",
                    "metadata": {
                        "source_url": "https://exemple.fr/document.pdf",
                        "nom_document": "document.pdf",
                        "page": 3,
                        "position_page": 0,
                    },
                }
            ]
        }
    )
    client_http = ConstructeurClientHttp().construis()
    client_http.get.side_effect = [RetourHttpJson({"chunks": 1}), retour]
    client_albert = ClientAlbertApi(
        ConstructeurClientOpenai().qui_ne_complete_pas().construis(),
        client_http,
        une_configuration_albert_client,
    )

    chunks = client_albert.recupere_chunks_document(4777455)

    assert chunks == [
        RechercheChunk(
            content="Contenu de la page 3",
            metadata=RechercheMetadonnees(
                source_url="https://exemple.fr/document.pdf",
                nom_document="document.pdf",
                page=3,
                position_page=0,
            ),
        )
    ]
    client_http.get.assert_called_with(
        "/documents/4777455/chunks",
        params={"limit": 100, "offset": 0},
        timeout=1.0,
    )


def test_recupere_toutes_les_pages_de_chunks_d_un_document(
    une_configuration_albert_client,
):
    retour_document = RetourHttpJson({"chunks": 101})
    premier_retour = RetourHttpJson(
        {
            "data": [
                {"content": f"Contenu {index}", "metadata": {"page": 1}}
                for index in range(100)
            ]
        }
    )
    dernier_retour = RetourHttpJson(
        {"data": [{"content": "Contenu 100", "metadata": {"page": 2}}]}
    )
    client_http = ConstructeurClientHttp().construis()
    client_http.get.side_effect = [retour_document, premier_retour, dernier_retour]
    client_albert = ClientAlbertApi(
        ConstructeurClientOpenai().qui_ne_complete_pas().construis(),
        client_http,
        une_configuration_albert_client,
    )

    chunks = client_albert.recupere_chunks_document(4777455)

    assert len(chunks) == 101
    assert client_http.get.call_args_list[0].args[0] == "/documents/4777455"
    assert len(client_http.get.call_args_list) == 3
    assert client_http.get.call_args_list[1].kwargs["params"] == {
        "limit": 100,
        "offset": 0,
    }
    assert client_http.get.call_args_list[2].kwargs["params"] == {
        "limit": 100,
        "offset": 100,
    }


def test_recherche_propage_l_identifiant_du_document_du_chunk(
    une_configuration_albert_client,
):
    retour = RetourHttpJson(
        {
            "data": [
                {
                    "chunk": {
                        "document_id": 4777455,
                        "content": "Contenu source",
                        "metadata": {"page": 3},
                    },
                    "score": 0.9,
                }
            ]
        }
    )
    client_albert = ClientAlbertApi(
        ConstructeurClientOpenai().qui_ne_complete_pas().construis(),
        ConstructeurClientHttp().qui_retourne(retour).construis(),
        une_configuration_albert_client,
    )

    resultat = client_albert.recherche(
        RecherchePayload([1], 1, "Une question", "semantic")
    )

    assert resultat[0].chunk.metadata.identifiant_document == 4777455


def test_recupere_les_metadonnees_de_bloc_des_chunks_d_un_document(
    une_configuration_albert_client,
):
    retour = RetourHttpJson(
        {
            "data": [
                {
                    "document_id": 4777455,
                    "content": "Contenu source",
                    "metadata": {
                        "source_url": "https://exemple.fr/document.pdf",
                        "nom_document": "document.pdf",
                        "page": 3,
                        "type_de_bloc": "paragraphe",
                        "code_recommandation": "R3",
                        "chemin_sections": '["Chapitre", "Section"]',
                        "position_page": 0,
                        "derniere_page": 14,
                    },
                }
            ]
        }
    )
    client_http = ConstructeurClientHttp().construis()
    client_http.get.side_effect = [RetourHttpJson({"chunks": 1}), retour]
    client_albert = ClientAlbertApi(
        ConstructeurClientOpenai().qui_ne_complete_pas().construis(),
        client_http,
        une_configuration_albert_client,
    )

    metadata = client_albert.recupere_chunks_document(4777455)[0].metadata

    assert metadata.type_de_bloc == "paragraphe"
    assert metadata.code_recommandation == "R3"
    assert metadata.chemin_sections == ["Chapitre", "Section"]
    assert metadata.derniere_page == 14


def test_recupere_un_chunk_sans_metadonnees_avec_des_valeurs_par_defaut(
    une_configuration_albert_client,
):
    retour = RetourHttpJson({"data": [{"content": "Contenu", "metadata": None}]})
    client_http = ConstructeurClientHttp().construis()
    client_http.get.side_effect = [RetourHttpJson({"chunks": 1}), retour]
    client_albert = ClientAlbertApi(
        ConstructeurClientOpenai().qui_ne_complete_pas().construis(),
        client_http,
        une_configuration_albert_client,
    )

    metadata = client_albert.recupere_chunks_document(4777455)[0].metadata

    assert metadata.page == 0
