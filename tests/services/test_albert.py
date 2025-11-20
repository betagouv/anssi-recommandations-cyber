import pytest
from unittest.mock import patch
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
from schemas.violations import (
    REPONSE_PAR_DEFAUT,
    Violation,
    ViolationIdentite,
    ViolationMalveillance,
    ViolationThematique,
)

from client_albert_de_test import (
    ConstructeurClientHttp,
    ConstructeurClientOpenai,
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


def test_peut_fabriquer_un_client_albert_avec_une_configuration_par_defaut() -> None:
    client = fabrique_client_albert(FAUSSE_CONFIGURATION_ALBERT_CLIENT)

    assert isinstance(client.client_openai, OpenAI)
    assert isinstance(client.client_http, ClientAlbertHttp)


def test_peut_fabriquer_un_service_albert_avec_une_configuration_par_defaut() -> None:
    service_albert = fabrique_service_albert()

    assert isinstance(service_albert.client, ClientAlbertApi)
    assert (
        "Tu es un service développé par ou pour l’ANSSI"
        in service_albert.PROMPT_SYSTEME
    )


@pytest.fixture
def mock_client_albert_api_avec_reponse():
    mock_client_http = ConstructeurClientHttp().construis()
    mock_client_openai_avec_reponse = (
        ConstructeurClientOpenai().qui_complete_avec(REPONSE).construis()
    )

    return ClientAlbertApi(
        mock_client_openai_avec_reponse,
        mock_client_http,
        FAUSSE_CONFIGURATION_ALBERT_CLIENT,
    )


@pytest.fixture
def mock_client_albert_api_sans_reponse():
    mock_client_http = ConstructeurClientHttp().construis()
    mock_client_openai_sans_reponse = (
        ConstructeurClientOpenai().qui_ne_complete_pas().construis()
    )

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
    mock_service_avec_reponse,
):
    with patch(
        "services.albert.ServiceAlbert.recherche_paragraphes",
        return_value=[],
    ):
        mock_service_avec_reponse.pose_question(QUESTION)

        mock_service_avec_reponse.client.client_openai.chat.completions.create.assert_called_once()

        [args, kwargs] = (
            mock_service_avec_reponse.client.client_openai.chat.completions.create._mock_call_args
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
    mock_service_avec_reponse,
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

        mock_service_avec_reponse.client.client_openai.chat.completions.create.assert_called_once()

        [args, kwargs] = (
            mock_service_avec_reponse.client.client_openai.chat.completions.create._mock_call_args
        )
        messages = kwargs["messages"]
        messages_systeme = list(filter(lambda m: m["role"] == "system", messages))

        assert len(messages_systeme) == 1
        assert FAUX_CONTENU in messages_systeme[0]["content"]


def test_pose_question_retourne_une_reponse_generique_et_pas_de_violation_si_albert_ne_retourne_rien(
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

        assert retour.reponse == REPONSE_PAR_DEFAUT
        assert retour.paragraphes == []
        assert retour.violation is None


def test_pose_question_si_timeout_retourne_reponse_par_defaut_et_aucune_violation():
    mock_client_http = ConstructeurClientHttp().construis()
    mock_client_openai = ConstructeurClientOpenai().qui_timeout().construis()

    client_albert_api = ClientAlbertApi(
        mock_client_openai, mock_client_http, FAUSSE_CONFIGURATION_ALBERT_CLIENT
    )

    mock_service_avec_openai_timeout = ServiceAlbert(
        configuration=FAUSSE_CONFIGURATION_ALBERT_SERVICE,
        client=client_albert_api,
        prompt_systeme="PROMPT {chunks}",
    )

    with patch.object(ServiceAlbert, "recherche_paragraphes", return_value=[]):
        retour = mock_service_avec_openai_timeout.pose_question("Question ?")

    assert retour.reponse == REPONSE_PAR_DEFAUT
    assert retour.paragraphes == []
    assert retour.violation is None


@pytest.mark.parametrize(
    "erreur,violation_attendue",
    [
        pytest.param(
            "ERREUR_MALVEILLANCE",
            ViolationMalveillance(),
            id="si_question_malveillante_retourne_message_malveillant_avec_paragraphes_vides",
        ),
        pytest.param(
            "ERREUR_THÉMATIQUE",
            ViolationThematique(),
            id="si_question_mauvaise_thematique_retourne_message_thematique_avec_paragraphes_vides",
        ),
        pytest.param(
            "ERREUR_IDENTITÉ",
            ViolationIdentite(),
            id="si_question_identite_retourne_message_identite_avec_paragraphes_vides",
        ),
    ],
)
def test_pose_question_illegale(erreur: str, violation_attendue: Violation):
    mock_client_http = ConstructeurClientHttp().construis()
    mock_client_openai = ConstructeurClientOpenai().qui_complete_avec(erreur).construis()

    client_albert_api = ClientAlbertApi(
        mock_client_openai, mock_client_http, FAUSSE_CONFIGURATION_ALBERT_CLIENT
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
        retour = mock_service_albert.pose_question("question illégale ?")

    assert retour.reponse == violation_attendue.reponse
    assert retour.paragraphes == []
    assert retour.violation == violation_attendue


def test_recherche_paragraphes_si_timeout_search_retourne_liste_vide():
    mock_client_openai_sans_reponse = (
        ConstructeurClientOpenai().qui_ne_complete_pas().construis()
    )
    mock_client_http = ConstructeurClientHttp().qui_timeout().construis()

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


def test_pose_question_si_timeout_recherche_paragraphes_retourne_liste_vide():
    mock_client_openai_sans_reponse = (
        ConstructeurClientOpenai().qui_ne_complete_pas().construis()
    )
    mock_client_http = ConstructeurClientHttp().qui_timeout().construis()

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
    assert retour.reponse == REPONSE_PAR_DEFAUT


def test_recherche_appelle_la_route_search_d_albert():
    mock_client_http = (
        ConstructeurClientHttp()
        .qui_retourne(FAUX_RETOURS_ALBERT_API["route_search"]())
        .construis()
    )
    mock_client_openai_sans_reponse = (
        ConstructeurClientOpenai().qui_ne_complete_pas().construis()
    )

    mock_client_albert_api = ClientAlbertApi(
        mock_client_openai_sans_reponse,
        mock_client_http,
        FAUSSE_CONFIGURATION_ALBERT_CLIENT,
    )

    payload = RecherchePayload([], 0, "un prompt", "semantic")
    mock_client_albert_api.recherche(payload)

    mock_client_albert_api.client_http.post.assert_called_once()

    _, call_kwargs = mock_client_albert_api.client_http.post.call_args
    assert call_kwargs["json"] == payload._asdict()


def test_recherche_retourne_une_liste_de_chunks_et_de_scores_associes():
    mock_client_http = (
        ConstructeurClientHttp()
        .qui_retourne(FAUX_RETOURS_ALBERT_API["route_search"]())
        .construis()
    )
    mock_client_openai_sans_reponse = (
        ConstructeurClientOpenai().qui_ne_complete_pas().construis()
    )

    mock_client_albert_api = ClientAlbertApi(
        mock_client_openai_sans_reponse,
        mock_client_http,
        FAUSSE_CONFIGURATION_ALBERT_CLIENT,
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
        FAUSSE_CONFIGURATION_ALBERT_CLIENT,
    )

    payload = RecherchePayload([], 0, "un prompt", "semantic")
    retour = mock_client_albert_api.recherche(payload)

    assert retour == []
