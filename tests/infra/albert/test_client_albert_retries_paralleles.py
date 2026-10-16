from typing import cast

import requests
from openai import OpenAI
from openai.types.chat.completion_create_params import ResponseFormat

from infra.albert.client_albert import fabrique_client_albert
from infra.albert.client_albert import ClientAlbertApi


class CompletionAlbertEnMemoire:
    def __init__(self) -> None:
        self.parametres_recus: dict[str, object] | None = None
        self.chat = self
        self.completions = self

    def create(self, **parametres):
        self.parametres_recus = parametres
        return type("Reponse", (), {"choices": [], "usage": None})()


class SessionAlbertEnMemoire:
    pass


def test_le_mode_parallele_desactive_les_reprises_sans_changer_le_timeout_sdk(
    une_configuration_albert_client,
) -> None:
    client_historique = fabrique_client_albert(une_configuration_albert_client)
    client_parallele = fabrique_client_albert(
        une_configuration_albert_client, max_retries=0
    )
    try:
        assert client_historique.client_openai.max_retries == 2
        assert client_parallele.client_openai.max_retries == 0
        assert (
            client_historique.client_openai.timeout
            == une_configuration_albert_client.temps_reponse_maximum_pose_question
        )
        assert (
            client_parallele.client_openai.timeout
            == une_configuration_albert_client.temps_reponse_maximum_pose_question
        )
    finally:
        client_historique.client_openai.close()
        client_historique.client_http.close()
        client_parallele.client_openai.close()
        client_parallele.client_http.close()


def test_transmet_le_format_de_reponse_demande_a_albert(
    une_configuration_albert_client,
) -> None:
    completion = CompletionAlbertEnMemoire()
    client = ClientAlbertApi(
        cast(OpenAI, completion),
        cast(requests.Session, SessionAlbertEnMemoire()),
        une_configuration_albert_client,
    )
    format_reponse = cast(
        ResponseFormat, {"type": "json_schema", "json_schema": {"name": "rangs"}}
    )

    client.recupere_propositions([], format_reponse=format_reponse)

    assert completion.parametres_recus is not None
    assert completion.parametres_recus["response_format"] == format_reponse
