import pytest
from fastapi.testclient import TestClient

from adaptateur_chiffrement import (
    AdaptateurChiffrementDeTest,
)
from adaptateurs.journal import (
    TypeEvenement,
)
from configuration import Mode
from schemas.albert import Paragraphe, ReponseQuestion
from schemas.type_utilisateur import TypeUtilisateur
from schemas.violations import (
    ViolationIdentite,
    ViolationMalveillance,
    ViolationThematique,
)
from serveur_de_test import (
    ConstructeurAdaptateurBaseDeDonnees,
    ConstructeurAdaptateurJournal,
    ConstructeurServiceAlbert,
    ConstructeurServeur,
)


def test_route_pose_question_repond_correctement(adaptateur_chiffrement) -> None:
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

    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construis()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construis()
    )
    serveur = (
        ConstructeurServeur(adaptateur_chiffrement=adaptateur_chiffrement)
        .avec_service_albert(service_albert)
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construis()
    )

    client: TestClient = TestClient(serveur)
    r = client.post("/api/pose_question", json={"question": "Qui es-tu"})

    assert r.status_code == 200
    service_albert.pose_question.assert_called_once()

    serveur.dependency_overrides.clear()


def test_route_pose_question_retourne_donnees_correctes(adaptateur_chiffrement) -> None:
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

    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construis()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construis()
    )
    serveur = (
        ConstructeurServeur(adaptateur_chiffrement=adaptateur_chiffrement)
        .avec_service_albert(service_albert)
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construis()
    )

    client_http = TestClient(serveur)
    r = client_http.post("/api/pose_question", json={"question": "Qui es-tu"})

    assert r.json() == {
        "interaction_id": "id-interaction-test",
        "question": "Qui es-tu",
        "reponse": "Réponse de test d'Albert",
        "paragraphes": [
            {
                "score_similarite": 0.75,
                "numero_page": 29,
                "url": "https://cyber.gouv.fr/sites/default/files/2021/10/anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                "nom_document": "anssi-guide-authentification_multifacteur_et_mots_de_passe.pdf",
                "contenu": "Contenu du paragraphe 1",
            },
            {
                "score_similarite": 0.72,
                "numero_page": 15,
                "url": "https://cyber.gouv.fr/sites/default/files/2017/01/guide_hygiene_informatique_anssi.pdf",
                "nom_document": "guide_hygiene_informatique_anssi.pdf",
                "contenu": "Contenu du paragraphe 2",
            },
        ],
    }

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

    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construis()
    adaptateur_chiffrement = AdaptateurChiffrementDeTest().qui_hache(valeur_hachee)
    adaptateur_journal = ConstructeurAdaptateurJournal().construis()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construis()
    )
    serveur = (
        ConstructeurServeur(mode=mode, adaptateur_chiffrement=adaptateur_chiffrement)
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .avec_adaptateur_chiffrement_pour_les_routes_d_api(adaptateur_chiffrement)
        .avec_adaptateur_journal(adaptateur_journal)
        .avec_service_albert(service_albert)
        .construis()
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
    assert adaptateur_chiffrement.valeur_recue_pour_le_hache == "id-interaction-test"


def test_route_pose_question_emet_un_evenement_donnant_les_informations_sur_l_interaction_creee():
    question_posee = " Qui es-tu ? "
    valeur_hachee = "haché"
    reponse = ReponseQuestion(
        reponse=" Je suis Albert, pour vous servir ",
        paragraphes=[],
        question=question_posee,
        violation=None,
    )
    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construis()
    adaptateur_chiffrement = AdaptateurChiffrementDeTest().qui_hache(valeur_hachee)
    adaptateur_journal = ConstructeurAdaptateurJournal().construis()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construis()
    )
    serveur = (
        ConstructeurServeur(
            mode=Mode.PRODUCTION, adaptateur_chiffrement=adaptateur_chiffrement
        )
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .avec_adaptateur_chiffrement_pour_les_routes_d_api(adaptateur_chiffrement)
        .avec_adaptateur_journal(adaptateur_journal)
        .avec_service_albert(service_albert)
        .construis()
    )

    client = TestClient(serveur)
    client.post(
        "/api/pose_question",
        json={"question": question_posee},
    )

    [args, kwargs] = adaptateur_journal.consigne_evenement._mock_call_args
    assert kwargs["donnees"].longueur_question == 11
    assert kwargs["donnees"].longueur_reponse == 32


def test_route_pose_question_emet_un_evenement_donnant_la_longueur_totale_des_paragraphes_sur_l_interaction_creee(
    un_constructeur_de_paragraphe,
):
    question_posee = " Qui es-tu ? "
    valeur_hachee = "haché"
    reponse = ReponseQuestion(
        reponse=" Je suis Albert, pour vous servir ",
        paragraphes=[
            un_constructeur_de_paragraphe.avec_contenu("Contenu A").construis(),
            un_constructeur_de_paragraphe.avec_contenu("Contenu B").construis(),
        ],
        question=question_posee,
        violation=None,
    )
    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construis()
    adaptateur_chiffrement = AdaptateurChiffrementDeTest().qui_hache(valeur_hachee)
    adaptateur_journal = ConstructeurAdaptateurJournal().construis()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construis()
    )
    serveur = (
        ConstructeurServeur(
            mode=Mode.PRODUCTION, adaptateur_chiffrement=adaptateur_chiffrement
        )
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .avec_adaptateur_chiffrement_pour_les_routes_d_api(adaptateur_chiffrement)
        .avec_adaptateur_journal(adaptateur_journal)
        .avec_service_albert(service_albert)
        .construis()
    )

    client = TestClient(serveur)
    client.post(
        "/api/pose_question",
        json={"question": question_posee},
    )

    [args, kwargs] = adaptateur_journal.consigne_evenement._mock_call_args
    assert kwargs["donnees"].longueur_paragraphes == 18


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

    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construis()
    adaptateur_chiffrement = AdaptateurChiffrementDeTest().qui_hache(valeur_hachee)
    adaptateur_journal = ConstructeurAdaptateurJournal().construis()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construis()
    )
    serveur = (
        ConstructeurServeur(adaptateur_chiffrement=adaptateur_chiffrement)
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .avec_adaptateur_chiffrement_pour_les_routes_d_api(adaptateur_chiffrement)
        .avec_adaptateur_journal(adaptateur_journal)
        .avec_service_albert(service_albert)
        .construis()
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
    assert adaptateur_chiffrement.valeur_recue_pour_le_hache == "id-interaction-test"


def test_route_pose_question_rejette_question_trop_longue(
    adaptateur_chiffrement,
) -> None:
    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construis()
    service_albert = ConstructeurServiceAlbert().construis()
    serveur = (
        ConstructeurServeur(adaptateur_chiffrement=adaptateur_chiffrement)
        .avec_service_albert(service_albert)
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .construis()
    )

    client = TestClient(serveur)
    question_trop_longue = "?" * 5001

    reponse = client.post("/api/pose_question", json={"question": question_trop_longue})

    assert reponse.status_code == 422
    assert "5000" in reponse.json()["detail"][0]["msg"]
    service_albert.pose_question.assert_not_called()

    serveur.dependency_overrides.clear()


@pytest.mark.parametrize(
    "type_utilisateur",
    [TypeUtilisateur.ANSSI, TypeUtilisateur.LAMBDA, TypeUtilisateur.EXPERT_SSI],
)
def test_route_pose_question_identifie_le_type_d_utilisateur(type_utilisateur):
    reponse = ReponseQuestion(
        reponse="ok", paragraphes=[], question="Q?", violation=None
    )
    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construis()
    adaptateur_chiffrement = AdaptateurChiffrementDeTest().qui_dechiffre(
        type_utilisateur
    )
    adaptateur_journal = ConstructeurAdaptateurJournal().construis()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construis()
    )
    serveur = (
        ConstructeurServeur(adaptateur_chiffrement=adaptateur_chiffrement)
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .avec_adaptateur_chiffrement_pour_les_routes_d_api(adaptateur_chiffrement)
        .avec_adaptateur_journal(adaptateur_journal)
        .avec_service_albert(service_albert)
        .construis()
    )

    client = TestClient(serveur)
    client.post(
        "/api/pose_question?type_utilisateur=ABCD", json={"question": "Une question"}
    )

    [args, kwargs] = adaptateur_journal.consigne_evenement._mock_call_args
    assert kwargs["donnees"].type_utilisateur == type_utilisateur


def test_route_pose_question_identifie_comme_inconnu_le_type_d_utilisateur():
    reponse = ReponseQuestion(
        reponse="ok", paragraphes=[], question="Q?", violation=None
    )
    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construis()
    adaptateur_chiffrement = AdaptateurChiffrementDeTest().qui_dechiffre(
        "une chaine inconnue"
    )
    adaptateur_journal = ConstructeurAdaptateurJournal().construis()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construis()
    )
    serveur = (
        ConstructeurServeur(adaptateur_chiffrement=adaptateur_chiffrement)
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .avec_adaptateur_chiffrement_pour_les_routes_d_api(adaptateur_chiffrement)
        .avec_adaptateur_journal(adaptateur_journal)
        .avec_service_albert(service_albert)
        .construis()
    )

    client = TestClient(serveur)
    client.post(
        "/api/pose_question?type_utilisateur=ABCD", json={"question": "Une question"}
    )

    [args, kwargs] = adaptateur_journal.consigne_evenement._mock_call_args
    assert kwargs["donnees"].type_utilisateur == TypeUtilisateur.INCONNU


def test_route_pose_question_identifie_comme_inconnu_le_type_d_utilisateur_si_le_dechiffrement_echoue():
    reponse = ReponseQuestion(
        reponse="ok", paragraphes=[], question="Q?", violation=None
    )
    adaptateur_base_de_donnees = ConstructeurAdaptateurBaseDeDonnees().construis()
    adaptateur_chiffrement = (
        AdaptateurChiffrementDeTest().qui_leve_une_erreur_au_dechiffrement()
    )
    adaptateur_journal = ConstructeurAdaptateurJournal().construis()
    service_albert = (
        ConstructeurServiceAlbert().qui_repond_aux_questions(reponse).construis()
    )
    serveur = (
        ConstructeurServeur(adaptateur_chiffrement=adaptateur_chiffrement)
        .avec_adaptateur_base_de_donnees(adaptateur_base_de_donnees)
        .avec_adaptateur_chiffrement_pour_les_routes_d_api(adaptateur_chiffrement)
        .avec_adaptateur_journal(adaptateur_journal)
        .avec_service_albert(service_albert)
        .construis()
    )

    client = TestClient(serveur)
    client.post(
        "/api/pose_question?type_utilisateur=ABCD", json={"question": "Une question"}
    )

    [args, kwargs] = adaptateur_journal.consigne_evenement._mock_call_args
    assert kwargs["donnees"].type_utilisateur == TypeUtilisateur.INCONNU
