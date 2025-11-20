import pytest
from fastapi.testclient import TestClient

from configuration import Mode

from adaptateur_chiffrement import ConstructeurAdaptateurChiffrement
from serveur_de_test import (
    ConstructeurServeur,
)

NONCE = "un-nonce"
adaptateur_chiffrement = (
    ConstructeurAdaptateurChiffrement().qui_retourne_nonce(NONCE).construis()
)
serveur = ConstructeurServeur(
    mode=Mode.PRODUCTION, adaptateur_chiffrement=adaptateur_chiffrement
).construis()


def test_route_index_sert_une_page_html() -> None:
    client: TestClient = TestClient(serveur)
    reponse = client.get("/")

    assert reponse.status_code == 200
    assert "text/html" in reponse.headers.get("content-type")


@pytest.mark.parametrize(
    "entete,valeur_attendue",
    list(
        map(
            lambda x: pytest.param(x[0], x[1], id=f"header `{x[0]}`"),
            [
                [
                    "content-security-policy",
                    f"default-src 'self' https://lab-anssi-ui-kit-prod-s3-assets.cellar-c2.services.clever-cloud.com; style-src 'self' 'nonce-{NONCE}'; script-src 'self' 'nonce-{NONCE}'",
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
    reponse = client.get("/")

    valeur_entete = reponse.headers.get(entete)

    assert valeur_entete == valeur_attendue
