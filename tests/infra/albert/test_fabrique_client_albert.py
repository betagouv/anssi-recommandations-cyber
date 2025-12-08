from openai import OpenAI
from client_albert_de_test import ConstructeurServiceAlbert
from infra.albert.client_albert import fabrique_client_albert, ClientAlbertHttp


def test_peut_fabriquer_un_client_albert_avec_une_configuration_par_defaut() -> None:
    client = fabrique_client_albert(
        ConstructeurServiceAlbert.FAUSSE_CONFIGURATION_ALBERT_CLIENT
    )

    assert isinstance(client.client_openai, OpenAI)
    assert isinstance(client.client_http, ClientAlbertHttp)
