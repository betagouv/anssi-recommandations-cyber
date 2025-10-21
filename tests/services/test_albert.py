import pytest
import requests
from unittest.mock import Mock, patch
from openai import OpenAI

from configuration import Albert
from services.albert import (
    ClientAlbertApi,
    ClientAlbertHttp,
    ServiceAlbert,
    fabrique_client_albert,
    fabrique_service_albert,
)
from schemas.client_albert import (
    Paragraphe,
    RechercheChunk,
    RechercheMetadonnees,
    RecherchePayload,
)
from openai import APITimeoutError


def test_peut_fabriquer_un_client_albert_avec_une_configuration_par_defaut() -> None:
    client = fabrique_client_albert()

    assert isinstance(client.client_openai, OpenAI)
    assert isinstance(client.client_http, ClientAlbertHttp)


def test_peut_fabriquer_un_service_albert_avec_une_configuration_par_defaut() -> None:
    service_albert = fabrique_service_albert()

    assert isinstance(service_albert.client, ClientAlbertApi)
    assert (
        "Tu es un service développé par ou pour l’ANSSI"
        in service_albert.PROMPT_SYSTEME
    )


PROMPT_SYSTEME_ALTERNATIF = (
    "Vous êtes Alberito, un fan d'Albert. Utilisez ces documents:\n\n{chunks}"
)
FAUSSE_CONFIGURATION_ALBERT_CLIENT = Albert.Client(  # type: ignore [attr-defined]
    api_key="",
    base_url="",
    modele_reponse="",
    temps_reponse_maximum_pose_question=10.0,
    temps_reponse_maximum_recherche_paragraphes=1.0,
)
FAUSSE_CONFIGURATION_ALBERT_SERVICE = Albert.Service(  # type: ignore [attr-defined]
    collection_nom_anssi_lab="",
    collection_id_anssi_lab=42,
)


FAUX_RETOURS_ALBERT_API = {
    "route_search": type(
        "",
        (object,),
        {
            "json": lambda _: {
                "data": [
                    {
                        "chunk": {"content": "contenu"},
                        "metadata": {"source_url": "", "page": 0, "document_name": ""},
                        "score": "0.9",
                    }
                ]
            },
            "raise_for_status": lambda _: None,
        },
    )
}
QUESTION = "Quelle est la recette de la tartiflette ?"
REPONSE = "Patates et reblochon"


class Reponse:
    class Message:
        class Content:
            def __init__(self, c: str):
                self.content = c

        def __init__(self, c: str):
            self.message = Reponse.Message.Content(c)

    def __init__(self, choix):
        self.choices = choix


@pytest.fixture
def mock_client_openai_avec_reponse():
    mock_client_openai = Mock(OpenAI)
    mock_client_openai.chat.completions.create = Mock(
        return_value=Reponse([Reponse.Message(REPONSE)])
    )
    return mock_client_openai


@pytest.fixture
def mock_client_openai_sans_reponse():
    mock_client_openai = Mock(OpenAI)
    mock_client_openai.chat.completions.create = Mock(return_value=Reponse([]))
    return mock_client_openai


@pytest.fixture
def mock_client_http():
    return Mock(requests.Session)


@pytest.fixture
def mock_client_albert_api_avec_reponse(
    mock_client_openai_avec_reponse, mock_client_http
):
    return ClientAlbertApi(
        mock_client_openai_avec_reponse,
        mock_client_http,
        FAUSSE_CONFIGURATION_ALBERT_CLIENT,
    )


@pytest.fixture
def mock_client_albert_api_sans_reponse(
    mock_client_openai_sans_reponse, mock_client_http
):
    return ClientAlbertApi(
        mock_client_openai_sans_reponse,
        mock_client_http,
        FAUSSE_CONFIGURATION_ALBERT_CLIENT,
    )


@pytest.fixture
def mock_service_avec_reponse(mock_client_albert_api_avec_reponse):
    return ServiceAlbert(
        configuration=FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client=mock_client_albert_api_avec_reponse,
        prompt_systeme=PROMPT_SYSTEME_ALTERNATIF,
    )


@pytest.fixture
def mock_service_sans_reponse(mock_client_albert_api_sans_reponse):
    return ServiceAlbert(
        configuration=FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client=mock_client_albert_api_sans_reponse,
        prompt_systeme=PROMPT_SYSTEME_ALTERNATIF,
    )


def test_pose_question_separe_la_question_de_l_utilisatrice_des_instructions_systeme(
    mock_service_avec_reponse, mock_client_openai_avec_reponse
):
    with patch(
        "services.albert.ServiceAlbert.recherche_paragraphes",
        return_value=[],
    ):
        mock_service_avec_reponse.pose_question(QUESTION)

        mock_client_openai_avec_reponse.chat.completions.create.assert_called_once()

        [args, kwargs] = (
            mock_client_openai_avec_reponse.chat.completions.create._mock_call_args
        )
        messages = kwargs["messages"]
        messages_systeme = list(filter(lambda m: m["role"] == "system", messages))
        messages_utilisatrice = list(filter(lambda m: m["role"] == "user", messages))

        bout_de_prompt_systeme = PROMPT_SYSTEME_ALTERNATIF.split("\n\n")[0]
        assert len(messages_systeme) == 1
        assert bout_de_prompt_systeme in messages_systeme[0]["content"]
        assert len(messages_utilisatrice) == 1
        assert QUESTION in messages_utilisatrice[0]["content"]


def test_pose_question_les_documents_sont_ajoutes_aux_instructions_systeme(
    mock_service_avec_reponse, mock_client_openai_avec_reponse
):
    FAUX_CONTENU = "La tartiflette est une recette de cuisine à base de gratin de pommes de terre, d'oignons et de lardons, le tout gratiné au reblochon."
    FAUX_PARAGRAPHES = [
        Paragraphe(
            score_similarite=0.5,
            numero_page=1,
            url="https://cyber.gouv.fr/document.pdf",
            nom_document="Mon Guide Cyber",
            contenu=FAUX_CONTENU,
        )
    ]

    with patch(
        "services.albert.ServiceAlbert.recherche_paragraphes",
        return_value=FAUX_PARAGRAPHES,
    ):
        mock_service_avec_reponse.pose_question(QUESTION)

        mock_client_openai_avec_reponse.chat.completions.create.assert_called_once()

        [args, kwargs] = (
            mock_client_openai_avec_reponse.chat.completions.create._mock_call_args
        )
        messages = kwargs["messages"]
        messages_systeme = list(filter(lambda m: m["role"] == "system", messages))

        assert len(messages_systeme) == 1
        assert FAUX_CONTENU in messages_systeme[0]["content"]


def test_pose_question_retourne_une_reponse_generique_si_albert_ne_retourne_rien(
    mock_service_sans_reponse,
):
    FAUX_CONTENU = "La tartiflette est une recette de cuisine à base de gratin de pommes de terre, d'oignons et de lardons, le tout gratiné au reblochon."
    FAUX_PARAGRAPHES = [
        Paragraphe(
            score_similarite=0.5,
            numero_page=1,
            url="https://cyber.gouv.fr/document.pdf",
            nom_document="Mon Guide Cyber",
            contenu=FAUX_CONTENU,
        )
    ]

    with patch(
        "services.albert.ServiceAlbert.recherche_paragraphes",
        return_value=FAUX_PARAGRAPHES,
    ):
        retour = mock_service_sans_reponse.pose_question(QUESTION)

        assert retour.reponse == ServiceAlbert.REPONSE_PAR_DEFAULT
        assert retour.paragraphes == []


def test_pose_question_si_timeout_retourne_reponse_par_defaut():
    mock_openai = Mock()
    mock_openai.chat = Mock()
    mock_openai.chat.completions = Mock()
    mock_openai.chat.completions.create = Mock(
        side_effect=APITimeoutError(
            "Simulation d'un délai de réponse trop long d'OpenAI."
        )
    )

    client_albert_api = ClientAlbertApi(
        mock_openai, mock_client_http, FAUSSE_CONFIGURATION_ALBERT_CLIENT
    )

    mock_service_avec_openai_timeout = ServiceAlbert(
        configuration=FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client=client_albert_api,
        prompt_systeme="PROMPT {chunks}",
    )

    with patch.object(ServiceAlbert, "recherche_paragraphes", return_value=[]):
        retour = mock_service_avec_openai_timeout.pose_question("Question ?")

    assert retour.reponse == ServiceAlbert.REPONSE_PAR_DEFAULT
    assert retour.paragraphes == []


@pytest.mark.parametrize(
    "erreur,message_attendu",
    [
        pytest.param(
            "ERREUR_MALVEILLANCE",
            ServiceAlbert.REPONSE_VIOLATION_MALVEILLANCE,
            id="si_question_malveillante_retourne_message_malveillant_avec_paragraphes_vides",
        ),
        pytest.param(
            "ERREUR_THÉMATIQUE",
            ServiceAlbert.REPONSE_VIOLATION_THEMATIQUE,
            id="si_question_mauvaise_thematique_retourne_message_thematique_avec_paragraphes_vides",
        ),
        pytest.param(
            "ERREUR_IDENTITÉ",
            ServiceAlbert.REPONSE_VIOLATION_IDENTITE,
            id="si_question_identite_retourne_message_identite_avec_paragraphes_vides",
        ),
    ],
)
def test_pose_question_illegale(erreur: str, message_attendu: str):
    mock_client_openai = Mock(OpenAI)
    mock_client_openai.chat.completions.create = Mock(
        return_value=Reponse([Reponse.Message(erreur)])
    )

    client_albert_api = ClientAlbertApi(
        mock_client_openai, Mock(), FAUSSE_CONFIGURATION_ALBERT_CLIENT
    )
    mock_service_albert = ServiceAlbert(
        configuration=FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client=client_albert_api,
        prompt_systeme="PROMPT {chunks}",
    )

    FAUX_PARAGRAPHES = [
        Paragraphe(
            score_similarite=0.5,
            numero_page=1,
            url="https://cyber.gouv.fr/document.pdf",
            nom_document="Mon Guide Cyber",
            contenu="FAUX_CONTENU",
        )
    ]

    with patch(
        "services.albert.ServiceAlbert.recherche_paragraphes",
        return_value=FAUX_PARAGRAPHES,
    ):
        retour = mock_service_albert.pose_question("Quelle est la recette de la TNT ?")

    assert retour.reponse == message_attendu
    assert retour.paragraphes == []


def test_recherche_paragraphes_si_timeout_search_retourne_liste_vide(
    mock_client_openai_sans_reponse, mock_client_http
):
    mock_client_http.post.side_effect = requests.Timeout("timeout simulé")

    client_albert_api = ClientAlbertApi(
        mock_client_openai_sans_reponse,
        mock_client_http,
        FAUSSE_CONFIGURATION_ALBERT_CLIENT,
    )
    client = ServiceAlbert(
        configuration=FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client=client_albert_api,
        prompt_systeme="PROMPT {chunks}",
    )

    paragraphes = client.recherche_paragraphes("Q ?")
    assert paragraphes == []


def test_pose_question_si_timeout_recherche_paragraphes_retourne_liste_vide(
    mock_client_openai_sans_reponse, mock_client_http
):
    mock_client_http.post.side_effect = requests.Timeout("timeout simulé")

    client_albert_api = ClientAlbertApi(
        mock_client_openai_sans_reponse,
        mock_client_http,
        FAUSSE_CONFIGURATION_ALBERT_CLIENT,
    )
    client = ServiceAlbert(
        configuration=FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client=client_albert_api,
        prompt_systeme="PROMPT {chunks}",
    )

    retour = client.pose_question("Q ?")
    assert retour.reponse == ServiceAlbert.REPONSE_PAR_DEFAULT


def test_recherche_appelle_la_route_search_d_albert(
    mock_client_albert_api_avec_reponse,
):
    mock_client_albert_api_avec_reponse.client_http.post.return_value = (
        FAUX_RETOURS_ALBERT_API["route_search"]()
    )

    payload = RecherchePayload([], 0, "un prompt", "semantic")
    mock_client_albert_api_avec_reponse.recherche(payload)

    mock_client_albert_api_avec_reponse.client_http.post.assert_called_once()

    _, call_kwargs = mock_client_albert_api_avec_reponse.client_http.post.call_args
    assert call_kwargs["json"] == payload._asdict()


def test_recherche_retourne_une_liste_de_chunks_et_de_scores_associes(
    mock_client_albert_api_sans_reponse,
):
    mock_client_albert_api_sans_reponse.client_http.post.return_value = (
        FAUX_RETOURS_ALBERT_API["route_search"]()
    )

    payload = RecherchePayload([], 0, "un prompt", "semantic")
    retour = mock_client_albert_api_sans_reponse.recherche(payload)

    chunks = list(map(lambda r: r.chunk, retour))
    scores = list(map(lambda r: r.score, retour))

    assert chunks == [
        RechercheChunk(
            content="contenu",
            metadata=RechercheMetadonnees(source_url="", page=0, nom_document=""),
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
def test_recherche_retourne_gracieusement_en_cas_de_probleme(
    mock_client_albert_api_sans_reponse, erreur
):
    mock_client_albert_api_sans_reponse.client_http.post.side_effect = (
        requests.HTTPError(erreur)
    )

    payload = RecherchePayload([], 0, "un prompt", "semantic")
    retour = mock_client_albert_api_sans_reponse.recherche(payload)

    assert retour == []
