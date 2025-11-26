import pytest
from openai import OpenAI

from clients.albert import (
    ClientAlbertApi,
    ClientAlbertHttp,
    fabrique_client_albert,
)
from schemas.client_albert import (
    RechercheChunk,
    RechercheMetadonnees,
    RecherchePayload,
)

from client_albert_de_test import (
    ConstructeurClientHttp,
    ConstructeurClientOpenai,
    ConstructeurServiceAlbert,
    FAUX_RETOURS_ALBERT_API,
)


def test_peut_fabriquer_un_client_albert_avec_une_configuration_par_defaut() -> None:
    client = fabrique_client_albert(
        ConstructeurServiceAlbert.FAUSSE_CONFIGURATION_ALBERT_CLIENT
    )

    assert isinstance(client.client_openai, OpenAI)
    assert isinstance(client.client_http, ClientAlbertHttp)


def test_recherche_appelle_la_route_search_d_albert():
    mock_client_http = (
        ConstructeurClientHttp().qui_retourne(FAUX_RETOURS_ALBERT_API).construis()
    )
    mock_client_openai_sans_reponse = (
        ConstructeurClientOpenai().qui_ne_complete_pas().construis()
    )

    mock_client_albert_api = ClientAlbertApi(
        mock_client_openai_sans_reponse,
        mock_client_http,
        ConstructeurServiceAlbert.FAUSSE_CONFIGURATION_ALBERT_CLIENT,
    )

    payload = RecherchePayload([], 0, "un prompt", "semantic")
    mock_client_albert_api.recherche(payload)

    mock_client_albert_api.client_http.post.assert_called_once()

    _, call_kwargs = mock_client_albert_api.client_http.post.call_args
    assert call_kwargs["json"] == payload._asdict()


def test_recherche_retourne_une_liste_de_chunks_et_de_scores_associes():
    mock_client_http = (
        ConstructeurClientHttp().qui_retourne(FAUX_RETOURS_ALBERT_API).construis()
    )
    mock_client_openai_sans_reponse = (
        ConstructeurClientOpenai().qui_ne_complete_pas().construis()
    )

    mock_client_albert_api = ClientAlbertApi(
        mock_client_openai_sans_reponse,
        mock_client_http,
        ConstructeurServiceAlbert.FAUSSE_CONFIGURATION_ALBERT_CLIENT,
    )

    payload = RecherchePayload([], 0, "un prompt", "semantic")
    retour = mock_client_albert_api.recherche(payload)

    chunks = list(map(lambda r: r.chunk, retour))
    scores = list(map(lambda r: r.score, retour))

    assert chunks == [
        RechercheChunk(
            content="contenu",
            metadata=RechercheMetadonnees(source_url="", page=1, nom_document=""),
        )
    ]
    assert scores == [0.9]


@pytest.mark.parametrize(
    "erreur",
    [
        pytest.param(
            "404 Client Error: Not Found for url: https://albert.api.etalab.gouv.fr/v1/search",
            id="si_api_retourne_404",
        ),
        pytest.param(
            "500 Server Error: Internal Server Error for url: http://albert.api.etalab.gouv.fr/v1/search",
            id="si_api_retourne_500",
        ),
    ],
)
def test_recherche_retourne_gracieusement_en_cas_de_probleme(erreur):
    mock_client_http = (
        ConstructeurClientHttp().qui_retourne_une_erreur(erreur).construis()
    )
    mock_client_openai_sans_reponse = (
        ConstructeurClientOpenai().qui_ne_complete_pas().construis()
    )

    mock_client_albert_api = ClientAlbertApi(
        mock_client_openai_sans_reponse,
        mock_client_http,
        ConstructeurServiceAlbert.FAUSSE_CONFIGURATION_ALBERT_CLIENT,
    )

    payload = RecherchePayload([], 0, "un prompt", "semantic")
    retour = mock_client_albert_api.recherche(payload)

    assert retour == []
