import pytest
from client_albert_de_test import (
    ConstructeurServiceAlbert,
    ConstructeurClientOpenai,
    ConstructeurClientHttp,
    ConstructeurRetourRouteSearch,
)
from infra.albert.client_albert import ClientAlbertApi
from schemas.albert import RecherchePayload, RechercheChunk, RechercheMetadonnees

REPONSE = "Patates et reblochon"
FAUX_RETOURS_ALBERT_API = (
    ConstructeurRetourRouteSearch().avec_contenu("contenu").construis()
)


def test_recupere_propositions():
    mock_client_http = (
        ConstructeurClientHttp()
        .qui_retourne(ConstructeurRetourRouteSearch().construis())
        .construis()
    )
    mock_client_openai_avec_reponse = (
        ConstructeurClientOpenai().qui_complete_avec(REPONSE).construis()
    )
    mock_service_avec_reponse = ClientAlbertApi(
        mock_client_openai_avec_reponse,
        mock_client_http,
        ConstructeurServiceAlbert.FAUSSE_CONFIGURATION_ALBERT_CLIENT,
    )

    propositions = mock_service_avec_reponse.recupere_propositions([])

    mock_service_avec_reponse.client_openai.chat.completions.create.assert_called_once()
    assert propositions[0].message.content == REPONSE


def test_recupere_propositions_si_timeout_retourne_un_resultat_vide():
    mock_client_http = (
        ConstructeurClientHttp()
        .qui_retourne(ConstructeurRetourRouteSearch().construis())
        .construis()
    )
    mock_client_openai = ConstructeurClientOpenai().qui_timeout().construis()

    mock_service_avec_reponse = ClientAlbertApi(
        mock_client_openai,
        mock_client_http,
        ConstructeurServiceAlbert.FAUSSE_CONFIGURATION_ALBERT_CLIENT,
    )

    retour = mock_service_avec_reponse.recupere_propositions([])

    assert len(retour) == 0


def test_recherche_si_timeout_retourne_un_resultat_vide():
    payload = RecherchePayload(
        collections=[1],
        k=5,
        prompt="Question ?",
        method="methode",
    )
    mock_client_http = ConstructeurClientHttp().qui_timeout().construis()
    mock_client_openai = ConstructeurClientOpenai().qui_ne_complete_pas().construis()

    mock_service_avec_reponse = ClientAlbertApi(
        mock_client_openai,
        mock_client_http,
        ConstructeurServiceAlbert.FAUSSE_CONFIGURATION_ALBERT_CLIENT,
    )

    retour = mock_service_avec_reponse.recherche(payload)

    assert retour == []


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
