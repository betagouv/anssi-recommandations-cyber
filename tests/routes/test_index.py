import pytest
from fastapi.testclient import TestClient
from serveur import (
    fabrique_serveur,
)

from configuration import Mode

serveur = fabrique_serveur(Mode.PRODUCTION)


def test_route_index_sert_une_page_html() -> None:
    client: TestClient = TestClient(serveur)
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type")


@pytest.mark.parametrize(
    "entete,valeur_attendue",
    list(
        map(
            lambda x: pytest.param(x[0], x[1], id=f"header `{x[0]}`"),
            [
                [
                    "content-security-policy",
                    "default-src 'self' https://lab-anssi-ui-kit-prod-s3-assets.cellar-c2.services.clever-cloud.com;",
                ],
                ["cross-origin-embedder-policy", "credentialless"],
                ["cross-origin-opener-policy", "same-origin"],
                ["cross-origin-resource-policy", "same-origin"],
                ["expect-ct", "max-age=86400, enforce"],
                ["origin-agent-cluster", "?1"],
                [
                    "strict-transport-security",
                    "max-age=63072000; includeSubDomains; preload",
                ],
                ["x-frame-options", "DENY"],
                ["x-content-type-options", "nosniff"],
                ["x-dns-prefetch-control", "off"],
            ],
        )
    ),
)
def test_route_index_sert_des_entetes_securisant_la_page_servie_avec_les_bonnes_valeurs(
    entete: str, valeur_attendue: str
) -> None:
    client: TestClient = TestClient(serveur)
    response = client.get("/")

    valeur_entete = response.headers.get(entete)

    assert valeur_entete == valeur_attendue
