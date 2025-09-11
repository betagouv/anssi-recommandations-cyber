from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from main import app, fabrique_adaptateur_base_de_donnees_retour_utilisatrice
from adaptateurs import AdaptateurBaseDeDonnees
import jwt
from datetime import datetime, timedelta, UTC

TEST_JWT_SECRET = "test-secret-key-for-ci-cd-only-123456789"


@patch("main.recupere_configuration")
def test_route_retour_avec_jwt_retourne_succes_200(mock_config):
    mock_config.return_value = {"JWT_SECRET_KEY": TEST_JWT_SECRET}
    mock_adaptateur = Mock(spec=AdaptateurBaseDeDonnees)
    mock_adaptateur.ajoute_retour_utilisatrice.return_value = True

    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock_adaptateur

    try:
        client = TestClient(app)
        payload_jwt = {
            "interaction_id": "test-id-456",
            "exp": datetime.now(UTC) + timedelta(hours=24),
        }
        token = jwt.encode(payload_jwt, TEST_JWT_SECRET, algorithm="HS256")

        payload = {"pouce_leve": False, "commentaire": "Pas très clair"}

        response = client.post(
            "/retour", json=payload, cookies={"interaction_token": token}
        )

        assert response.status_code == 200
        mock_adaptateur.ajoute_retour_utilisatrice.assert_called_once()

    finally:
        app.dependency_overrides.clear()


@patch("main.recupere_configuration")
def test_route_retour_avec_jwt_retourne_retour_utilisatrice_correcte(mock_config):
    mock_config.return_value = {"JWT_SECRET_KEY": TEST_JWT_SECRET}
    mock_adaptateur = Mock(spec=AdaptateurBaseDeDonnees)
    mock_adaptateur.ajoute_retour_utilisatrice.return_value = True

    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock_adaptateur

    try:
        client = TestClient(app)
        payload_jwt = {
            "interaction_id": "test-id-456",
            "exp": datetime.now(UTC) + timedelta(hours=24),
        }
        token = jwt.encode(payload_jwt, TEST_JWT_SECRET, algorithm="HS256")

        payload = {"pouce_leve": False, "commentaire": "Pas très clair"}

        response = client.post(
            "/retour", json=payload, cookies={"interaction_token": token}
        )

        data = response.json()
        assert data["succes"] is True
        assert data["commentaire"] == "Pas très clair"
        mock_adaptateur.ajoute_retour_utilisatrice.assert_called_once()

    finally:
        app.dependency_overrides.clear()


@patch("main.recupere_configuration")
def test_route_retour_interaction_inexistante_retourne_404(mock_config):
    mock_config.return_value = {"JWT_SECRET_KEY": TEST_JWT_SECRET}
    mock_adaptateur = Mock(spec=AdaptateurBaseDeDonnees)
    mock_adaptateur.ajoute_retour_utilisatrice.return_value = False

    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock_adaptateur

    try:
        client = TestClient(app)
        payload_jwt = {
            "interaction_id": "id-inexistant",
            "exp": datetime.now(UTC) + timedelta(hours=24),
        }
        token = jwt.encode(payload_jwt, TEST_JWT_SECRET, algorithm="HS256")

        payload = {"pouce_leve": True, "commentaire": "Test"}

        response = client.post(
            "/retour", json=payload, cookies={"interaction_token": token}
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Interaction non trouvée"

    finally:
        app.dependency_overrides.clear()


def test_route_retour_sans_token_retourne_400():
    mock_adaptateur = Mock(spec=AdaptateurBaseDeDonnees)

    app.dependency_overrides[
        fabrique_adaptateur_base_de_donnees_retour_utilisatrice
    ] = lambda: mock_adaptateur

    try:
        client = TestClient(app)
        payload = {"pouce_leve": True, "commentaire": "Test sans token"}
        response = client.post("/retour", json=payload)
        assert response.status_code == 400
        assert "Token d'interaction manquant" in response.json()["detail"]

    finally:
        app.dependency_overrides.clear()
