from fastapi.testclient import TestClient

from configuration import Mode


def test_mode_maintenance_retourne_une_erreur_HTTP_503(
    un_serveur_de_test, un_adaptateur_de_chiffrement
):
    serveur = un_serveur_de_test(
        mode=Mode.PRODUCTION,
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        mode_maintenance=True,
    )
    client = TestClient(serveur)

    reponse = client.get("/")

    assert reponse.status_code == 503


def test_mode_maintenance_desactive_retourne_un_code_HTTP_200(
    un_serveur_de_test, un_adaptateur_de_chiffrement
):
    serveur = un_serveur_de_test(
        mode=Mode.PRODUCTION,
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        mode_maintenance=False,
    )
    client = TestClient(serveur)

    reponse = client.get("/")

    assert reponse.status_code == 200