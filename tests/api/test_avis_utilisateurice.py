import pytest
from starlette.testclient import TestClient

from adaptateurs.journal import AdaptateurJournalMemoire, TypeEvenement


@pytest.mark.parametrize(
    "valeur_pertinence",
    ["très pertinente", "pertinente", "correcte"],
)
def test_peut_ajouter_un_avis_sur_la_pertinence(
    valeur_pertinence: str, un_serveur_de_test
):
    serveur = un_serveur_de_test()
    client = TestClient(serveur)
    payload = {
        "id_interaction": "123",
        "id_conversation": "456",
        "avis": {
            "pertinence": {"valeur": valeur_pertinence},
            "sources_adaptees": {"valeur": "oui, partiellement"},
        },
    }

    reponse = client.post("/api/avis", json=payload)

    assert reponse.status_code == 200


@pytest.mark.parametrize(
    "valeur_sources_adaptees",
    ["oui, tout à fait", "oui, partiellement"],
)
def test_peut_ajouter_un_avis_sur_les_sources_adaptees(
    valeur_sources_adaptees, un_serveur_de_test
):
    serveur = un_serveur_de_test()
    client = TestClient(serveur)
    payload = {
        "id_interaction": "123",
        "id_conversation": "456",
        "avis": {
            "pertinence": {"valeur": "pertinente"},
            "sources_adaptees": {"valeur": valeur_sources_adaptees},
        },
    }

    reponse = client.post("/api/avis", json=payload)

    assert reponse.status_code == 200


@pytest.mark.parametrize(
    "valeur_pertinence",
    [
        {
            "informations_erronees": "",
            "message_attendu": "Value error, Le champ 'informations_erronees' est obligatoire lorsque la pertinence est erronée.",
        },
        {
            "informations_erronees": "valeur pas assez longue",
            "message_attendu": "Value error, Le champ 'informations_erronees' doit contenir au moins 50 caractères.",
        },
        {
            "informations_erronees": "a" * 5_001,
            "message_attendu": "Value error, Le champ 'informations_erronees' ne peut contenir que 5000 caractères maximum.",
        },
    ],
)
def test_les_informations_erronees_sont_obligatoires_pour_un_avis_sur_la_pertinence(
    valeur_pertinence,
    un_serveur_de_test,
):
    serveur = un_serveur_de_test()
    client = TestClient(serveur)
    payload = {
        "id_interaction": "123",
        "id_conversation": "456",
        "avis": {
            "pertinence": {
                "valeur": "erronée",
                "informations_erronees": valeur_pertinence.get("informations_erronees"),
            },
            "sources_adaptees": {"valeur": "bonne"},
        },
    }

    reponse = client.post("/api/avis", json=payload)
    print(reponse.json())
    assert reponse.status_code == 422
    assert reponse.json().get("detail")[0].get("msg") == valeur_pertinence.get(
        "message_attendu"
    )


@pytest.mark.parametrize(
    "valeur_sources_adaptees",
    [
        {
            "sources_adaptees": "",
            "message_attendu": "Value error, Le champ 'liste' est obligatoire lorsque l’avis sur les sources adaptées est non.",
            "raisons": ["Sources peu pertinentes"],
        },
        {
            "sources_adaptees": "valeur pas assez longue",
            "message_attendu": "Value error, Le champ 'liste' doit contenir au moins 50 caractères.",
            "raisons": ["Sources manquantes"],
        },
        {
            "sources_adaptees": "b" * 5_001,
            "message_attendu": "Value error, Le champ 'liste' ne peut contenir que 5000 caractères maximum.",
            "raisons": ["Sources peu pertinentes", "Sources manquantes"],
        },
    ],
)
def test_la_liste_des_sources_adaptees_est_obligatoire_si_l_avis_est_negatif(
    valeur_sources_adaptees,
    un_serveur_de_test,
):
    serveur = un_serveur_de_test()
    client = TestClient(serveur)
    payload = {
        "id_interaction": "123",
        "id_conversation": "456",
        "avis": {
            "sources_adaptees": {
                "valeur": "non",
                "liste": valeur_sources_adaptees.get("sources_adaptees"),
            },
            "pertinence": {"valeur": "pertinente"},
        },
    }

    reponse = client.post("/api/avis", json=payload)
    print(reponse.json())
    assert reponse.status_code == 422
    assert reponse.json().get("detail")[0].get("msg") == valeur_sources_adaptees.get(
        "message_attendu"
    )


@pytest.mark.parametrize(
    "valeur_sources_adaptees",
    [
        {
            "raisons": [],
            "message_attendu": "Value error, Le champ 'raisons' est obligatoire lorsque l’avis sur les sources adaptées est non.",
            "sources_adaptees": "Les sources non adaptées sont : les sources non adaptées",
        },
        {
            "raisons": ["raison non valable"],
            "message_attendu": "Value error, Le champ 'raisons' accepte comme valeurs 'Sources peu pertinentes', 'Sources manquantes'.",
            "sources_adaptees": "Les sources non adaptées sont : les sources non adaptées",
        },
    ],
)
def test_les_raisons_sont_obligatoires_si_l_avis_est_negatif_pour_les_sources_adaptees(
    valeur_sources_adaptees,
    un_serveur_de_test,
):
    serveur = un_serveur_de_test()
    client = TestClient(serveur)
    payload = {
        "id_interaction": "123",
        "id_conversation": "456",
        "avis": {
            "sources_adaptees": {
                "valeur": "non",
                "liste": valeur_sources_adaptees.get("sources_adaptees"),
                "raisons": valeur_sources_adaptees.get("raisons"),
            },
            "pertinence": {"valeur": "pertinente"},
        },
    }

    reponse = client.post("/api/avis", json=payload)
    print(reponse.json())
    assert reponse.status_code == 422
    assert reponse.json().get("detail")[0].get("msg") == valeur_sources_adaptees.get(
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
            "sources_adaptees": {
                "valeur": "non",
                "liste": "Les sources adaptées pour la complétude sont : les sources adaptées",
                "raisons": ["Sources peu pertinentes"],
            },
            "pertinence": {"valeur": "pertinente"},
        },
    }

    client.post("/api/avis", json=payload)

    evenements = adaptateur_journal.les_evenements()
    assert evenements[0]["type"] == TypeEvenement.AVIS_AVANCE_SOUMIS
    assert evenements[0]["donnees"].id_interaction == "123"
    assert evenements[0]["donnees"].id_conversation == "456"
    assert evenements[0]["donnees"].avis.sources_adaptees.valeur == "non"
    assert (
        evenements[0]["donnees"].avis.sources_adaptees.liste
        == "Les sources adaptées pour la complétude sont : les sources adaptées"
    )
    assert evenements[0]["donnees"].avis.sources_adaptees.raisons == [
        "Sources peu pertinentes"
    ]
    assert evenements[0]["donnees"].avis.pertinence.valeur == "pertinente"
    assert evenements[0]["donnees"].avis.pertinence.informations_erronees is None
    assert evenements[0]["donnees"].avis.pertinence.commentaire is None
