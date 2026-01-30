from openai import OpenAI
from infra.albert.client_albert import fabrique_client_albert, ClientAlbertHttp


def test_peut_fabriquer_un_client_albert_avec_une_configuration_par_defaut(
    une_configuration_albert_client,
) -> None:
    client = fabrique_client_albert(une_configuration_albert_client)

    assert isinstance(client.client_openai, OpenAI)
    assert isinstance(client.client_http, ClientAlbertHttp)
