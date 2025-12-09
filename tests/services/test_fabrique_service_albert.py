from infra.albert.client_albert import ClientAlbertApi
from services.fabrique_service_albert import fabrique_service_albert


def test_peut_fabriquer_un_service_albert_avec_une_configuration_par_defaut() -> None:
    service_albert = fabrique_service_albert()

    assert isinstance(service_albert.client, ClientAlbertApi)
    assert (
        "Tu es un service développé par ou pour l’ANSSI"
        in service_albert.prompt_systeme
    )
