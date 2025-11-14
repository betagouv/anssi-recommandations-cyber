import pytest
from fastapi.testclient import TestClient

from adaptateurs.journal import (
    TypeEvenement,
)
from schemas.client_albert import Paragraphe, ReponseQuestion
from schemas.violations import (
    ViolationIdentite,
    ViolationMalveillance,
    ViolationThematique,
)
from configuration import Mode

from serveur_de_test import (
    ConstructeurAdaptateurBaseDeDonnees,
    ConstructeurAdaptateurJournal,
    ConstructeurServiceAlbert,
    ConstructeurServeur,
)
from adaptateur_chiffrement import ConstructeurAdaptateurChiffrement


def test_route_recherche_repond_correctement() -> None:
    service_albert = ConstructeurServiceAlbert().construit()
    serveur = ConstructeurServeur().avec_service_albert(service_albert).construit()
    client: TestClient = TestClient(serveur)

    reponse = client.post("/api/recherche", json={"question": "Ma question test"})

    assert reponse.status_code == 200
    service_albert.recherche_paragraphes.assert_called_once()


def test_route_recherche_donnees_correctes() -> None:
    paragraphes: list[Paragraphe] = []
    service_albert = (
        ConstructeurServiceAlbert()
        .qui_retourne_les_paragraphes(paragraphes)
        .construit()
    )
    serveur = ConstructeurServeur().avec_service_albert(service_albert).construit()
    client: TestClient = TestClient(serveur)

    reponse = client.post("/api/recherche", json={"question": "Ma question test"})
    resultat = reponse.json()

    assert isinstance(resultat, list)
    assert len(resultat) == len(paragraphes)
    service_albert.recherche_paragraphes.assert_called_once()


def test_route_recherche_retourne_la_bonne_structure_d_objet() -> None:
    paragraphes = [
        Paragraphe(
            contenu="Contenu du paragraphe 1",
            url="https://cyber.gouv.fr/sites/default/files/2021/10/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
            score_similarite=0.75,
            numero_page=29,
            nom_document="anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
        ),
    ]

    service_albert = (
        ConstructeurServiceAlbert()
        .qui_retourne_les_paragraphes(paragraphes)
        .construit()
    )
    serveur = ConstructeurServeur().avec_service_albert(service_albert).construit()

    client: TestClient = TestClient(serveur)
    reponse = client.post("/api/recherche", json={"question": "Ma question test"})

    resultat = reponse.json()
    assert len(resultat) == 1
    p1 = resultat[0]
    assert p1["contenu"] == "Contenu du paragraphe 1"
    assert (
        p1["url"]
        == "https://cyber.gouv.fr/sites/default/files/2021/10/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf"
    )
    assert p1["score_similarite"] == 0.75
    assert p1["numero_page"] == 29
    assert (
        p1["nom_document"]
        == "anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf"
    )

    service_albert.recherche_paragraphes.assert_called_once()


def test_route_pose_question_repond_correctement() -> None:
    reponse = ReponseQuestion(
        reponse="Réponse de test d'Albert",
        paragraphes=[
            Paragraphe(
                score_similarite=0.75,
                numero_page=29,
                url="https://cyber.gouv.fr/sites/default/files/2021/10/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                nom_document="anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                contenu="Contenu du paragraphe 1",
            ),
        ],
        question="Qui es-tu",
        violation=None,
    )

    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construit()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construit()
    )
    serveur = (
        ConstructeurServeur()
        .avec_service_albert(service_albert)
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construit()
    )

    client: TestClient = TestClient(serveur)
    r = client.post("/api/pose_question", json={"question": "Qui es-tu"})

    assert r.status_code == 200
    service_albert.pose_question.assert_called_once()

    serveur.dependency_overrides.clear()


def test_route_pose_question_retourne_donnees_correctes() -> None:
    reponse = ReponseQuestion(
        reponse="Réponse de test d'Albert",
        paragraphes=[
            Paragraphe(
                score_similarite=0.75,
                numero_page=29,
                url="https://cyber.gouv.fr/sites/default/files/2021/10/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                nom_document="anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                contenu="Contenu du paragraphe 1",
            ),
            Paragraphe(
                score_similarite=0.72,
                numero_page=15,
                url="https://cyber.gouv.fr/sites/default/files/2017/01/guide_hygiene_informatique_anssi.pdf",
                nom_document="guide_hygiene_informatique_anssi.pdf",
                contenu="Contenu du paragraphe 2",
            ),
        ],
        question="Qui es-tu",
        violation=None,
    )

    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construit()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construit()
    )
    serveur = (
        ConstructeurServeur()
        .avec_service_albert(service_albert)
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construit()
    )

    client_http = TestClient(serveur)
    r = client_http.post("/api/pose_question", json={"question": "Qui es-tu"})
    resultat = r.json()

    assert "reponse" in resultat
    assert "paragraphes" in resultat
    assert "question" in resultat
    assert resultat["reponse"] == "Réponse de test d'Albert"
    assert isinstance(resultat["paragraphes"], list)
    assert len(resultat["paragraphes"]) == 2

    p1 = resultat["paragraphes"][0]
    assert p1["score_similarite"] == 0.75
    assert p1["numero_page"] == 29
    assert (
        p1["url"]
        == "https://cyber.gouv.fr/sites/default/files/2021/10/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf"
    )
    assert (
        p1["nom_document"]
        == "anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf"
    )
    assert p1["contenu"] == "Contenu du paragraphe 1"
    assert resultat["question"] == "Qui es-tu"

    service_albert.pose_question.assert_called_once()
    adaptateur_base_de_donnees.sauvegarde_interaction.assert_called_once()


@pytest.mark.parametrize("mode", [Mode.DEVELOPPEMENT, Mode.PRODUCTION])
def test_route_pose_question_emet_un_evenement_journal_indiquant_la_creation_d_une_interaction(
    mode,
) -> None:
    valeur_hachee = "haché"
    reponse = ReponseQuestion(
        reponse="ok", paragraphes=[], question="Q?", violation=None
    )

    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construit()
    adaptateur_chiffrement = (
        ConstructeurAdaptateurChiffrement().qui_hache(valeur_hachee).construit()
    )
    adaptateur_journal = ConstructeurAdaptateurJournal().construit()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construit()
    )
    serveur = (
        ConstructeurServeur(mode=mode)
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .avec_adaptateur_chiffrement_pour_les_routes_d_api(adaptateur_chiffrement)
        .avec_adaptateur_journal(adaptateur_journal)
        .avec_service_albert(service_albert)
        .construit()
    )

    client: TestClient = TestClient(serveur)
    client.post(
        "/api/pose_question",
        json={"question": "Qui es-tu ?"},
    )

    adaptateur_journal.consigne_evenement.assert_called_once()
    [args, kwargs] = adaptateur_journal.consigne_evenement._mock_call_args
    assert kwargs["type"] == TypeEvenement.INTERACTION_CREEE
    assert kwargs["donnees"].id_interaction == valeur_hachee
    assert kwargs["donnees"].model_dump_json()

    adaptateur_chiffrement.hache.assert_called_once()
    [args, kwargs] = adaptateur_chiffrement.hache._mock_call_args
    assert args[0] == "id-interaction-test"


@pytest.mark.parametrize(
    "violation", [ViolationIdentite(), ViolationMalveillance(), ViolationThematique()]
)
def test_route_pose_question_emet_un_evenement_journal_indiquant_la_detection_d_une_question_illegale(
    violation,
) -> None:
    valeur_hachee = "haché"
    reponse = ReponseQuestion(
        reponse="", paragraphes=[], question="Q?", violation=violation
    )

    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construit()
    adaptateur_chiffrement = (
        ConstructeurAdaptateurChiffrement().qui_hache(valeur_hachee).construit()
    )
    adaptateur_journal = ConstructeurAdaptateurJournal().construit()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construit()
    )
    serveur = (
        ConstructeurServeur()
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .avec_adaptateur_chiffrement_pour_les_routes_d_api(adaptateur_chiffrement)
        .avec_adaptateur_journal(adaptateur_journal)
        .avec_service_albert(service_albert)
        .construit()
    )

    client: TestClient = TestClient(serveur)
    client.post(
        "/api/pose_question",
        json={"question": "Qui es-tu ?"},
    )

    assert adaptateur_journal.consigne_evenement.call_count == 2
    [args, kwargs] = adaptateur_journal.consigne_evenement._mock_call_args
    assert kwargs["type"] == TypeEvenement.VIOLATION_DETECTEE
    assert kwargs["donnees"].id_interaction == valeur_hachee
    assert kwargs["donnees"].type_violation == violation.__class__.__name__
    assert kwargs["donnees"].model_dump_json()

    assert adaptateur_journal.consigne_evenement.call_count == 2
    [args, kwargs] = adaptateur_chiffrement.hache._mock_call_args
    assert args[0] == "id-interaction-test"


def test_route_pose_question_retourne_id_dans_body() -> None:
    reponse = ReponseQuestion(
        reponse="ok", paragraphes=[], question="Q?", violation=None
    )

    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construit()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construit()
    )
    serveur = (
        ConstructeurServeur()
        .avec_service_albert(service_albert)
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construit()
    )

    client = TestClient(serveur)
    r = client.post("/api/pose_question", json={"question": "Q?"})
    j = r.json()
    assert r.status_code == 200
    assert j["reponse"] == "ok"
    assert j["interaction_id"] == "id-interaction-test"
