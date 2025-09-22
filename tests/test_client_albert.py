from client_albert import fabrique_client_albert


def test_peut_fabriquer_un_client_albert_avec_une_configuration_par_defaut():
    client_albert = fabrique_client_albert()

    assert client_albert.client.__class__.__name__ == "OpenAI"
    assert client_albert.session.__class__.__name__ == "ClientAlbertHttp"
