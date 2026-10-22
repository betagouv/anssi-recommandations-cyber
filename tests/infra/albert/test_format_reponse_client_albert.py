from typing import cast

import requests
from openai import OpenAI
from openai.types.chat.completion_create_params import ResponseFormat

from infra.albert.client_albert import ClientAlbertApi


class CompletionAlbertEnMemoire:
    def __init__(self) -> None:
        self.parametres_recus: dict[str, object] = {}
        self.chat = self
        self.completions = self

    def create(self, **parametres):
        self.parametres_recus = parametres
        return type("Reponse", (), {"choices": [], "usage": None})()


def test_transmet_le_format_de_reponse_demande_a_albert(
    une_configuration_albert_client,
) -> None:
    completion = CompletionAlbertEnMemoire()
    client = ClientAlbertApi(
        cast(OpenAI, completion),
        cast(requests.Session, None),
        une_configuration_albert_client,
    )
    format_reponse = cast(
        ResponseFormat, {"type": "json_schema", "json_schema": {"name": "rangs"}}
    )

    client.recupere_propositions([], format_reponse=format_reponse)

    assert completion.parametres_recus["response_format"] == format_reponse
