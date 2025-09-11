from unittest.mock import Mock, patch
from starlette.testclient import TestClient
from main import (
    route_pose_question,
    app,
    fabrique_adaptateur_base_de_donnees_retour_utilisatrice,
)
from schemas.requetes import QuestionRequete
from schemas.reponses import ReponseQuestion
from adaptateur_base_de_donnees import AdaptateurBaseDeDonnees
from client_albert import ClientAlbert
from test_adaptateur_base_de_donnees_retour_utilisatrice import adaptateur_test
import jwt
from datetime import datetime, timedelta, UTC

TEST_JWT_SECRET = "test-secret-key-for-ci-cd-only-123456789"


def test_route_pose_question_avec_objet_gestionnaire_en_parametre_retoure_la_reponse():
    mock_client_albert = Mock(spec=ClientAlbert)
    mock_adaptateur = Mock(spec=AdaptateurBaseDeDonnees)

    reponse_attendue = ReponseQuestion(
        reponse="Test réponse", paragraphes=[], question="Test question"
    )
    mock_client_albert.pose_question.return_value = reponse_attendue
    mock_adaptateur.sauvegarde_interaction.return_value = "test-id-123"

    requete = QuestionRequete(question="Test question")

    resultat = route_pose_question(requete, mock_client_albert, mock_adaptateur)

    assert resultat == reponse_attendue
    mock_client_albert.pose_question.assert_called_once_with("Test question")
    mock_adaptateur.sauvegarde_interaction.assert_called_once_with(reponse_attendue)


def test_route_pose_question_sauvegarde_interaction(adaptateur_test):
    mock_client_albert = Mock(spec=ClientAlbert)

    reponse_attendue = ReponseQuestion(
        reponse="Test réponse", paragraphes=[], question="Test question"
    )
    mock_client_albert.pose_question.return_value = reponse_attendue

    requete = QuestionRequete(question="Test question")

    _ = route_pose_question(requete, mock_client_albert, adaptateur_test)

    stats = adaptateur_test.obtient_statistiques()
    assert stats["total_interactions"] == 1
    assert stats["total_retours"] == 0


def test_gestionnaire_lit_interactions_sauvegardees(adaptateur_test):
    gestionnaire = adaptateur_test

    reponse_question = ReponseQuestion(
        reponse="Test réponse", paragraphes=[], question="Test question"
    )

    id_interaction = gestionnaire.sauvegarde_interaction(reponse_question)

    interaction_lue = gestionnaire.lit_interaction(id_interaction)

    assert interaction_lue is not None
    assert interaction_lue.reponse_question.question == "Test question"
    assert interaction_lue.reponse_question.reponse == "Test réponse"
    assert interaction_lue.retour_utilisatrice is None


@patch("main.recupere_configuration")
def test_route_retour_accepte_retour_utilisatrice_et_renvoie_200(mock_config):
    mock_config.return_value = {"JWT_SECRET_KEY": TEST_JWT_SECRET}

    mock_gestionnaire = Mock(spec=AdaptateurBaseDeDonnees)
    mock_gestionnaire.ajoute_retour_utilisatrice.return_value = True

    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock_gestionnaire

    try:
        client = TestClient(app)

        # Créer un token JWT pour le test
        payload_jwt = {
            "interaction_id": "test-id-123",
            "exp": datetime.now(UTC) + timedelta(hours=24),
        }
        token = jwt.encode(payload_jwt, TEST_JWT_SECRET, algorithm="HS256")

        payload = {
            "pouce_leve": True,
            "commentaire": "Très utile, merci !",
        }

        response = client.post(
            "/retour", json=payload, cookies={"interaction_token": token}
        )

        assert response.status_code == 200
        mock_gestionnaire.ajoute_retour_utilisatrice.assert_called_once()

    finally:
        app.dependency_overrides.clear()


@patch("main.recupere_configuration")
def test_route_retour_renvoie_donnees_retour_utilisatrice(mock_config):
    mock_config.return_value = {"JWT_SECRET_KEY": TEST_JWT_SECRET}

    mock_gestionnaire = Mock(spec=AdaptateurBaseDeDonnees)
    mock_gestionnaire.ajoute_retour_utilisatrice.return_value = True

    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock_gestionnaire

    try:
        client = TestClient(app)

        # Créer un token JWT pour le test
        payload_jwt = {
            "interaction_id": "test-id-123",
            "exp": datetime.now(UTC) + timedelta(hours=24),
        }
        token = jwt.encode(payload_jwt, TEST_JWT_SECRET, algorithm="HS256")

        payload = {
            "pouce_leve": True,
            "commentaire": "Très utile, merci !",
        }

        response = client.post(
            "/retour", json=payload, cookies={"interaction_token": token}
        )
        data = response.json()

        assert data["succes"] is True
        assert data["commentaire"] == "Très utile, merci !"
        mock_gestionnaire.ajoute_retour_utilisatrice.assert_called_once()

    finally:
        app.dependency_overrides.clear()


@patch("main.recupere_configuration")
def test_route_retour_puis_lecture_avec_le_gestionnaire_et_verification_des_donnes(
    mock_config,
    adaptateur_test,
):
    mock_config.return_value = {"JWT_SECRET_KEY": TEST_JWT_SECRET}

    reponse_question = ReponseQuestion(
        reponse="Test réponse", paragraphes=[], question="Test question"
    )
    id_interaction = adaptateur_test.sauvegarde_interaction(reponse_question)

    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: adaptateur_test

    try:
        client = TestClient(app)

        payload_jwt = {
            "interaction_id": id_interaction,
            "exp": datetime.now(UTC) + timedelta(hours=24),
        }
        token = jwt.encode(payload_jwt, TEST_JWT_SECRET, algorithm="HS256")

        payload = {
            "pouce_leve": True,
            "commentaire": "Excellent, très clair !",
        }

        _ = client.post("/retour", json=payload, cookies={"interaction_token": token})

        retour_sauvegarde = adaptateur_test.lit_interaction(
            id_interaction
        ).retour_utilisatrice

        assert retour_sauvegarde is not None
        assert retour_sauvegarde.pouce_leve is True
        assert retour_sauvegarde.commentaire == "Excellent, très clair !"
        assert retour_sauvegarde.horodatage is not None

    finally:
        app.dependency_overrides.clear()
