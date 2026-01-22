from fastapi.testclient import TestClient

from configuration import Mode


def test_route_sante_est_exposee_en_developpement(
    un_serveur_de_test, un_adaptateur_de_chiffrement
) -> None:
    serveur = un_serveur_de_test(
        mode=Mode.DEVELOPPEMENT, adaptateur_chiffrement=un_adaptateur_de_chiffrement()
    )
    client: TestClient = TestClient(serveur)

    reponse = client.get("/api/sante")

    assert reponse.status_code == 200
    assert reponse.json() == {"status": "ok"}


def test_route_sante_n_est_pas_exposee_en_production(
    un_serveur_de_test, un_adaptateur_de_chiffrement
) -> None:
    serveur = un_serveur_de_test(
        mode=Mode.PRODUCTION, adaptateur_chiffrement=un_adaptateur_de_chiffrement()
    )
    client: TestClient = TestClient(serveur)

    reponse = client.get("/api/sante")

    assert reponse.status_code == 404
    assert reponse.json() == {"detail": "Not Found"}
