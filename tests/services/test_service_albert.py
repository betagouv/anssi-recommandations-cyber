import pytest
from client_albert_de_test import (
    ConstructeurClientHttp,
    ConstructeurClientOpenai,
    ConstructeurRetourRouteSearch,
    ConstructeurServiceAlbert,
)
from infra.albert.client_albert import (
    ClientAlbertApi,
)
from schemas.albert import (
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

FAUX_RETOURS_ALBERT_API = (
    ConstructeurRetourRouteSearch().avec_contenu("contenu").construis()
)
QUESTION = "Quelle est la recette de la tartiflette ?"
REPONSE = "Patates et reblochon"


def test_pose_question_separe_la_question_de_l_utilisatrice_des_instructions_systeme():
    mock_client_http = (
        ConstructeurClientHttp()
        .qui_retourne(ConstructeurRetourRouteSearch().construis())
        .construis()
    )
    mock_client_openai_avec_reponse = (
        ConstructeurClientOpenai().qui_complete_avec(REPONSE).construis()
    )
    mock_service_avec_reponse = (
        ConstructeurServiceAlbert()
        .avec_client_http(mock_client_http)
        .avec_client_openai(mock_client_openai_avec_reponse)
        .construis()
    )

    mock_service_avec_reponse.pose_question(QUESTION)

    mock_service_avec_reponse.client.client_openai.chat.completions.create.assert_called_once()

    [args, kwargs] = (
        mock_service_avec_reponse.client.client_openai.chat.completions.create._mock_call_args
    )
    messages = kwargs["messages"]
    messages_systeme = list(filter(lambda m: m["role"] == "system", messages))
    messages_utilisatrice = list(filter(lambda m: m["role"] == "user", messages))

    bout_de_prompt_systeme = ConstructeurServiceAlbert.PROMPT_SYSTEME_ALTERNATIF.split(
        "\n\n"
    )[0]
    assert len(messages_systeme) == 1
    assert bout_de_prompt_systeme in messages_systeme[0]["content"]
    assert len(messages_utilisatrice) == 1
    assert QUESTION in messages_utilisatrice[0]["content"]


def test_pose_question_les_documents_sont_ajoutes_aux_instructions_systeme():
    FAUX_CONTENU = "La tartiflette est une recette de cuisine à base de gratin de pommes de terre, d'oignons et de lardons, le tout gratiné au reblochon."

    mock_client_http = (
        ConstructeurClientHttp()
        .qui_retourne(
            ConstructeurRetourRouteSearch().avec_contenu(FAUX_CONTENU).construis()
        )
        .construis()
    )
    mock_client_openai_avec_reponse = (
        ConstructeurClientOpenai().qui_complete_avec(REPONSE).construis()
    )
    mock_service_avec_reponse = (
        ConstructeurServiceAlbert()
        .avec_client_http(mock_client_http)
        .avec_client_openai(mock_client_openai_avec_reponse)
        .construis()
    )

    mock_service_avec_reponse.pose_question(QUESTION)

    mock_service_avec_reponse.client.client_openai.chat.completions.create.assert_called_once()

    [args, kwargs] = (
        mock_service_avec_reponse.client.client_openai.chat.completions.create._mock_call_args
    )
    messages = kwargs["messages"]
    messages_systeme = list(filter(lambda m: m["role"] == "system", messages))

    assert len(messages_systeme) == 1
    assert FAUX_CONTENU in messages_systeme[0]["content"]


def test_pose_question_retourne_une_reponse_generique_et_pas_de_violation_si_albert_ne_retourne_rien():
    FAUX_CONTENU = "La tartiflette est une recette de cuisine à base de gratin de pommes de terre, d'oignons et de lardons, le tout gratiné au reblochon."

    mock_client_http = (
        ConstructeurClientHttp()
        .qui_retourne(
            ConstructeurRetourRouteSearch().avec_contenu(FAUX_CONTENU).construis()
        )
        .construis()
    )
    mock_client_openai_sans_reponse = (
        ConstructeurClientOpenai().qui_ne_complete_pas().construis()
    )
    mock_service_sans_reponse = (
        ConstructeurServiceAlbert()
        .avec_client_http(mock_client_http)
        .avec_client_openai(mock_client_openai_sans_reponse)
        .construis()
    )

    retour = mock_service_sans_reponse.pose_question(QUESTION)

    assert retour.reponse == REPONSE_PAR_DEFAUT
    assert retour.paragraphes == []
    assert retour.violation is None


def test_pose_question_si_timeout_retourne_reponse_par_defaut_et_aucune_violation():
    mock_client_http = (
        ConstructeurClientHttp()
        .qui_retourne(ConstructeurRetourRouteSearch().construis())
        .construis()
    )
    mock_client_openai = ConstructeurClientOpenai().qui_timeout().construis()

    mock_service_avec_openai_timeout = (
        ConstructeurServiceAlbert()
        .avec_client_http(mock_client_http)
        .avec_client_openai(mock_client_openai)
        .construis()
    )

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
    mock_client_http = (
        ConstructeurClientHttp().qui_retourne(FAUX_RETOURS_ALBERT_API).construis()
    )
    mock_client_openai = (
        ConstructeurClientOpenai().qui_complete_avec(erreur).construis()
    )

    mock_service_albert = (
        ConstructeurServiceAlbert()
        .avec_client_http(mock_client_http)
        .avec_client_openai(mock_client_openai)
        .construis()
    )

    retour = mock_service_albert.pose_question("question illégale ?")

    assert retour.reponse == violation_attendue.reponse
    assert retour.paragraphes == []
    assert retour.violation == violation_attendue


def test_recherche_paragraphes_si_timeout_search_retourne_liste_vide():
    mock_client_openai_sans_reponse = (
        ConstructeurClientOpenai().qui_ne_complete_pas().construis()
    )
    mock_client_http = ConstructeurClientHttp().qui_timeout().construis()

    client = (
        ConstructeurServiceAlbert()
        .avec_client_http(mock_client_http)
        .avec_client_openai(mock_client_openai_sans_reponse)
        .construis()
    )

    paragraphes = client.recherche_paragraphes("Q ?")
    assert paragraphes == []


def test_pose_question_si_timeout_recherche_paragraphes_retourne_liste_vide():
    mock_client_openai_sans_reponse = (
        ConstructeurClientOpenai().qui_ne_complete_pas().construis()
    )
    mock_client_http = ConstructeurClientHttp().qui_timeout().construis()

    client = (
        ConstructeurServiceAlbert()
        .avec_client_http(mock_client_http)
        .avec_client_openai(mock_client_openai_sans_reponse)
        .construis()
    )

    retour = client.pose_question("Q ?")
    assert retour.reponse == REPONSE_PAR_DEFAUT


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
