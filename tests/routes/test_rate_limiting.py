import pytest

from fastapi.testclient import TestClient

from adaptateurs.chiffrement import (
    fabrique_adaptateur_chiffrement,
)
from configuration import Mode

from serveur_de_test import (
    ConstructeurServeur,
)
from starlette.routing import Route


# Semble résoudre une confusion de `mypy` qui apparait quand inlinée...
def dans_l_ensemble(ensemble, element) -> bool:
    return element in ensemble


# Par simplicité, on teste seulement les routes GET.
routes_get = list(
    map(
        lambda r: r.path,
        filter(
            lambda r: isinstance(r, Route) and dans_l_ensemble(r.methods, "GET"),
            ConstructeurServeur(
                mode=Mode.DEVELOPPEMENT,
                adaptateur_chiffrement=fabrique_adaptateur_chiffrement(),
            )
            .construit()
            .routes,
        ),
    )
)


@pytest.mark.parametrize("route", routes_get)
def test_les_routes_limitent_le_nombre_de_requetes_quand_un_utilisateur_fait_trop_de_requetes(
    route,
) -> None:
    serveur = ConstructeurServeur(
        max_requetes_par_minute=1,
        mode=Mode.DEVELOPPEMENT,
    ).construit()
    client: TestClient = TestClient(serveur)

    ip_client = "123.123.123.123"

    client.get(route, headers={"X-Forwarded-For": f"{ip_client}"})
    reponse = client.get(route, headers={"X-Forwarded-For": f"{ip_client}"})

    assert reponse.status_code == 429


@pytest.mark.parametrize("route", routes_get)
def test_les_routes_ne_limitent_PAS_le_nombre_de_requetes_quand_elles_viennent_d_utilisateurs_differents(
    route,
) -> None:
    serveur = ConstructeurServeur(
        max_requetes_par_minute=1,
        mode=Mode.DEVELOPPEMENT,
    ).construit()
    client: TestClient = TestClient(serveur)

    ip_client = "123.123.123.123"
    ip_autre_client = "122.122.122.122"

    client.get(route, headers={"X-Forwarded-For": f"{ip_client}"})
    reponse = client.get(route, headers={"X-Forwarded-For": f"{ip_autre_client}"})

    assert reponse.status_code == 200
