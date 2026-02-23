from configuration import recupere_configuration
from infra.albert.client_albert import ClientAlbertApi
from question.reformulateur_de_question import ReformulateurDeQuestion
from services.fabrique_service_albert import fabrique_service_albert


def test_peut_fabriquer_un_service_albert_avec_une_configuration_par_defaut() -> None:
    service_albert = fabrique_service_albert()

    assert isinstance(service_albert.client, ClientAlbertApi)
    assert "Tu es un service développé par l'ANSSI" in service_albert.prompt_systeme


def test_la_configuration_contient_la_taille_de_la_fenetre_historique() -> None:
    configuration = recupere_configuration()

    assert configuration.albert.service.taille_fenetre_historique == 10


def test_fabrique_un_service_albert_avec_un_reformulateur(monkeypatch) -> None:
    monkeypatch.setenv("REFORMULATEUR_ACTIVE", "true")
    service_albert = fabrique_service_albert()

    assert service_albert.reformulateur is not None
    assert isinstance(service_albert.reformulateur, ReformulateurDeQuestion)
    assert (
        "composant de reformulation"
        in service_albert.reformulateur.prompt_de_reformulation
    )
