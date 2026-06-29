import pytest
from starlette.testclient import TestClient

from adaptateurs.journal import AdaptateurJournalMemoire, TypeEvenement


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
            "informations_erronees": "Les informations erronées sont : les infos erronées",
            "sources_adaptees": "",
            "message_attendu": "Value error, Le champ 'sources_adaptees' est obligatoire lorsque l'exactitude est fausse.",
        },
        {
            "informations_erronees": "valeur pas assez longue",
            "sources_adaptees": "Les sources adaptées pour l’exactitude sont : les sources adaptées",
            "message_attendu": "Value error, Le champ 'informations_erronees' doit contenir au moins 50 caractères.",
        },
        {
            "informations_erronees": "Les informations erronées sont : les infos erronées",
            "sources_adaptees": "valeur pas assez longue",
            "message_attendu": "Value error, Le champ 'sources_adaptees' doit contenir au moins 50 caractères.",
        },
        {
            "informations_erronees": "a" * 5_001,
            "sources_adaptees": "Les sources adaptées pour l’exactitude sont : les sources adaptées",
            "message_attendu": "Value error, Le champ 'informations_erronees' ne peut contenir que 5000 caractères maximum.",
        },
        {
            "informations_erronees": "Les informations erronées sont : les infos erronées",
            "sources_adaptees": "b" * 5_001,
            "message_attendu": "Value error, Le champ 'sources_adaptees' ne peut contenir que 5000 caractères maximum.",
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
            "sources_adaptees": "Les sources adaptées pour l’exactitude sont : les sources adaptées",
            "message_attendu": "Value error, Le champ 'informations_erronees' est obligatoire lorsque la complétude est fausse.",
        },
        {
            "informations_erronees": "Les informations erronées sont : les infos erronées",
            "sources_adaptees": "",
            "message_attendu": "Value error, Le champ 'sources_adaptees' est obligatoire lorsque la complétude est fausse.",
        },
        {
            "informations_erronees": "valeur pas assez longue",
            "sources_adaptees": "Les sources adaptées pour l’exactitude sont : les sources adaptées",
            "message_attendu": "Value error, Le champ 'informations_erronees' doit contenir au moins 50 caractères.",
        },
        {
            "informations_erronees": "Les informations erronées sont : les infos erronées",
            "sources_adaptees": "valeur pas assez longue",
            "message_attendu": "Value error, Le champ 'sources_adaptees' doit contenir au moins 50 caractères.",
        },
        {
            "informations_erronees": "a" * 5_001,
            "sources_adaptees": "Les sources adaptées pour l’exactitude sont : les sources adaptées",
            "message_attendu": "Value error, Le champ 'informations_erronees' ne peut contenir que 5000 caractères maximum.",
        },
        {
            "informations_erronees": "Les informations erronées sont : les infos erronées",
            "sources_adaptees": "b" * 5_001,
            "message_attendu": "Value error, Le champ 'sources_adaptees' ne peut contenir que 5000 caractères maximum.",
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


def test_consigne_dans_le_journal_un_avis(un_serveur_de_test):
    adaptateur_journal = AdaptateurJournalMemoire()
    serveur = un_serveur_de_test(adaptateur_journal=adaptateur_journal)
    client = TestClient(serveur)
    payload = {
        "id_interaction": "123",
        "id_conversation": "456",
        "avis": {
            "completude": {
                "valeur": "fausse",
                "informations_erronees": "Les informations erronées sont : les infos erronées",
                "sources_adaptees": "Les sources adaptées pour la complétude sont : les sources adaptées",
            },
            "exactitude": {"valeur": "bonne"},
        },
    }

    client.post("/api/avis", json=payload)

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["type"] == TypeEvenement.AVIS_AVANCE_SOUMIS
    assert evenements[0]["donnees"].id_interaction == "123"
    assert evenements[0]["donnees"].id_conversation == "456"
    assert evenements[0]["donnees"].avis.completude.valeur == "fausse"
    assert (
        evenements[0]["donnees"].avis.completude.informations_erronees
        == "Les informations erronées sont : les infos erronées"
    )
    assert (
        evenements[0]["donnees"].avis.completude.sources_adaptees
        == "Les sources adaptées pour la complétude sont : les sources adaptées"
    )
    assert evenements[0]["donnees"].avis.exactitude.valeur == "bonne"
    assert evenements[0]["donnees"].avis.exactitude.informations_erronees is None
    assert evenements[0]["donnees"].avis.exactitude.sources_adaptees is None
    assert evenements[0]["donnees"].avis.exactitude.commentaire is None
