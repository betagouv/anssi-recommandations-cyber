from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.routing import Route
from typing import Any

from configuration import Mode


# Semble résoudre une confusion de `mypy` qui apparait quand inlinée...
def dans_l_ensemble(ensemble, element) -> bool:
    return element in ensemble


def les_routes_du_serveur(serveur: FastAPI) -> list[Any]:
    return list(
        map(
            lambda r: r.path,  # type:ignore[attr-defined]
            filter(
                lambda r: isinstance(r, Route) and dans_l_ensemble(r.methods, "GET"),
                serveur.routes,
            ),
        )
    )


def test_les_routes_limitent_le_nombre_de_requetes_quand_un_utilisateur_fait_trop_de_requetes(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
) -> None:
    serveur = un_serveur_de_test(
        rate_limit=1, adaptateur_chiffrement=un_adaptateur_de_chiffrement()
    )
    ip_client = "123.123.123.123"

    routes = les_routes_du_serveur(serveur)
    for route in routes:
        client: TestClient = TestClient(serveur)
        client.get(route, headers={"X-Forwarded-For": f"{ip_client}"})
        reponse = client.get(route, headers={"X-Forwarded-For": f"{ip_client}"})

        assert reponse.status_code == 429


def test_les_routes_ne_limitent_PAS_le_nombre_de_requetes_quand_elles_viennent_d_utilisateurs_differents(
    un_serveur_de_test,
    un_adaptateur_de_chiffrement,
) -> None:
    serveur = un_serveur_de_test(
        mode=Mode.DEVELOPPEMENT,
        rate_limit=1,
        adaptateur_chiffrement=un_adaptateur_de_chiffrement(),
    )
    client: TestClient = TestClient(serveur)

    ip_client = "123.123.123.123"
    ip_autre_client = "122.122.122.122"

    routes = les_routes_du_serveur(serveur)
    for route in routes:
        client.get(route, headers={"X-Forwarded-For": f"{ip_client}"})
        reponse = client.get(route, headers={"X-Forwarded-For": f"{ip_autre_client}"})

        assert reponse.status_code == 200
