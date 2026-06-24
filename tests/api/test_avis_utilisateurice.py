import pytest
from starlette.testclient import TestClient


@pytest.mark.parametrize(
    "valeur_exactitude",
    ["très bonne", "bonne", "correcte"],
)
def test_peut_ajouter_un_avis_sur_l_exactitude(
    valeur_exactitude: str, un_serveur_de_test
):
    serveur = un_serveur_de_test()
    client = TestClient(serveur)
    payload = {
        "id_interaction": "123",
        "id_conversation": "456",
        "avis": {
            "exactitude": {"valeur": valeur_exactitude},
            "completude": {"valeur": "bonne"},
        },
    }

    reponse = client.post("/api/avis", json=payload)

    assert reponse.status_code == 200


@pytest.mark.parametrize(
    "valeur_completude",
    ["très bonne", "bonne", "correcte"],
)
def test_peut_ajouter_un_avis_sur_la_completude(
    valeur_completude: str, un_serveur_de_test
):
    serveur = un_serveur_de_test()
    client = TestClient(serveur)
    payload = {
        "id_interaction": "123",
        "id_conversation": "456",
        "avis": {
            "exactitude": {"valeur": "bonne"},
            "completude": {"valeur": valeur_completude},
        },
    }

    reponse = client.post("/api/avis", json=payload)

    assert reponse.status_code == 200


@pytest.mark.parametrize(
    "valeur_exactitude",
    [
        {
            "informations_erronees": "",
            "sources_adaptees": "ma source",
            "message_attendu": "Value error, Le champ 'informations_erronees' est obligatoire lorsque l'exactitude est fausse.",
        },
        {
            "informations_erronees": "valeur",
            "sources_adaptees": "",
            "message_attendu": "Value error, Le champ 'sources_adaptees' est obligatoire lorsque l'exactitude est fausse.",
        },
    ],
)
def test_les_informations_erronees_sont_obligatoires_pour_un_avis_fausse_sur_l_exactitude(
    valeur_exactitude,
    un_serveur_de_test,
):
    serveur = un_serveur_de_test()
    client = TestClient(serveur)
    payload = {
        "id_interaction": "123",
        "id_conversation": "456",
        "avis": {
            "exactitude": {
                "valeur": "fausse",
                "informations_erronees": valeur_exactitude.get("informations_erronees"),
                "sources_adaptees": valeur_exactitude.get("sources_adaptees"),
            },
            "completude": {"valeur": "bonne"},
        },
    }

    reponse = client.post("/api/avis", json=payload)
    print(reponse.json())
    assert reponse.status_code == 422
    assert reponse.json().get("detail")[0].get("msg") == valeur_exactitude.get(
        "message_attendu"
    )


@pytest.mark.parametrize(
    "valeur_completude",
    [
        {
            "informations_erronees": "",
            "sources_adaptees": "ma source",
            "message_attendu": "Value error, Le champ 'informations_erronees' est obligatoire lorsque la complétude est fausse.",
        },
        {
            "informations_erronees": "valeur",
            "sources_adaptees": "",
            "message_attendu": "Value error, Le champ 'sources_adaptees' est obligatoire lorsque la complétude est fausse.",
        },
    ],
)
def test_les_informations_erronees_sont_obligatoires_pour_un_avis_fausse_sur_la_completude(
    valeur_completude,
    un_serveur_de_test,
):
    serveur = un_serveur_de_test()
    client = TestClient(serveur)
    payload = {
        "id_interaction": "123",
        "id_conversation": "456",
        "avis": {
            "completude": {
                "valeur": "fausse",
                "informations_erronees": valeur_completude.get("informations_erronees"),
                "sources_adaptees": valeur_completude.get("sources_adaptees"),
            },
            "exactitude": {"valeur": "bonne"},
        },
    }

    reponse = client.post("/api/avis", json=payload)
    print(reponse.json())
    assert reponse.status_code == 422
    assert reponse.json().get("detail")[0].get("msg") == valeur_completude.get(
        "message_attendu"
    )
