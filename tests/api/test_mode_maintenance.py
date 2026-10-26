from fastapi.testclient import TestClient

from configuration import Mode
from serveur_de_test import ServiceAlbertMemoire


def test_mode_maintenance_retourne_200(
    un_serveur_de_test, un_adaptateur_de_chiffrement
):
    serveur = un_serveur_de_test(
        mode=Mode.PRODUCTION,
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        mode_maintenance=True,
    )
    client = TestClient(serveur)

    reponse = client.get("/")

    assert reponse.status_code == 200


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


def test_mode_maintenance_retourne_du_HTML(
    un_serveur_de_test, un_adaptateur_de_chiffrement
):
    serveur = un_serveur_de_test(
        mode=Mode.PRODUCTION,
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        mode_maintenance=True,
    )
    client = TestClient(serveur)

    reponse = client.get("/")

    assert "text/html" in reponse.headers["content-type"]


def test_mode_maintenance_autorise_les_assets_statiques(
    un_serveur_de_test, un_adaptateur_de_chiffrement
):
    serveur = un_serveur_de_test(
        mode=Mode.PRODUCTION,
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        mode_maintenance=True,
    )
    client = TestClient(serveur)

    reponse = client.get("/assets/test.css")

    assert reponse.status_code == 200

def test_mode_maintenance_empeche_les_appel_api(un_serveur_de_test, un_adaptateur_de_chiffrement):
    service_albert = ServiceAlbertMemoire()
    serveur = un_serveur_de_test(
        mode=Mode.PRODUCTION,
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
        service_albert=service_albert,
        mode_maintenance=True,
    )
    client = TestClient(serveur)

    reponse = client.post("/api/conversation", json={"question": "Qui es-tu"})

    assert reponse.status_code == 200
    assert service_albert.question_recue is None
